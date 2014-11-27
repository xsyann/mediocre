#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window_ui.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:07:41 2014 (+0100)
# Last-Updated: Thu Nov 27 04:00:33 2014 (+0100)
#           By: Yann KOETH
#     Update #: 442
#

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QTabWidget,
                             QWidget, QSplitter)

from mediocre.classes_tree_view import ClassesTreeView
from mediocre.widgets import TrainingWidget, DatasetWidget, RecognitionWidget


class WindowUI(object):

    def widgetTraining(self):
        return TrainingWidget(self.classes_tree_view)

    def widgetRecognition(self):
        return RecognitionWidget(self.classes_tree_view)

    def widgetDataset(self):
        return DatasetWidget(self.classes_tree_view)

    def setupUI(self):
        """Create User Interface.
        """
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()

        tabs = QTabWidget()
        self.classes_tree_view = ClassesTreeView(self)
        tabs.addTab(self.widgetDataset(), self.tr("Dataset"))
        tabs.addTab(self.widgetTraining(), self.tr("Training"))
        tabs.addTab(self.widgetRecognition(), self.tr("Recognition"))

        leftLayout, rightLayout = QHBoxLayout(), QHBoxLayout()
        leftLayout.addWidget(self.classes_tree_view)
        rightLayout.addWidget(tabs)
        left, right = QWidget(), QWidget()
        left.setLayout(leftLayout)
        right.setLayout(rightLayout)
        self.hsplitter = QSplitter(QtCore.Qt.Horizontal)
        self.hsplitter.addWidget(left)
        self.hsplitter.addWidget(right)
        self.hsplitter.setStretchFactor(1, 3)

        mainLayout.addWidget(self.hsplitter)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
