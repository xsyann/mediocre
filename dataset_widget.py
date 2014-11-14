#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 12 16:35:10 2014 (+0100)
# Last-Updated: Fri Nov 14 21:54:31 2014 (+0100)
#           By: Yann KOETH
#     Update #: 478
#

import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QToolBar, QSizePolicy, QAction, QLineEdit,
                             QScrollArea, QGroupBox, QSpinBox, QFileDialog)
from PyQt5.QtCore import QRectF, QEvent, Qt, QSize
from PyQt5.QtGui import QFont, QKeySequence, QIcon, QPixmap, QPainter

from paint_area import PaintArea
from brush_size_widget import BrushSizeWidget
from dataset import Dataset

class DatasetWidget(QWidget):

    FORMAT = "bmp"
    SAVE_SIZE = 50, 50
    PAINT_SIZE = 300, 300

    def __init__(self, classes_tree, parent=None):
        super(DatasetWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self._dataset = None
        self.brush_size = 13
        self.setupUI()
        self.connectUI()
        self.initUI()
        self.reloadClasses()

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea(self.brush_size)
        self.paintArea.setFixedSize(*self.PAINT_SIZE)
        self.paintArea.installEventFilter(self)
        self.previewLabel = QLabel(self.tr("Preview"))
        layout.addWidget(self.toolbarWidget())
        hbox = QHBoxLayout()
        hbox.addWidget(self.randomWidget())
        hbox.addWidget(self.paintArea)
        layout.addLayout(hbox)
        layout.addWidget(self.folderWidget())
        self.setLayout(layout)

    def initUI(self):
        folder = os.path.join(os.path.dirname(__file__), "dataset")
        self.datasetFolder.setText(folder)

    def connectUI(self):
        self.brushSizeWidget.brushSizeChanged.connect(self.setBrushSize)
        self.clearAction.triggered.connect(self.clear)
        self.saveAction.triggered.connect(self.save)
        self._classes_tree.model.itemChecked.connect(self.reloadClasses)
        self.selectFolderButton.clicked.connect(self.selectFolder)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress and \
                (event.matches(QKeySequence.InsertParagraphSeparator) or \
                event.key() == Qt.Key_Space):
            self.save()
        return super(DatasetWidget, self).eventFilter(watched, event)

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

    def prefixWidget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        prefixLabel = QLabel(self.tr("Prefix:"))
        self.prefixLine = QLineEdit()
        self.prefixLine.setPlaceholderText(self.tr("login_x-"))
        self.prefixLine.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        layout.addWidget(prefixLabel)
        layout.addWidget(self.prefixLine)
        widget.setLayout(layout)
        return widget

    def randomWidget(self):
        group = QGroupBox("Randomize")
        countLayout = QHBoxLayout()
        self.randomCount = QSpinBox()
        countLayout.addWidget(QLabel(self.tr("Count")))
        countLayout.addWidget(self.randomCount)
        countLayout.addStretch(1)
        layout = QVBoxLayout()
        self.minBrushSize = BrushSizeWidget(3)
        self.maxBrushSize = BrushSizeWidget(20)
        brushSizeRange = QHBoxLayout()
        brushSizeRange.addWidget(QLabel(self.tr("Min")))
        brushSizeRange.addWidget(self.minBrushSize)
        brushSizeRange.addStretch(1)
        brushSizeRange.addWidget(QLabel(self.tr("Max")))
        brushSizeRange.addWidget(self.maxBrushSize)
        layout.addLayout(countLayout)
        layout.addLayout(brushSizeRange)
        layout.addStretch(1)
        group.setLayout(layout)
        group.setFixedWidth(200)
        return group

    def toolbarSpacer(self):
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return spacer

    def toolbarWidget(self):
        self.brushSizeWidget = BrushSizeWidget(self.brush_size)
        self.instructionLabel = QLabel()
        f = QFont('Arial', 20, QFont.Bold)
        self.instructionLabel.setFont(f)
        self.clearAction = QAction(QIcon('assets/clear.png'), 'Clear', self)
        self.saveAction = QAction(QIcon('assets/save.png'), 'Save', self)
        self.removeAction = QAction(QIcon('assets/remove.png'), 'Remove', self)

        toolbar = QToolBar()

        toolbar.setIconSize(QSize(30, 30))
        toolbar.addWidget(self.brushSizeWidget)
        toolbar.addSeparator()
        toolbar.addAction(self.clearAction)
        toolbar.addAction(self.saveAction)
        toolbar.addAction(self.removeAction)
        toolbar.addSeparator()
        toolbar.addWidget(self.prefixWidget())
        toolbar.addWidget(self.toolbarSpacer())
        toolbar.addWidget(self.instructionLabel)
        return toolbar

    def reloadClasses(self):
        self.clear()
        self._index = 0
        self._classes = self._classes_tree.getClasses()
        self.displayInstructions()
        self.setEnabled(len(self._classes) > 0)

    def selectFolder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file:
            self.datasetFolder.setText(file)

    def displayInstructions(self):
        if not self._classes:
            self.instructionLabel.setText("")
        else:
            class_name = self._classes[self._index].repr
            self.instructionLabel.setText(self.tr("Draw: ") + class_name)

    def clear(self):
        self.paintArea.clear()

    def saveImage(self):
        cl = self._classes[self._index]
        pixmap = QPixmap(*self.SAVE_SIZE)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintArea.render(painter)
        painter.end()
        if not self._dataset:
            self._dataset = Dataset(self.datasetFolder.text())
        else:
            self._dataset.setFolder(self.datasetFolder.text())
        self._dataset.addDatum(self.prefixLine.text(), cl, pixmap, self.FORMAT)

    def save(self):
        if self._classes:
            self.saveImage()
            self._index = (self._index + 1) % len(self._classes)
            self.displayInstructions()
            self.clear()
#        pixmap = QPixmap(300, 600)
#        pixmap.fill(Qt.white)
#        painter = QPainter(pixmap)
#        painter.setRenderHint(QPainter.Antialiasing)
#        self.paintArea.render(painter)
#        painter.end()
#        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#        print self.scrollArea.size()
#        self.previewLabel.resize(self.scrollArea.size())
#        self.previewLabel.setPixmap(pixmap)
#        print self.previewLabel.size()

    def setBrushSize(self, size):
        self.paintArea.setBrushSize(size)
