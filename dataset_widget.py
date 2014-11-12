#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset_widget.py
#
# Author: Yann KOETH
# Created: Wed Nov 12 16:35:10 2014 (+0100)
# Last-Updated: Wed Nov 12 17:05:19 2014 (+0100)
#           By: Yann KOETH
#     Update #: 10
#

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from paint_area import PaintArea
from brush_size_widget import BrushSizeWidget

class DatasetWidget(QWidget):

    DEFAULT_SIZE = 10

    def __init__(self, parent=None):
        super(DatasetWidget, self).__init__(parent)
        self.setupUI()
        self.connectUI()

    def setupUI(self):
        layout = QVBoxLayout()
        self.paintArea = PaintArea(10)
        self.brushSizeWidget = BrushSizeWidget(10)
        layout.addWidget(self.brushSizeWidget)
        layout.addWidget(self.paintArea)
        self.setLayout(layout)

    def connectUI(self):
        self.brushSizeWidget.brushSizeChanged.connect(self.setBrushSize)

    def setBrushSize(self, size):
        self.paintArea.setBrushSize(size)
