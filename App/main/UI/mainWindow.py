# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitled.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QComboBox, QGraphicsView,
    QGridLayout, QGroupBox, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_Delete = QPushButton(self.centralwidget)
        self.pushButton_Delete.setObjectName(u"pushButton_Delete")
        self.pushButton_Delete.setCheckable(False)

        self.gridLayout_2.addWidget(self.pushButton_Delete, 1, 4, 1, 1)

        self.pushButton_Save = QPushButton(self.centralwidget)
        self.pushButton_Save.setObjectName(u"pushButton_Save")

        self.gridLayout_2.addWidget(self.pushButton_Save, 1, 3, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.listWidget_Frames = QListWidget(self.groupBox)
        self.listWidget_Frames.setObjectName(u"listWidget_Frames")
        self.listWidget_Frames.setMaximumSize(QSize(151, 16777215))
        self.listWidget_Frames.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.gridLayout.addWidget(self.listWidget_Frames, 1, 0, 3, 1)

        self.listWidget_AddedClasses = QListWidget(self.groupBox)
        self.listWidget_AddedClasses.setObjectName(u"listWidget_AddedClasses")
        self.listWidget_AddedClasses.setMaximumSize(QSize(151, 16777215))

        self.gridLayout.addWidget(self.listWidget_AddedClasses, 2, 2, 1, 2)

        self.spinBox_TrackId = QSpinBox(self.groupBox)
        self.spinBox_TrackId.setObjectName(u"spinBox_TrackId")
        font = QFont()
        font.setPointSize(16)
        self.spinBox_TrackId.setFont(font)

        self.gridLayout.addWidget(self.spinBox_TrackId, 3, 2, 1, 1)

        self.graphicsView = QGraphicsView(self.groupBox)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setAcceptDrops(False)
        self.graphicsView.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.gridLayout.addWidget(self.graphicsView, 0, 1, 4, 1)

        self.comboBox_Classes = QComboBox(self.groupBox)
        self.comboBox_Classes.setObjectName(u"comboBox_Classes")

        self.gridLayout.addWidget(self.comboBox_Classes, 1, 2, 1, 2)

        self.pushButton_AddClass = QPushButton(self.groupBox)
        self.pushButton_AddClass.setObjectName(u"pushButton_AddClass")

        self.gridLayout.addWidget(self.pushButton_AddClass, 0, 2, 1, 2)

        self.pushButton_AddFrame = QPushButton(self.groupBox)
        self.pushButton_AddFrame.setObjectName(u"pushButton_AddFrame")
        self.pushButton_AddFrame.setMaximumSize(QSize(151, 16777215))

        self.gridLayout.addWidget(self.pushButton_AddFrame, 0, 0, 1, 1)

        self.pushButton_AddTrackId = QPushButton(self.groupBox)
        self.pushButton_AddTrackId.setObjectName(u"pushButton_AddTrackId")
        self.pushButton_AddTrackId.setFont(font)

        self.gridLayout.addWidget(self.pushButton_AddTrackId, 3, 3, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 5)

        self.pushButton_Fill = QPushButton(self.centralwidget)
        self.pushButton_Fill.setObjectName(u"pushButton_Fill")

        self.gridLayout_2.addWidget(self.pushButton_Fill, 1, 1, 1, 1)

        self.lineEdit_SingleTrackId = QLineEdit(self.centralwidget)
        self.lineEdit_SingleTrackId.setObjectName(u"lineEdit_SingleTrackId")
        self.lineEdit_SingleTrackId.setMaximumSize(QSize(133, 16777215))

        self.gridLayout_2.addWidget(self.lineEdit_SingleTrackId, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.groupBox.raise_()
        self.pushButton_Delete.raise_()
        self.pushButton_Save.raise_()
        self.pushButton_Fill.raise_()
        self.lineEdit_SingleTrackId.raise_()
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_Delete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.pushButton_Save.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Easier Image Annotator", None))
        self.pushButton_AddClass.setText(QCoreApplication.translate("MainWindow", u"Add Class", None))
#if QT_CONFIG(tooltip)
        self.pushButton_AddFrame.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select the folder of your frames</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.pushButton_AddFrame.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButton_AddFrame.setText(QCoreApplication.translate("MainWindow", u"Add Frame", None))
        self.pushButton_AddTrackId.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.pushButton_Fill.setText(QCoreApplication.translate("MainWindow", u"Fill", None))
    # retranslateUi

