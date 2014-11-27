#!/usr/bin/env python
# -*- coding: utf-8 -*-
# training_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:06:45 2014 (+0100)
# Last-Updated: Thu Nov 27 15:18:11 2014 (+0100)
#           By: Yann KOETH
#     Update #: 142
#

import os

from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTextEdit, QVBoxLayout,
                             QWidget)

from mediocre.dataset import Dataset
from mediocre.ocr import OCR


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
        self.errorsIteration = QSpinBox()
        layout.addWidget(QLabel(self.tr("Train ratio")), 0, 0)
        layout.addWidget(self.trainRatio, 0, 1)
        layout.addWidget(QLabel(self.tr("Maximum per class")), 1, 0)
        layout.addWidget(self.maxPerClass, 1, 1)
        layout.addWidget(QLabel(self.tr("Mode")), 3, 0)
        layout.addWidget(self.mode, 3, 1)
        layout.addWidget(QLabel(self.tr("Errors iteration")), 2, 0)
        layout.addWidget(self.errorsIteration, 2, 1)
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
    MODE_ANN = "Artificial Neural Networks"
    MODE_KNN = "K-Nearest Neighbors"
    MODE_SVM = "Support Vector Machines"
    __modes = [MODE_ANN, MODE_KNN, MODE_SVM]

    def __init__(self, classes_tree, parent=None):
        super(TrainingWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self.setupUI()
        self.populateUI()
        self.connectUI()
        self.initUI()
        self._dataset = Dataset(self.datasetFolder.text())
        self.datasetFolder.textChanged.connect(self._dataset.setFolder)

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
        self.errorsIteration.setRange(0, 500)
        self.maxPerClass.setValue(400)
        self.trainRatio.setValue(50)
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        folder = os.path.join(root, "dataset")
        self.datasetFolder.setText(folder)

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.datasetFolder.setText(file)
            self._dataset.setFolder(file)

    def log(self, text):
        cursor = self.outputText.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.outputText.setTextCursor(cursor)
        QApplication.processEvents()

    def train(self):
        modes = {
            self.MODE_ANN: OCR.MODEL_ANN,
            self.MODE_KNN: OCR.MODEL_KNN,
            self.MODE_SVM: OCR.MODEL_SVM
        }
        mode = modes[self.__modes[self.mode.currentIndex()]]
        classes = self._classes_tree.getClasses()
        ocr = OCR()
        ocr.trainModel(self._dataset, classes, mode,
                       self.trainRatio.value() / 100.0,
                       self.maxPerClass.value(), self.errorsIteration.value(),
                       self.log)
        ocr.saveModel()


__all__ = ["TrainingWidget"]
