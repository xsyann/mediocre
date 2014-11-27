#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 12 16:35:10 2014 (+0100)
# Last-Updated: Wed Nov 26 23:15:18 2014 (+0100)
#           By: Yann KOETH
#     Update #: 1574
#

import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QToolBar, QSizePolicy, QAction, QLineEdit,
                             QScrollArea, QGroupBox, QSpinBox, QFileDialog,
                             QSpinBox, QSplitter, QGridLayout)
from PyQt5.QtCore import QRectF, QEvent, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence, QIcon, QPixmap, QPainter

from mediocre.dataset import Dataset, RandomParam
from mediocre.paint_area import PaintArea
from mediocre.widgets import BrushSizeWidget


class ImageLabel(QLabel):

    def __init__(self, pixmap, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.parent = parent
        self.pixmap = pixmap
        self.setPixmap(self.pixmap)
        self._resize = True

    def resizeEvent(self, event):
        height = self.parent.widget.size().height()
        scaled = self.pixmap.scaledToHeight(height, Qt.SmoothTransformation)
        self.setPixmap(scaled)
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


class DatasetWidgetUI(object):

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

    def sizeWidget(self):
        widget = QWidget()
        layout = QHBoxLayout()
        sizeLabel = QLabel(self.tr("x"))
        self.widthBox = QSpinBox()
        self.heightBox = QSpinBox()
        layout.addWidget(self.widthBox)
        layout.addWidget(sizeLabel)
        layout.addWidget(self.heightBox)
        widget.setLayout(layout)
        return widget

    def randomWidget(self):
        group = QGroupBox("Randomize")
        layout = QGridLayout()
        self.randomCount = QSpinBox()
        layout.addWidget(QLabel(self.tr("Count")), 0, 0)
        layout.addWidget(self.randomCount, 0, 1)
        self.minBrushSize = BrushSizeWidget(15)
        self.maxBrushSize = BrushSizeWidget(50)
        layout.addWidget(QLabel(self.tr("Min")), 1, 0)
        layout.addWidget(self.minBrushSize, 1, 1)
        layout.addWidget(QLabel(self.tr("Max")), 2, 0)
        layout.addWidget(self.maxBrushSize, 2, 1)
        self.xAngle = QSpinBox()
        self.yAngle = QSpinBox()
        self.zAngle = QSpinBox()
        layout.addWidget(QLabel(self.tr("Angle X")), 3, 0)
        layout.addWidget(self.xAngle, 3, 1)
        layout.addWidget(QLabel(self.tr("Angle Y")), 4, 0)
        layout.addWidget(self.yAngle, 4, 1)
        layout.addWidget(QLabel(self.tr("Angle Z")), 5, 0)
        layout.addWidget(self.zAngle, 5, 1)
        container = QVBoxLayout()
        container.addLayout(layout)
        container.addStretch(1)
        group.setLayout(container)
        group.setFixedWidth(150)
        return group

    def toolbarSpacer(self):
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return spacer

    def toolbarWidget(self):
        self.brushSizeWidget = BrushSizeWidget(self.brush_size, max_size=70)
        self.clearAction = QAction(QIcon("assets/clear.png"), "Clear", self)
        self.saveAction = QAction(QIcon("assets/save.png"), "Save", self)
        self.removeAction = QAction(QIcon("assets/remove.png"), "Remove", self)
        self.previewAction = QAction(QIcon("assets/preview.png"), "Preview", self)

        toolbar = QToolBar()
        toolbar.setIconSize(QSize(30, 30))
        toolbar.addWidget(self.brushSizeWidget)
        toolbar.addSeparator()
        toolbar.addAction(self.clearAction)
        toolbar.addAction(self.saveAction)
        toolbar.addAction(self.removeAction)
        toolbar.addAction(self.removeAction)
        toolbar.addAction(self.previewAction)
        toolbar.addSeparator()
        toolbar.addWidget(self.sizeWidget())
        toolbar.addWidget(self.prefixWidget())
        toolbar.addWidget(self.toolbarSpacer())
        return toolbar

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea(self.brush_size)
        self.paintArea.installEventFilter(self)
        self.previewWidget = PreviewWidget()
        layout.addWidget(self.toolbarWidget())
        hbox = QHBoxLayout()
        hbox.addWidget(self.randomWidget())
        hbox.addWidget(self.paintArea)
        up = QWidget()
        up.setLayout(hbox)
        down = QWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.previewWidget)
        down.setLayout(hbox)
        self.vsplitter = QSplitter(Qt.Vertical)
        self.vsplitter.addWidget(up)
        self.vsplitter.addWidget(down)
        self.vsplitter.setStretchFactor(1, 3)
        layout.addWidget(self.vsplitter)
        layout.addWidget(self.folderWidget())
        self.setLayout(layout)


