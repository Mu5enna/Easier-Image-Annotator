import math
import os
import sys
from pathlib import Path

from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw

from App.main.UI.mainWindow import Ui_MainWindow
from classes.BoundingBox import BoundingBox

#----------------------------------------------------------------------------------------------------------------------#
imagePaths={}

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
        self.selected_item = None

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
        resizeOrMove = False
        if isinstance(item, ResizableRectItem) and item.isSelected():
            resizeOrMove = True
        # Yeni çizim başlatma
        if not resizeOrMove:
            self.start_pos = self.mapToScene(event.pos())
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
        item = self.itemAt(event.pos())
        if isinstance(item, ResizableRectItem):
            # Dikdörtgen seçimi
            for rect_item in self.scene.items():
                if isinstance(rect_item, ResizableRectItem):
                    rect_item.setSelected(False)  # Herkesi deseç
            item.setSelected(True)  # Teknik olarak sadece bir item seçili olacak
        if self.current_rect:
            # Yeni dikdörtgen çizimi tamamlandı
            self.current_rect = None
            self.start_pos = None
            BoundingBox.add(item.rect().x(), item.rect().y(), item.rect().x()+item.rect().width(), item.rect().y()+item.rect().height(),0,0)
            print(BoundingBox.BoundingBoxes)
        super().mouseReleaseEvent(event)

# TODO print yerine statusbarda yazsın

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Qt Designer'daki QGraphicsView'i özelleştirilmiş sınıfa dönüştürüyoruz
        self.ui.graphicsView = ImageAnnotationView(self.ui.graphicsView)

        # Add frames and switch frames when a list item is clicked
        self.ui.pushButton_AddFrame.clicked.connect(self.fileDialog)
        self.ui.listWidget_Frames.currentRowChanged.connect(self.loadImage)

        self.ui.graphicsView.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        self.ui.graphicsView.setRenderHint(qtg.QPainter.Antialiasing)
        self.ui.graphicsView.fitInView(self.ui.graphicsView.sceneRect(), qtc.Qt.KeepAspectRatio)



    @qtc.Slot()
    def fileDialog(self):
        folder = qtw.QFileDialog.getExistingDirectory(self, 'Select Folder', str(Path.home() / "Desktop"))
        if folder:
            imagePaths.clear()
            for filename in os.listdir(folder):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    full_path = os.path.join(folder, filename)
                    imagePaths[filename] = full_path
            self.ui.listWidget_Frames.clear()
            for key in imagePaths.keys():
                self.ui.listWidget_Frames.addItem(key)
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
