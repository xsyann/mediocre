#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window_ui.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:07:41 2014 (+0100)
# Last-Updated: Tue Nov 11 15:14:07 2014 (+0100)
#           By: Yann KOETH
#     Update #: 160
#

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QHBoxLayout, QTabWidget,
                             QWidget, QSplitter)

from classes_tree_view import ClassesTreeView

class WindowUI(object):

    def widgetDataset(self):
        widget = QWidget()
        return widget

    def widgetTraining(self):
        return QWidget()

    def widgetRecognition(self):
        return QWidget()

    def setupUI(self):
        """Create User Interface.
        """
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()

        tabs = QTabWidget()
        tabs.addTab(self.widgetDataset(), self.tr("Dataset"))
        tabs.addTab(self.widgetTraining(), self.tr("Training"))
        tabs.addTab(self.widgetRecognition(), self.tr("Recognition"))

        self.hsplitter = QSplitter(QtCore.Qt.Horizontal)
        self.classes_tree_view = ClassesTreeView(self)
        self.hsplitter.addWidget(self.classes_tree_view)
        self.hsplitter.addWidget(tabs)

        mainLayout.addWidget(self.hsplitter)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
