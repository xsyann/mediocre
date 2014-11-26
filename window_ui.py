#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window_ui.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:07:41 2014 (+0100)
# Last-Updated: Wed Nov 26 22:53:17 2014 (+0100)
#           By: Yann KOETH
#     Update #: 438
#

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QHBoxLayout, QTabWidget,
                             QWidget, QSplitter)

from classes_tree_view import ClassesTreeView
from dataset_widget import DatasetWidget
from training_widget import TrainingWidget

class WindowUI(object):

    def widgetTraining(self):
        return TrainingWidget(self.classes_tree_view)

    def widgetRecognition(self):
        return QWidget()

    def setupUI(self):
        """Create User Interface.
        """
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()

        tabs = QTabWidget()
        self.classes_tree_view = ClassesTreeView(self)
        tabs.addTab(DatasetWidget(self.classes_tree_view), self.tr("Dataset"))
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

