#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window_ui.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:07:41 2014 (+0100)
# Last-Updated: Mon Nov 10 19:19:47 2014 (+0100)
#           By: Yann KOETH
#     Update #: 102
#

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QHBoxLayout, QTabWidget, QTreeView,
                             QWidget, QGroupBox, QSplitter)

class WindowUI(object):

    def widgetDataset(self):
        return QWidget()

    def widgetTraining(self):
        return QWidget()

    def widgetRecognition(self):
        return QWidget()

    def widgetClassesTree(self):
        self.classes_tree = QTreeView()
        treeLayout = QHBoxLayout()
        treeLayout.addWidget(self.classes_tree)
        groupBox = QGroupBox(self.tr("Classes"))
        groupBox.setLayout(treeLayout)
        return groupBox

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
        self.hsplitter.addWidget(self.widgetClassesTree())
        self.hsplitter.addWidget(tabs)

        mainLayout.addWidget(self.hsplitter)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

