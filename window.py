#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:14:27 2014 (+0100)
# Last-Updated: Mon Nov 10 19:07:26 2014 (+0100)
#           By: Yann KOETH
#     Update #: 192
#

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QMainWindow, QApplication)
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from window_ui import WindowUI
from classes import Classes

class TreeModel(QStandardItemModel):

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.itemChanged.connect(self._itemChanged)

    def _itemChanged(self, item):
        item.setCheckState(item.checkState())

    def mapChildren(self, parent, method):
        for i in xrange(parent.rowCount()):
            item = parent.child(i)
            method(item)
            self.mapChildren(item, method)

class TreeItem(QStandardItem):

    def setCheckState(self, state):
        method = lambda child: child.setEnabled(state == QtCore.Qt.Checked)
        self.model().mapChildren(self, method)
        return super(TreeItem, self).setCheckState(state)

class Window(QMainWindow, WindowUI):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUI()
        self.populateUI()
        self.connectUI()
        self.initUI()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def populateUI(self):
        self.classes_tree_model = self.convertTree(Classes.getClasses())
        self.classes_tree.setModel(self.classes_tree_model)

    def connectUI(self):
        self.hsplitter.splitterMoved.connect(self.splitterMoved)

    def initUI(self):
        self.initClassesTree()

    def initClassesTree(self):
        self.classes_tree.header().close()
        model = self.classes_tree_model
        unchecked = [Classes.ENGLISH_ALPHABET, Classes.PUNCTUATION]
        method = lambda child: child.setCheckState(QtCore.Qt.Checked \
            if not child.data() in unchecked else QtCore.Qt.Unchecked)
        model.mapChildren(model.invisibleRootItem(), method)

    ########################################################
    # Utils

    def convertTree(self, tree):
        def cloneChildren(source, parent):
            for i in xrange(source.rowCount()):
                item = source.child(i)
                clone = TreeItem(item.text())
                clone.setData(item.data())
                clone.setCheckable(True)
                parent.appendRow(clone)
                cloneChildren(item, clone)
        model = TreeModel(self)
        cloneChildren(tree.invisibleRootItem(), model)
        return model

    ########################################################
    # Signals handlers

    def splitterMoved(self, pos, index):
        """Avoid segfault when QTreeView has focus and
        is going to be collapsed.
        """
        focusedWidget = QApplication.focusWidget()
        if focusedWidget:
            focusedWidget.clearFocus()