class DatasetWidget(QWidget, DatasetWidgetUI):
    FORMAT = "bmp"

    def __init__(self, classes_tree, parent=None):
        super(DatasetWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self._dataset = None
        self._last = []
        self.brush_size = 20
        self.setupUI()
        self.connectUI()
        self.initUI()
        self.reloadClasses()
        self._dataset = Dataset(self.datasetFolder.text())

    def connectUI(self):
        self.brushSizeWidget.brushSizeChanged.connect(self.setBrushSize)
        self.clearAction.triggered.connect(self.clear)
        self.saveAction.triggered.connect(self.save)
        self.removeAction.triggered.connect(self.removeLast)
        self.previewAction.triggered.connect(self.previewMode)
        self._classes_tree.model.itemChecked.connect(self.reloadClasses)
        self.selectFolderButton.clicked.connect(self.selectFolder)
        self.widthBox.valueChanged.connect(self.widthChanged)
        self.heightBox.valueChanged.connect(self.heightChanged)

    def initUI(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        folder = os.path.join(root, "dataset")
        self.datasetFolder.setText(folder)
        self.widthBox.setRange(5, 5000)
        self.heightBox.setRange(5, 5000)
        self.widthBox.setValue(150)
        self.heightBox.setValue(150)
        self.randomCount.setValue(5)
        self.xAngle.setRange(0, 360)
        self.yAngle.setRange(0, 360)
        self.zAngle.setRange(0, 360)
        self.xAngle.setValue(70)
        self.yAngle.setValue(50)
        self.zAngle.setValue(12)

    def eventFilter(self, watched, event):
        if (event.type() == QEvent.KeyPress and
            (event.matches(QKeySequence.InsertParagraphSeparator) or
             event.key() == Qt.Key_Space)):
            self.save()
        return super(DatasetWidget, self).eventFilter(watched, event)

    ########################################################
    # Utils

    def displayInstructions(self):
        if not self._classes:
            self.paintArea.setInstructions("")
        else:
            class_name = self._classes[self._index].repr
            self.paintArea.setInstructions(class_name)

    def generateRandom(self):
        canvas, lines = self.paintArea.getLines()
        params = RandomParam(self.randomCount.value(), self.widthBox.value(),
                             self.heightBox.value(), self.minBrushSize.value(),
                             self.maxBrushSize.value(), self.xAngle.value(),
                             self.yAngle.value(), self.zAngle.value())
        randoms = self._dataset.generateData(canvas, lines, params)
        return randoms

    def saveImages(self):
        cl = self._classes[self._index]
        pixmap = QPixmap(self.widthBox.value(), self.heightBox.value())
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintArea.render(painter)
        painter.end()
        self._dataset.setFolder(self.datasetFolder.text())
        self._dataset.addDatum(self.prefixLine.text(), cl, pixmap, self.FORMAT)
        randoms = self.generateRandom()
        for random in randoms:
            self._dataset.addDatum(self.prefixLine.text(), cl, random,
                                   self.FORMAT)
        del self._last[:]
        self._last.append(pixmap)
        self._last.extend(randoms)
        return [pixmap] + randoms

    ########################################################
    # Signals handlers

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
            self._dataset.setFolder(file)

    def widthChanged(self, width):
        if self.heightBox.value():
            self.paintArea.setFrame(width, self.heightBox.value())

    def heightChanged(self, height):
        if self.widthBox.value():
            self.paintArea.setFrame(self.widthBox.value(), height)

    def removeLast(self):
        if self._last:
            self._index = (self._index - 1) % len(self._classes)
            for last in self._last:
                if self._dataset.removeLast():
                    self.previewWidget.removeLast()
            del self._last[:]
            self.displayInstructions()
            self.clear()

    def clear(self):
        self.paintArea.clear()

    def save(self):
        if self._classes:
            pixmaps = self.saveImages()
            self._index = (self._index + 1) % len(self._classes)
            self.displayInstructions()
            for pixmap in pixmaps:
                self.previewWidget.addPixmap(pixmap)
            self.clear()

    def setBrushSize(self, size):
        self.paintArea.setBrushSize(size)

    def previewMode(self):
        randoms = self.generateRandom()
        for random in randoms:
            self.previewWidget.addPixmap(random)


__all__ = ["DatasetWidget"]
