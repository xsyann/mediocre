#!/usr/bin/env python
# -*- coding: utf-8 -*-
# recognition.py
#
# Author: Yann KOETH
# Created: Thu Nov 27 03:53:17 2014 (+0100)
# Last-Updated: Thu Nov 27 05:23:26 2014 (+0100)
#           By: Yann KOETH
#     Update #: 74
#

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QComboBox,
                             QLabel, QHBoxLayout, QLineEdit)
from PyQt5.QtGui import QPixmap, QPainter, QFont

from mediocre.paint_area import PaintArea
from mediocre.ocr import OCR

class RecognitionWidgetUI(object):

    def folderWidget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.modelsFolder = QLineEdit()
        self.selectFolderButton = QPushButton(self.tr("..."))
        self.selectFolderButton.setMaximumWidth(40)
        layout.addWidget(QLabel(self.tr("Models Folder")))
        layout.addWidget(self.modelsFolder)
        layout.addWidget(self.selectFolderButton)
        widget.setLayout(layout)
        return widget

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea()
        self.runButton = QPushButton(self.tr("Run"))
        self.runButton.setFont(QFont('Arial', 15, QFont.Bold))
        self.mode = QComboBox()
        self.resultText = QLabel(self.tr("Result:"))
        layout.addWidget(self.paintArea)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(self.tr("Mode")))
        hbox.addWidget(self.mode)
        hbox.addStretch(1)
        hbox.addWidget(self.runButton)
        hbox.addStretch(1)
        layout.addLayout(hbox)
        layout.addWidget(self.folderWidget())
        layout.addWidget(self.resultText)
        self.setLayout(layout)


class RecognitionWidget(QWidget, RecognitionWidgetUI):
    MODE_ANN = "Neural Network"
    MODE_KNEAREST = "K-Nearest"
    __modes = [MODE_ANN, MODE_KNEAREST]

    def __init__(self, classes_tree, parent=None):
        super(RecognitionWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self.setupUI()
        self.populateUI()
        self.connectUI()
        self.initUI()
        self.ocr = OCR()

    def connectUI(self):
        self.runButton.clicked.connect(self.run)
        self.selectFolderButton.clicked.connect(self.selectFolder)

    def populateUI(self):
        for mode in self.__modes:
            self.mode.addItem(mode)

    def initUI(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        folder = os.path.join(root, "models")
        self.modelsFolder.setText(folder)

    def run(self):
        modes = {
            self.MODE_ANN: OCR.MODEL_ANN,
            self.MODE_KNEAREST: OCR.MODEL_KNEAREST
        }
        mode = modes[self.__modes[self.mode.currentIndex()]]
        folder = self.modelsFolder.text()
        self.ocr.loadModel(self._classes_tree.getClasses(), folder, mode)
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintArea.render(painter)
        painter.end()
        self.resultText.setText(self.tr("Result: ") + self.ocr.charFromImage(pixmap))

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.modelsFolder.setText(file)


__all__ = ["RecognitionWidget"]
