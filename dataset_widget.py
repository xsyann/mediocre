#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 12 16:35:10 2014 (+0100)
# Last-Updated: Thu Nov 20 20:47:34 2014 (+0100)
#           By: Yann KOETH
#     Update #: 1306
#

import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QToolBar, QSizePolicy, QAction, QLineEdit,
                             QScrollArea, QGroupBox, QSpinBox, QFileDialog)
from PyQt5.QtCore import QRectF, QEvent, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence, QIcon, QPixmap, QPainter

from paint_area import PaintArea
from brush_size_widget import BrushSizeWidget
from dataset import Dataset

class ImageLabel(QLabel):

    def __init__(self, pixmap, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.parent = parent
        self.pixmap = pixmap
        self.setPixmap(self.pixmap)
        self._resize = True

    def resizeEvent(self, event):
        self.scaled = self.pixmap.scaledToHeight(self.parent.widget.size().height(),
                                                 Qt.SmoothTransformation)
        self.setPixmap(self.scaled)
        super(ImageLabel, self).resizeEvent(event)

class PreviewWidget(QScrollArea):

    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.layout.addStretch(1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

    def removeLast(self):
        item = self.layout.takeAt(0)
        if item:
            item.widget().deleteLater()

    def resizeEvent(self, event):
        self.widget.setFixedHeight(self.viewport().height())
        super(PreviewWidget, self).resizeEvent(event)

    def addPixmap(self, pixmap):
        label = ImageLabel(pixmap, self)
        self.layout.insertWidget(0, label)

class DatasetWidget(QWidget):

    FORMAT = "bmp"
    SAVE_SIZE = 150, 150

    def __init__(self, classes_tree, parent=None):
        super(DatasetWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self._dataset = None
        self.brush_size = 20
        self.setupUI()
        self.connectUI()
        self.initUI()
        self.reloadClasses()

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea(self.brush_size)
        self.paintArea.installEventFilter(self)
        self.paintArea.setFrame(*self.SAVE_SIZE)
        self.previewWidget = PreviewWidget()
        layout.addWidget(self.toolbarWidget())
        hbox = QHBoxLayout()
        hbox.addWidget(self.randomWidget())
        hbox.addWidget(self.paintArea)
        layout.addLayout(hbox)
        layout.addWidget(self.previewWidget)
        layout.addWidget(self.folderWidget())
        self.setLayout(layout)

    def initUI(self):
        folder = os.path.join(os.path.dirname(__file__), "dataset")
        self.datasetFolder.setText(folder)

    def connectUI(self):
        self.brushSizeWidget.brushSizeChanged.connect(self.setBrushSize)
        self.clearAction.triggered.connect(self.clear)
        self.saveAction.triggered.connect(self.save)
        self.removeAction.triggered.connect(self.removeLast)
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

    def removeLast(self):
       if self._dataset:
           if self._dataset.removeLast():
               self._index = (self._index - 1) % len(self._classes)
               self.previewWidget.removeLast()
               self.displayInstructions()

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
        return pixmap

    def save(self):
        if self._classes:
            pixmap = self.saveImage()
            self._index = (self._index + 1) % len(self._classes)
            self.displayInstructions()
            self.previewWidget.addPixmap(pixmap)
            self.clear()

    def setBrushSize(self, size):
        self.paintArea.setBrushSize(size)
