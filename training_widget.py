#!/usr/bin/env python
# -*- coding: utf-8 -*-
# training_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:06:45 2014 (+0100)
# Last-Updated: Wed Nov 26 23:10:37 2014 (+0100)
#           By: Yann KOETH
#     Update #: 78
#

import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QToolBar, QSizePolicy, QFileDialog,
                             QLineEdit, QScrollArea, QGroupBox, QSpinBox,
                             QComboBox, QSpinBox, QSplitter, QTextEdit,
                             QGridLayout)
from PyQt5.QtCore import QRectF, QEvent, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence, QIcon, QPixmap, QPainter

from dataset import Dataset
from ocr import OCR

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

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.datasetFolder.setText(file)
            self._dataset.setFolder(file)

    def train(self):
        print self.maxPerClass.value()
        print self.trainRatio.value()
        modes = {
            self.MODE_ANN: OCR.MODEL_ANN,
            self.MODE_KNEAREST: OCR.MODEL_KNEAREST
            }
        mode = modes[self.__modes[self.mode.currentIndex()]]
        print mode
        classes = self._classes_tree.getClasses()
        self.outputText.setText("Ta mere")
        ocr = OCR()
        ocr.trainModel(self._dataset, classes, mode, self.trainRatio.value(),
                       self.maxPerClass.value())
        # ocr.saveModel()
