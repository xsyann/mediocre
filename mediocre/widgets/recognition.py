#!/usr/bin/env python
# -*- coding: utf-8 -*-
# recognition.py
#
# Author: Yann KOETH
# Created: Thu Nov 27 03:53:17 2014 (+0100)
# Last-Updated: Thu Nov 27 12:54:48 2014 (+0100)
#           By: Yann KOETH
#     Update #: 138
#

import os
from collections import OrderedDict

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QFont, QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

from mediocre.ocr import ModelException, OCR
from mediocre.paint_area import PaintArea


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
        self.paintArea = PaintArea(30)
        self.runButton = QPushButton(self.tr("Run"))
        self.runButton.setFont(QFont('Arial', 15, QFont.Bold))
        self.results = OrderedDict((m, QLabel(m + ": ")) for m in self._modes)
        layout.addWidget(self.paintArea)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.runButton)
        hbox.addStretch(1)
        layout.addLayout(hbox)
        layout.addWidget(self.folderWidget())
        for label in self.results.values():
            layout.addWidget(label)
        self.setLayout(layout)


class RecognitionWidget(QWidget, RecognitionWidgetUI):
    MODE_ANN = "Artifical Neural Networks"
    MODE_KNN = "K-Nearest Neighbors"
    MODE_SVM = "Support Vector Machines"
    _modes = [MODE_ANN, MODE_KNN, MODE_SVM]

    def __init__(self, classes_tree, parent=None):
        super(RecognitionWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self.setupUI()
        self.connectUI()
        self.initUI()
        self.ocr = OCR()
        self.paintArea.installEventFilter(self)

    def connectUI(self):
        self.runButton.clicked.connect(self.run)
        self.selectFolderButton.clicked.connect(self.selectFolder)

    def initUI(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        folder = os.path.join(root, "models")
        self.modelsFolder.setText(folder)

    def eventFilter(self, watched, event):
        if (event.type() == QEvent.KeyPress and
            (event.matches(QKeySequence.InsertParagraphSeparator) or
             event.key() == Qt.Key_Space)):
            self.run()
        return super(RecognitionWidget, self).eventFilter(watched, event)

    def run_mode(self, mode, pixmap):
        folder = self.modelsFolder.text()
        classes = self._classes_tree.getClasses()
        self.ocr.loadModel(classes, folder, mode)
        chr = self.ocr.charFromImage(pixmap)
        for cl in classes:
            if cl.value == chr:
                return cl.repr
        return chr

    def run(self):
        modes = {
            self.MODE_ANN: OCR.MODEL_ANN,
            self.MODE_KNN: OCR.MODEL_KNN,
            self.MODE_SVM: OCR.MODEL_SVM
        }
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintArea.render(painter)
        painter.end()

        for mode, label in self.results.items():
            try:
                result = self.run_mode(modes[mode], pixmap)
            except ModelException:
                label.setText(mode + ": need training")
            else:
                label.setText(mode + ": " + result)
        self.paintArea.clear()

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.modelsFolder.setText(file)


__all__ = ["RecognitionWidget"]
