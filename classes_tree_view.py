#!/usr/bin/env python
# -*- coding: utf-8 -*-
# classes_tree_view.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 15:10:03 2014 (+0100)
# Last-Updated: Thu Nov 13 18:55:20 2014 (+0100)
#           By: Yann KOETH
#     Update #: 80
#

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTreeView, QHBoxLayout, QGroupBox
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from classes import Classes, Class

class TreeItem(QStandardItem):

    def setData(self, value, role=Qt.UserRole + 1):
        state = self.checkState()
        super(TreeItem, self).setData(value, role)
        if (role == Qt.CheckStateRole and
            state != self.checkState()):
            model = self.model()
            if model is not None:
                model.itemChecked.emit(self)

    def isActivated(self):
        return self.checkState() == Qt.Checked and self.isEnabled()

    def setCheckState(self, state):
        enable = (state == Qt.Checked)
        parent = self.parent()
        while parent:
            enable &= (parent.checkState() == Qt.Checked)
            parent = parent.parent()
        method = lambda child: child.setEnabled(enable)
        self.model().mapChildren(self, method)
        return super(TreeItem, self).setCheckState(state)

class TreeModel(QStandardItemModel):

    itemChecked = pyqtSignal(TreeItem)

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.itemChecked.connect(self.__itemChecked)

    def __itemChecked(self, item):
        item.setCheckState(item.checkState())

    def mapChildren(self, parent, method):
        for i in xrange(parent.rowCount()):
            item = parent.child(i)
            method(item)
            self.mapChildren(item, method)

class ClassesTreeView(QTreeView):

    def __init__(self, parent=None):
        super(ClassesTreeView, self).__init__(parent)
        self.parent = parent
        self.populateUI()
        self.initUI()

    def populateUI(self):
        self.model = self.convertTree(Classes.getClasses())
        self.model.setHorizontalHeaderLabels(["Classes"])
        self.setModel(self.model)

    def initUI(self):
        unchecked = [Classes.ENGLISH_ALPHABET, Classes.PUNCTUATION]
        method = (lambda c: c.setCheckState(Qt.Checked if not c.data() in \
                                                unchecked else Qt.Unchecked))
        self.model.mapChildren(self.model.invisibleRootItem(), method)

    def getClasses(self):
       classes = []
       method = lambda child: classes.append(child.data()) \
           if isinstance(child.data(), Class) and child.isActivated() else False
       self.model.mapChildren(self.model.invisibleRootItem(), method)
       return classes

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
