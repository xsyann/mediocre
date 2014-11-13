#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 12 16:35:10 2014 (+0100)
# Last-Updated: Thu Nov 13 18:15:03 2014 (+0100)
#           By: Yann KOETH
#     Update #: 158
#

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel)
from PyQt5.QtCore import QRectF, QEvent, Qt
from PyQt5.QtGui import QFont, QKeySequence

from paint_area import PaintArea
from brush_size_widget import BrushSizeWidget

class DatasetWidget(QWidget):

    def __init__(self, classes_tree, parent=None):
        super(DatasetWidget, self).__init__(parent)
        self._classes_tree = classes_tree
        self.brush_size = 10
        self.setupUI()
        self.connectUI()
        self.reloadClasses()

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea(self.brush_size)
        self.paintArea.installEventFilter(self)
        self.paintArea.setSceneRect(QRectF(0, 0, 320, 240))
        layout.addWidget(self.toolbarWidget())
        layout.addWidget(self.paintArea)
        self.setLayout(layout)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress and \
                (event.matches(QKeySequence.InsertParagraphSeparator) or \
                event.key() == Qt.Key_Space):
            self.save()
        return super(DatasetWidget, self).eventFilter(watched, event)

    def toolbarWidget(self):
        toolbar = QWidget()
        layout = QHBoxLayout()
        self.brushSizeWidget = BrushSizeWidget(self.brush_size)
        self.clearButton = QPushButton(self.tr("Clear"))
        self.saveButton = QPushButton(self.tr("Save"))
        self.instructionLabel = QLabel()
        f = QFont('Arial', 20, QFont.Bold)
        self.instructionLabel.setFont(f)
        layout.addWidget(self.brushSizeWidget)
        layout.addWidget(self.clearButton)
        layout.addWidget(self.saveButton)
        layout.addStretch(1)
        layout.addWidget(self.instructionLabel)
        toolbar.setLayout(layout)
        return toolbar

    def connectUI(self):
        self.brushSizeWidget.brushSizeChanged.connect(self.setBrushSize)
        self.clearButton.clicked.connect(self.clear)
        self.saveButton.clicked.connect(self.save)
        self._classes_tree.model.itemChecked.connect(self.reloadClasses)

    def reloadClasses(self):
        self.clear()
        self._index = 0
        self._classes = self._classes_tree.getClasses()
        self.displayInstructions()
        self.setEnabled(len(self._classes) > 0)

    def displayInstructions(self):
        if not self._classes:
            self.instructionLabel.setText("")
        else:
            class_name = self._classes[self._index].repr
            self.instructionLabel.setText(self.tr("Draw: ") + class_name)

    def clear(self):
        self.paintArea.clear()

    def save(self):
        if self._classes:
            print "save", self._classes[self._index].folder
        if self._classes:
            self._index = (self._index + 1) % len(self._classes)
        self.displayInstructions()
        self.clear()

    def setBrushSize(self, size):
        self.paintArea.setBrushSize(size)
