import os
import sys
from pathlib import Path

from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw
from PySide6.QtCore import Qt

from App.main.UI.mainWindow import Ui_MainWindow
from classes.BoundingBox import BoundingBox
from classes.calculations import JsonData, Calculations

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
    def __init__(self, rect, bounding_box_id=None, parent=None):
        super().__init__(rect, parent)
        self.bounding_box_id = bounding_box_id  # Bu dikdörtgenin BoundingBox id'si
        self.setFlags(
            qtw.QGraphicsItem.ItemIsMovable |
            qtw.QGraphicsItem.ItemIsSelectable |
            qtw.QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setPen(qtg.QPen(qtg.Qt.red, 3))
        self.setBrush(qtg.QBrush(qtg.Qt.transparent))
        self.is_resizing = False
        self.resize_dir = None

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

            if rect.width() < 5 or rect.height() < 5:
                return

            # Güncellenmiş dikdörtgeni ayarla
            self.setRect(rect.normalized())
        elif self.isSelected():  # Seçiliyse hareket ettir
            super().mouseMoveEvent(event)  # Hareket ettirmek için QGraphicsItem default davranış çalışır
        else:
            return  # Seçili değilse hiçbir işlem yapılmasın

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()  # Tıklama bitiş pozisyonunu kaydet
        # İşlem bittikten sonra boyutlandırma durdurulmalı
        if self.isSelected():
            self.is_resizing = False
        # Eğer bu öğe bir BoundingBox ile ilişkilendirilmişse, güncelle
        if self.bounding_box_id is not None:
            print(f"Updating BoundingBox with id: {self.bounding_box_id}")
            rect = self.rect().normalized()  # Geçerli dikdörtgen sınırlarını al
            BoundingBox.update(
                self.bounding_box_id,
                x1=self.mapToScene(rect.topLeft()).x(),
                y1=self.mapToScene(rect.topLeft()).y(),
                x2=self.mapToScene(rect.bottomRight()).x(),
                y2=self.mapToScene(rect.bottomRight()).y()
            )
            print("Updated BoundingBox:", BoundingBox.BoundingBoxes[self.bounding_box_id])
            print(BoundingBox.BoundingBoxes)
            main_window = qtw.QApplication.instance().activeWindow()  # Açık olan ana pencereyi al
            MainWindow.loadTrackId(main_window)
            MainWindow.load
        else:
            print(f"selected box no: {self.bounding_box_id}")

        # Eğer yeniden boyutlandırma yapılmadıysa seçim durumu yönetimi
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
        self.selected_item = None
        self.selected_bounding_box_id = -1
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.setSceneRect(self.scene.itemsBoundingRect())
        

        # Dikdörtgen çizimi için başlangıç değişkenleri
        self.current_rect = None

    def load_image(self, image_path):
        """Arka plan olarak bir resmi yükler"""
        pixmap = qtg.QPixmap(image_path)
        self.scene.clear()
        self.scene.addPixmap(pixmap)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        resizeOrMove = False
        if isinstance(item, ResizableRectItem) and item.isSelected():
            resizeOrMove = True
        # Yeni çizim başlatma
        if not resizeOrMove:
            self.start_pos = self.mapToScene(event.pos())
            print(f"Start position: {self.start_pos}")
            self.current_rect = ResizableRectItem(qtc.QRectF(self.start_pos, self.start_pos))
            self.scene.addItem(self.current_rect)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selected_item:  # Seçiliyse hareket ettir
            delta = event.scenePos() - event.lastScenePos()
            self.selected_item.moveBy(delta.x(), delta.y())
        elif self.start_pos:  # Başlangıç noktası bir dikdörtgeni çizer
            end_pos = self.mapToScene(event.pos())
            rect = qtc.QRectF(self.start_pos, end_pos).normalized()
            self.current_rect.setRect(rect)

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        # Tıklanan öğeyi al
        item = self.itemAt(event.pos())

        # Mevcut bir dikdörtgen seçildiyse
        if isinstance(item, ResizableRectItem):
            # Diğer tüm dikdörtgenleri deseç
            for rect_item in self.scene.items():
                if isinstance(rect_item, ResizableRectItem):
                    rect_item.setSelected(False)
            # Seçilen dikdörtgeni aktif yap
            item.setSelected(True)
            self.selected_bounding_box_id = item.bounding_box_id

        # Yeni bir dikdörtgen oluşturuluyorsa
        if self.current_rect:
            notDrawn = False
            # Dikdörtgenin koordinatlarını al
            rect = self.current_rect.rect()
            if rect.width()<5 or rect.height()<5:
                notDrawn = True
            if not notDrawn:
                # BoundingBox nesnesine ekle
                bounding_box = BoundingBox.add(
                    rect.left(), rect.top(), rect.right(), rect.bottom(), classId=0, trackId=0
                )
                # Dikdörtgenin BoundingBox kimliğini ilişkilendir
                self.current_rect.bounding_box_id = bounding_box._id
                self.selected_bounding_box_id = bounding_box._id

                print(f"New BoundingBox added: {bounding_box}")
                print(f"BoundingBox ID assigned to ResizableRectItem: {self.current_rect.bounding_box_id}\n")

                # Yeni dikdörtgenin çizimini tamamla
            self.current_rect = None
            self.start_pos = None

        super().mouseReleaseEvent(event)

    def get_selected_bounding_box(self):
        """Seçili dikdörtgenin BoundingBox ID'sini döndürür"""
        if self.selected_bounding_box_id >= 0:
            ret:int = self.selected_bounding_box_id
            return ret
        else:
            return -1


# TODO print yerine statusbarda yazsın

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        path: str = r"C:\Users\Serhat\Desktop\ids.txt"
        self.load_ids(self, path)

        # Grafik ayarları
        self.ui.graphicsView.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.ui.graphicsView.setFrameShape(qtw.QFrame.NoFrame)  # Kenar boşluklarını kaldırır
        self.ui.graphicsView.fitInView(self.ui.graphicsView.sceneRect(), qtc.Qt.KeepAspectRatio)

        # Qt Designer'daki QGraphicsView'i özelleştirilmiş sınıfa dönüştürüyoruz
        self.ui.graphicsView = ImageAnnotationView(self.ui.graphicsView)

        # Add frames and switch frames when a list item is clicked
        self.ui.pushButton_AddFrame.clicked.connect(self.fileDialog)
        self.ui.listWidget_Frames.currentRowChanged.connect(self.loadImage)

        self.ui.comboBox_Classes.currentIndexChanged.connect(self.combo_classes)
        self.ui.pushButton_AddClass.clicked.connect(self.add_class)
        self.ui.listWidget_AddedClasses.itemChanged.connect(self.class_selected)
        self.ui.pushButton_Save.clicked.connect(self.save_to_file)
        self.ui.pushButton_AddTrackId.clicked.connect(self.assign_track_id)

        """Context menu for frames"""
        self.context_menu = qtw.QMenu(self)
        self.action_FirstFrame = self.context_menu.addAction("First Frame")
        self.action_FirstFrame.triggered.connect(self.firstFrame)
        self.action_LastFrame = self.context_menu.addAction("Last Frame")
        self.action_LastFrame.triggered.connect(self.lastFrame)
        self.action_FillInBetween = self.context_menu.addAction("Fill in Between")
        self.action_FillInBetween.triggered.connect(self.fillInBetween)
        self.action_FillInBetweenFor = self.context_menu.addAction("Fill in Between For:")
        self.action_FillInBetweenFor.triggered.connect(self.fillInBetweenFor)

        self.context_menu2 = qtw.QMenu(self)
        self.action_DeleteClass = self.context_menu2.addAction("Delete Class")
        self.action_DeleteClass.triggered.connect(self.delete_class)

        self.ui.listWidget_Frames.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.listWidget_AddedClasses.customContextMenuRequested.connect(self.show_context_menu2)

        self.ui.pushButton_Delete.clicked.connect(self.deleteBox)


    @qtc.Slot()
    def deleteBox(self): #todo silince en büyük+1 den başlasın
        selected_box_id = self.getSelectedBoxId()
        if selected_box_id >= 0:
            print(f"Deleting BoundingBox with id: {selected_box_id}")

            # Delete the BoundingBox from the BoundingBox class
            BoundingBox.delete(selected_box_id)
            # Remove the corresponding ResizableRectItem from the scene
            for item in self.ui.graphicsView.scene.items():
                if isinstance(item, ResizableRectItem) and item.bounding_box_id == selected_box_id:
                    self.ui.graphicsView.scene.removeItem(item)
                    break
            self.ui.graphicsView.scene.removeItem(self.ui.graphicsView.scene.items()[selected_box_id])
            print(f"BoundingBox List: {BoundingBox.BoundingBoxes}")
            print(f"GraphicsView Scene: {self.ui.graphicsView.scene.items()}")


    @qtc.Slot()
    def getSelectedBoxId(self):
        selected_box_id = self.ui.graphicsView.get_selected_bounding_box()
        if selected_box_id >= 0:
            print(f"Selected BoundingBox ID: {selected_box_id}")
            ret:int = selected_box_id
            return ret
        else:
            print("No BoundingBox is selected.")
            return -1

    @staticmethod
    def loadTrackId(self):
        selected_box_id = self.getSelectedBoxId()
        if selected_box_id >= 0:
            track_id:int = BoundingBox.BoundingBoxes[selected_box_id].trackId
            self.ui.spinBox_TrackId.setValue(track_id)
            print(f"Track ID assigned to BoundingBox with id: {selected_box_id}")

    @staticmethod
    def loadClass(self):
        pass

    def show_context_menu(self, pos):
        # Sağ tık menüsünü, QListWidget üzerinde sağ tıklanan öğe ile konumlandır
        selected_item = self.ui.listWidget_Frames.itemAt(pos)  # Tıklanan öğe
        if selected_item:
            self.context_menu.exec(self.ui.listWidget_Frames.mapToGlobal(pos))

    def show_context_menu2(self, pos):
        selected_item2 = self.ui.listWidget_AddedClasses.itemAt(pos)
        if selected_item2:
            self.context_menu2.exec(self.ui.listWidget_AddedClasses.mapToGlobal(pos))

    def class_selected(self, changed_item):
        if changed_item.checkState() == Qt.CheckState.Checked:
            for i in range(self.ui.listWidget_AddedClasses.count()):
                item = self.ui.listWidget_AddedClasses.item(i)
                if item != changed_item:
                    item.setCheckState(Qt.CheckState.Unchecked)

    def assign_track_id(self):
        selected_box_id = self.getSelectedBoxId()
        if selected_box_id >= 0:
            track_id:int = self.ui.spinBox_TrackId.value()
            BoundingBox.BoundingBoxes[selected_box_id].trackId = track_id
            print(f"Track ID assigned to BoundingBox with id: {selected_box_id}")
            print(f"BoundingBox List: {BoundingBox.BoundingBoxes}")



# TODO duplicate olanları ekleme
    @qtc.Slot()
    def add_class(self):
        does_contain = False
        for data in self.ui.listWidget_AddedClasses.items(): #todo burada hata var
            if selected_addclass_id == data:
                does_contain = True
        if not does_contain:
            item = qtw.QListWidgetItem(selected_addclass_text)
            item.setData(qtc.Qt.ItemDataRole.UserRole, selected_addclass_id)
            item.setFlags(item.flags() | qtc.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(qtc.Qt.CheckState.Unchecked)
            display_str = selected_addclass_text + " (" + str(item.data(qtc.Qt.ItemDataRole.UserRole)) + ")"
            item.setText(display_str)
            self.ui.listWidget_AddedClasses.addItem(item)
            self.upd_cur_class_file(selected_addclass_text, selected_addclass_id, False)
        else:
            self.message_box(qtw.QMessageBox.Icon.Information, "Existent Class", qtw.QApplication.style().standardIcon(qtw.QStyle.SP_MessageBoxInformation), "This class has already added")

    @qtc.Slot()
    def delete_class(self):
        cid = self.ui.listWidget_AddedClasses.currentItem().data(qtc.Qt.ItemDataRole.UserRole)
        deleted = self.ui.listWidget_AddedClasses.takeItem(self.ui.listWidget_AddedClasses.currentRow())
        del deleted
        self.upd_cur_class_file("non", int(cid), True)

    @qtc.Slot()
    def save_to_file(self):
        image_file_path = json_path + "/" + os.path.splitext(os.path.basename(self.ui.listWidget_Frames.currentItem().text()))[0] + ".json"
        json_object = {}
        box_id = 0
        for box in BoundingBox.BoundingBoxes.values():
            box_values = [box.x1, box.y1, box.x2, box.y2]
            json_object[box_id] = {
                'box': box_values,
                'class': box.classId,
                'track_id': box.trackId
            }
            box_id += 1

        JsonData.json_dump(image_file_path, json_object)

    @qtc.Slot()
    def load_from_file(self):
        image_file_path = json_path + "/" + os.path.splitext(os.path.basename(self.ui.listWidget_Frames.currentItem().text()))[0] + ".json"
        json_object = JsonData.json_load(image_file_path)
        for key, entry in json_object.items():
            BoundingBox.add(entry.box[0], entry.box[1], entry.box[2], entry.box[3], entry.class_id, entry.track_id )
            rect = qtc.QRect(entry.box[0], entry.box[1], (entry.box[2] - entry.box[0]), (entry.box[3] - entry.box[1]))
            rect_item = ResizableRectItem(rect)
            rect_item.bounding_box_id = int(key)
            self.ui.graphicsView.scene.addItem(rect_item)


    @staticmethod
    def upd_cur_class_file(text: str, cid: int, is_delete: bool):
        global json_path
        file_path = json_path + "/classes.txt"
        if not is_delete:
            with open(file_path, "a") as f:
                file_input = text + " , " + str(cid) + "\n"
                f.write(file_input)
        else:
            with open(file_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() != "":
                        values = [value.strip() for value in line.strip().split(',')]
                        ftext, fcid = values
                        if int(fcid) == cid:
                            lines.remove(line)
                            break
            with open(file_path, "w") as f:
                f.writelines(lines)


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
    def show_context_menu(self, pos):
        # Sağ tık menüsünü, QListWidget üzerinde sağ tıklanan öğe ile konumlandır
        selected_item = self.ui.listWidget_Frames.itemAt(pos)  # Tıklanan öğe
        if selected_item:
            self.context_menu.exec_(self.ui.listWidget_Frames.mapToGlobal(pos))

    @qtc.Slot()
    def firstFrame(self):
        print("first")

    @qtc.Slot()
    def lastFrame(self):
        print("last")

    @qtc.Slot()
    def fillInBetween(self):
        print("fill")

    @qtc.Slot()
    def fillInBetweenFor(self):
        print("fill for")

    @qtc.Slot()
    def combo_classes(self):
        index = self.ui.comboBox_Classes.currentIndex()
        if index >= 0:
            global selected_addclass_text
            global selected_addclass_id
            selected_addclass_text = self.ui.comboBox_Classes.currentText()
            selected_addclass_id = self.ui.comboBox_Classes.currentData()

    @staticmethod
    def message_box(icon: qtw.QMessageBox.Icon, window_title: str, bar_icon, text: str):
        msg_box = qtw.QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(window_title)
        msg_box.setWindowIcon(bar_icon)
        msg_box.setText(text)
        msg_box.exec()

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
            text = f"File '{json_path}' already exists"
            MainWindow.message_box(qtw.QMessageBox.Icon.Information, "Existent File", qtw.QApplication.style().standardIcon(qtw.QStyle.SP_DirOpenIcon), text)
            self.load_class_file(self)
        except Exception as e:
            text = f"Error occurred: {e}"
            MainWindow.message_box(qtw.QMessageBox.Icon.Information, "Error", qtw.QApplication.style().standardIcon(qtw.QStyle.SP_MessageBoxCritical), text)

        if folder:
            global imagePaths
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
        BoundingBox.reset()
        self.ui.graphicsView.scene.clear()
        self.ui.graphicsView.load_image(imagePaths[self.ui.listWidget_Frames.currentItem().text()])
        self.ui.graphicsView.show()
        self.load_from_file()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.showMaximized()
    sys.exit(app.exec())
