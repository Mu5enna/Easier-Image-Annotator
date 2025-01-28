import math
import os
import sys
import json
from pathlib import Path

from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw
from PySide6.QtCore import Qt

from App.main.UI.mainWindow import Ui_MainWindow

#----------------------------------------------------------------------------------------------------------------------#
imagePaths={}
json_path = ""
selected_addclass_text = ""
selected_addclass_id = 0

class Item:
    def __init__(self, text, id):
        self.text = text
        self.id = id

    def stringify(self):
        return self.text


class ResizableRectItem(qtw.QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlags(
            qtw.QGraphicsItem.ItemIsMovable |
            qtw.QGraphicsItem.ItemIsSelectable |
            qtw.QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setPen(qtg.QPen(qtg.Qt.red, 3))
        self.setBrush(qtg.QBrush(qtg.Qt.transparent))

        self.is_resizing = False  # Boyutlandırma modunu takip et
        self.resize_dir = None  # Hangi kenarın sürüklendiğini belirle

    def hoverMoveEvent(self, event):
        cursor = qtg.Qt.ArrowCursor
        rect = self.rect()
        pos = event.pos()

        buffer = 10  # Kenar veya köşe algılama mesafesi
        left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()

        if not self.isSelected():
            cursor = qtg.Qt.ArrowCursor
            self.setCursor(cursor)
            return
        # Öncelik köşe algılamasında
        if abs(pos.x() - left) < buffer and abs(pos.y() - top) < buffer:
            cursor = qtg.Qt.SizeFDiagCursor  # Sol üst köşe
            self.resize_dir = "top_left"
        elif abs(pos.x() - right) < buffer and abs(pos.y() - top) < buffer:
            cursor = qtg.Qt.SizeBDiagCursor  # Sağ üst köşe
            self.resize_dir = "top_right"
        elif abs(pos.x() - left) < buffer and abs(pos.y() - bottom) < buffer:
            cursor = qtg.Qt.SizeBDiagCursor  # Sol alt köşe
            self.resize_dir = "bottom_left"
        elif abs(pos.x() - right) < buffer and abs(pos.y() - bottom) < buffer:
            cursor = qtg.Qt.SizeFDiagCursor  # Sağ alt köşe
            self.resize_dir = "bottom_right"
        elif abs(pos.x() - left) < buffer:
            cursor = qtg.Qt.SizeHorCursor  # Sol kenar
            self.resize_dir = "left"
        elif abs(pos.x() - right) < buffer:
            cursor = qtg.Qt.SizeHorCursor  # Sağ kenar
            self.resize_dir = "right"
        elif abs(pos.y() - top) < buffer:
            cursor = qtg.Qt.SizeVerCursor  # Üst kenar
            self.resize_dir = "top"
        elif abs(pos.y() - bottom) < buffer:
            cursor = qtg.Qt.SizeVerCursor  # Alt kenar
            self.resize_dir = "bottom"
        elif rect.contains(pos):
            cursor = qtg.Qt.SizeAllCursor  # İçeride hareket ikonu
            self.resize_dir = None
        else:
            self.resize_dir = None

        self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        self.start_pos = event.pos()  # Başlangıç pozisyonunu kaydet
        # Eğer bir kenar algılandıysa boyutlandırma başlat
        if self.isSelected():  # Sadece seçili öğelerde işlem yapılır
            if self.resize_dir:
                self.is_resizing = True
                self.original_rect = self.rect()
            else:
                self.is_resizing = False
        # Seçim işlemini engellemek için varsayılan davranışı iptal edelim
        event.accept()

    def mouseMoveEvent(self, event):
        if self.isSelected() and self.is_resizing and self.resize_dir:  # Seçili öğeye göre kontrol
            delta = event.scenePos() - event.lastScenePos()
            rect = self.rect()

            if self.resize_dir == "left":
                rect.setLeft(rect.left() + delta.x())
            elif self.resize_dir == "right":
                rect.setRight(rect.right() + delta.x())
            elif self.resize_dir == "top":
                rect.setTop(rect.top() + delta.y())
            elif self.resize_dir == "bottom":
                rect.setBottom(rect.bottom() + delta.y())
            elif self.resize_dir == "top_left":
                rect.setLeft(rect.left() + delta.x())
                rect.setTop(rect.top() + delta.y())
            elif self.resize_dir == "top_right":
                rect.setRight(rect.right() + delta.x())
                rect.setTop(rect.top() + delta.y())
            elif self.resize_dir == "bottom_left":
                rect.setLeft(rect.left() + delta.x())
                rect.setBottom(rect.bottom() + delta.y())
            elif self.resize_dir == "bottom_right":
                rect.setRight(rect.right() + delta.x())
                rect.setBottom(rect.bottom() + delta.y())

            self.setRect(rect)
        elif self.isSelected():  # Seçiliyse hareket ettir
            super().mouseMoveEvent(event)  # Hareket ettirmek için QGraphicsItem default davranış çalışır
        else:
            return  # Seçili değilse hiçbir işlem yapılmasın

    def mouseReleaseEvent(self, event):
        # İşlem bittikten sonra boyutlandırma durdurulmalı
        if self.isSelected():
            self.is_resizing = False
        # Seçim işlemini burada gerçekleştirelim
        if self.resize_dir is None:
            self.setSelected(True)
        super().mouseReleaseEvent(event)



class ImageAnnotationView(qtw.QGraphicsView):
    """Ana çizim sahnesi için özel bir QGraphicsView"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = qtw.QGraphicsScene(self)
        self.setScene(self.scene)
        self.dragStartPosition = qtc.QPointF()
        self.isDragging = False
        self.start_pos = None

        # Dikdörtgen çizimi için başlangıç değişkenleri
        self.start_pos = None
        self.current_rect = None

    def load_image(self, image_path):
        """Arka plan olarak bir resmi yükler"""
        pixmap = qtg.QPixmap(image_path)
        self.scene.clear()
        self.scene.addPixmap(pixmap)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if not isinstance(item, ResizableRectItem): # TODO şunu click drag farkına çevirince olcak glb
            # Yeni çizim başlatma
            self.start_pos = self.mapToScene(event.pos())
            self.current_rect = ResizableRectItem(qtc.QRectF(self.start_pos, self.start_pos))
            self.scene.addItem(self.current_rect)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            # Başlangıç pozisyonu ile mevcut pozisyon arasındaki mesafeyi hesapla
            dx = event.position().x() - self.start_pos.x()
            dy = event.position().y() - self.start_pos.y()
            distance = math.sqrt(dx ** 2 + dy ** 2)  # Öklid mesafesi
            if distance > 5:  # Belirli bir eşik değeri (ör. 5 piksel)
                # Eğer yeni bir dikdörtgen çiziliyorsa
                if self.start_pos and self.current_rect:
                    end_pos = self.mapToScene(event.pos())
                    rect = qtc.QRectF(self.start_pos, end_pos).normalized()
                    self.current_rect.setRect(rect)
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, ResizableRectItem):
            # Dikdörtgen seçimi
            for rect_item in self.scene.items():
                if isinstance(rect_item, ResizableRectItem):
                    rect_item.setSelected(False)  # Herkesi deseç
            item.setSelected(True)  # Teknik olarak sadece bir item seçili olacak
        if self.current_rect:
            # Yeni dikdörtgen çizimi tamamlandı
            print(f"Dikdörtgen eklendi: {self.current_rect.rect()}")
            self.current_rect = None
            self.start_pos = None
        super().mouseReleaseEvent(event)


# TODO print yerine statusbarda yazsın

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        path: str = r"C:\Users\Eren\Desktop\ids.txt"
        self.load_ids(self, path)


        # Qt Designer'daki QGraphicsView'i özelleştirilmiş sınıfa dönüştürüyoruz
        self.ui.graphicsView = ImageAnnotationView(self.ui.graphicsView)

        # Add frames and switch frames when a list item is clicked
        self.ui.pushButton_AddFrame.clicked.connect(self.fileDialog)
        self.ui.listWidget_Frames.currentRowChanged.connect(self.loadImage)

        self.ui.graphicsView.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.ui.graphicsView.setRenderHint(qtg.QPainter.Antialiasing)
        self.ui.graphicsView.fitInView(self.ui.graphicsView.sceneRect(), qtc.Qt.KeepAspectRatio)
        self.ui.comboBox_Classes.currentIndexChanged.connect(self.combo_classes)
        self.ui.pushButton_AddClass.clicked.connect(self.add_class)
        self.ui.listWidget_AddedClasses.itemChanged.connect(self.class_selected)


    def class_selected(self, changed_item):
        if changed_item.checkState() == Qt.CheckState.Checked:
            for i in range(self.ui.listWidget_AddedClasses.count()):
                item = self.ui.listWidget_AddedClasses.item(i)
                if item != changed_item:
                    item.setCheckState(Qt.CheckState.Unchecked)

    qtc.Slot()
    def add_class(self):
        item = qtw.QListWidgetItem(selected_addclass_text)
        item.setData(qtc.Qt.ItemDataRole.UserRole, selected_addclass_id)
        item.setFlags(item.flags() | qtc.Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(qtc.Qt.CheckState.Unchecked)
        display_str = selected_addclass_text + " (" + str(item.data(qtc.Qt.ItemDataRole.UserRole)) + ")"
        item.setText(display_str)
        self.ui.listWidget_AddedClasses.addItem(item)
        self.upd_cur_class_file(self, selected_addclass_text, selected_addclass_id, False)

    @staticmethod
    def upd_cur_class_file(self, text: str, cid: int, is_delete: bool):
        global json_path
        file_path = json_path + "/classes.txt"
        if not is_delete:
            with open(file_path, "a") as f:
                file_input = text + " , " + str(cid) + "\n"
                f.write(file_input)
        else:
            pass ## deleting code

    @staticmethod
    def load_ids(self, file_path: str):
        with open(file_path, "r") as f:
            f.readline()
            for line in f:
                if line.strip() != "":
                    values = [value.strip() for value in line.strip().split(',')]
                    text, cid = values
                    item = Item(text, cid)
                    self.ui.comboBox_Classes.addItem(item.text, item.id)

    @staticmethod
    def load_class_file(self):
        with open(json_path + "/classes.txt", "r") as f:
            for line in f:
                if line.strip() != "":
                    values = [value.strip() for value in line.strip().split(',')]
                    text, cid = values
                    item = qtw.QListWidgetItem(text)
                    item.setData(qtc.Qt.ItemDataRole.UserRole, cid)
                    item.setFlags(item.flags() | qtc.Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(qtc.Qt.CheckState.Unchecked)
                    display_str = text + " (" + str(item.data(qtc.Qt.ItemDataRole.UserRole)) + ")"
                    item.setText(display_str)
                    self.ui.listWidget_AddedClasses.addItem(item)



    @qtc.Slot()
    def combo_classes(self):
        index = self.ui.comboBox_Classes.currentIndex()
        if index >= 0:
            global selected_addclass_text
            global selected_addclass_id
            selected_addclass_text = self.ui.comboBox_Classes.currentText()
            selected_addclass_id = self.ui.comboBox_Classes.currentData()

    @qtc.Slot()
    def fileDialog(self):
        create_json = False
        folder = qtw.QFileDialog.getExistingDirectory(self, 'Select Folder', str(Path.home() / "Desktop"))
        global json_path
        json_path = folder + "_json"
        try:
            os.mkdir(json_path)
            create_json = True
            ## create new class file
            open(json_path + "/classes.txt", "x")

        except FileExistsError:
            msg_box = qtw.QMessageBox()
            msg_box.setIcon(qtw.QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Existent File")
            folder_icon = qtw.QApplication.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
            msg_box.setWindowIcon(folder_icon)
            msg_box.setText(f"File '{json_path}' already exists")
            msg_box.exec_()
            self.load_class_file(self)
        except Exception as e:
            msg_box = qtw.QMessageBox()
            msg_box.setIcon(qtw.QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Error")
            error_icon = qtw.QApplication.style().standardIcon(qtw.QStyle.SP_MessageBoxCritical)
            msg_box.setWindowIcon(error_icon)
            qtw.QMessageBox.text(f"Error occured: {e}")
            msg_box.exec_()

        if folder:
            imagePaths.clear()
            for filename in os.listdir(folder):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    full_path = os.path.join(folder, filename)
                    imagePaths[filename] = full_path
            self.ui.listWidget_Frames.clear()
            for key, value in imagePaths.items():
                self.ui.listWidget_Frames.addItem(key)
                if create_json:
                    with open(json_path + "/" + os.path.splitext(os.path.basename(str(key)))[0] + ".json", "w") as f:
                        def_json_struct = "{\n}"
                        f.write(def_json_struct)

            self.ui.listWidget_Frames.setCurrentRow(0)


    @qtc.Slot()
    def loadImage(self):
        self.ui.graphicsView.load_image(imagePaths[self.ui.listWidget_Frames.currentItem().text()])
        self.ui.graphicsView.show()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    sys.exit(app.exec())
