#!/usr/bin/env python
# -*- coding: utf-8 -*-
# training_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:06:45 2014 (+0100)
# Last-Updated: Thu Nov 27 00:07:46 2014 (+0100)
#           By: Yann KOETH
#     Update #: 98
#

import os
import sys

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QToolBar, QSizePolicy, QFileDialog,
                             QLineEdit, QScrollArea, QGroupBox, QSpinBox,
                             QComboBox, QSpinBox, QSplitter, QTextEdit,
                             QGridLayout, QApplication)
from PyQt5.QtCore import QRectF, QEvent, Qt, QSize, pyqtSignal, QObject
from PyQt5.QtGui import (QFont, QKeySequence, QIcon, QPixmap, QPainter,
                         QTextCursor)

from dataset import Dataset
from ocr import OCR

class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class TrainingWidgetUI(object):

    def folderWidget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(self.tr("Folder"))
        self.datasetFolder = QLineEdit()
        self.selectFolderButton = QPushButton(self.tr("..."))
        self.selectFolderButton.setMaximumWidth(40)
        layout.addWidget(label)
        layout.addWidget(self.datasetFolder)
        layout.addWidget(self.selectFolderButton)
        widget.setLayout(layout)
        return widget

    def paramWidget(self):
        groupBox = QGroupBox(self.tr("Parameters"))
        layout = QGridLayout()
        self.trainRatio = QSpinBox()
        self.maxPerClass = QSpinBox()
        self.mode = QComboBox()
        layout.addWidget(QLabel(self.tr("Train ratio")), 0, 0)
        layout.addWidget(self.trainRatio, 0, 1)
        layout.addWidget(QLabel(self.tr("Maximum per class")), 1, 0)
        layout.addWidget(self.maxPerClass, 1, 1)
        layout.addWidget(QLabel(self.tr("Mode")), 2, 0)
        layout.addWidget(self.mode, 2, 1)
        groupBox.setLayout(layout)
        return groupBox

    def setupUI(self):
        layout = QVBoxLayout()
        self.outputText = QTextEdit()
        self.trainButton = QPushButton(self.tr("Train"))
        self.trainButton.setMaximumWidth(200)
        self.trainButton.setFont(QFont('Arial', 15, QFont.Bold))
        hbox = QHBoxLayout()
        hbox.addWidget(self.paramWidget())
        hbox.addStretch(1)
        hbox.addWidget(self.trainButton)
        hbox.addStretch(1)
        layout.addLayout(hbox)
        layout.addWidget(self.folderWidget())
        layout.addWidget(self.outputText)
        self.setLayout(layout)

class TrainingWidget(QWidget, TrainingWidgetUI):

    MODE_ANN = "Neural Network"
    MODE_KNEAREST = "K-Nearest"

    __modes = [MODE_ANN, MODE_KNEAREST]

    def __init__(self, classes_tree, parent=None):
        super(TrainingWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self.setupUI()
        self.populateUI()
        self.connectUI()
        self.initUI()
        self._dataset = Dataset(self.datasetFolder.text())
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    def __del__(self):
        sys.stdout = sys.__stdout__

    def populateUI(self):
        for mode in self.__modes:
            self.mode.addItem(mode)

    def connectUI(self):
        self.trainButton.clicked.connect(self.train)
        self.selectFolderButton.clicked.connect(self.selectFolder)

    def initUI(self):
        self.trainRatio.setSuffix(' %')
        self.trainRatio.setRange(0, 100)
        self.maxPerClass.setRange(1, 50000)
        self.maxPerClass.setValue(700)
        self.trainRatio.setValue(50)
        folder = os.path.join(os.path.dirname(__file__), "dataset")
        self.datasetFolder.setText(folder)

    ########################################################
    # Utils

    ########################################################
    # Signals handlers

    def normalOutputWritten(self, text):
        """Append text to debug infos.
        """
        cursor = self.outputText.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.outputText.setTextCursor(cursor)
        QApplication.processEvents()

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.datasetFolder.setText(file)
            self._dataset.setFolder(file)

    def train(self):
        modes = {
            self.MODE_ANN: OCR.MODEL_ANN,
            self.MODE_KNEAREST: OCR.MODEL_KNEAREST
            }
        mode = modes[self.__modes[self.mode.currentIndex()]]
        classes = self._classes_tree.getClasses()
        ocr = OCR()
        ocr.trainModel(self._dataset, classes, mode, self.trainRatio.value(),
                       self.maxPerClass.value())
        ocr.saveModel()
