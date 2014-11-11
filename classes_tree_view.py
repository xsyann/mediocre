#!/usr/bin/env python
# -*- coding: utf-8 -*-
# classes_tree_view.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 15:10:03 2014 (+0100)
# Last-Updated: Tue Nov 11 15:13:27 2014 (+0100)
#           By: Yann KOETH
#     Update #: 12
#

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QTreeView, QHBoxLayout, QGroupBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from classes import Classes

class TreeModel(QStandardItemModel):

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.itemChanged.connect(self.__itemChanged)

    def __itemChanged(self, item):
        item.setCheckState(item.checkState())

    def mapChildren(self, parent, method):
        for i in xrange(parent.rowCount()):
            item = parent.child(i)
            method(item)
            self.mapChildren(item, method)

class TreeItem(QStandardItem):

    def setCheckState(self, state):
        enable = (state == QtCore.Qt.Checked)
        parent = self.parent()
        while parent:
            enable &= (parent.checkState() == QtCore.Qt.Checked)
            parent = parent.parent()
        method = lambda child: child.setEnabled(enable)
        self.model().mapChildren(self, method)
        return super(TreeItem, self).setCheckState(state)


class ClassesTreeView(QWidget):

    def __init__(self, parent=None):
        super(ClassesTreeView, self).__init__(parent)
        self.parent = parent
        self.setupUI()
        self.populateUI()
        self.initUI()

    def setupUI(self):
        self.tree = QTreeView()
        treeLayout = QHBoxLayout()
        treeLayout.addWidget(self.tree)
        groupBox = QGroupBox(self.tr("Classes"))
        groupBox.setLayout(treeLayout)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(groupBox)
        self.setLayout(mainLayout)

    def populateUI(self):
        self.model = self.convertTree(Classes.getClasses())
        self.tree.setModel(self.model)

    def initUI(self):
        self.tree.header().close()
        unchecked = [Classes.ENGLISH_ALPHABET, Classes.PUNCTUATION]
        method = lambda child: child.setCheckState(QtCore.Qt.Checked \
            if not child.data() in unchecked else QtCore.Qt.Unchecked)
        self.model.mapChildren(self.model.invisibleRootItem(), method)

    def convertTree(self, tree):
        def cloneChildren(source, parent):
            for i in xrange(source.rowCount()):
                item = source.child(i)
                clone = TreeItem(item.text())
                clone.setData(item.data())
                clone.setCheckable(True)
                parent.appendRow(clone)
                cloneChildren(item, clone)
        model = TreeModel(self.parent)
        cloneChildren(tree.invisibleRootItem(), model)
        return model
