#!/usr/bin/env python
# -*- coding: utf-8 -*-
# window.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 15:14:27 2014 (+0100)
# Last-Updated: Tue Nov 11 15:14:08 2014 (+0100)
#           By: Yann KOETH
#     Update #: 218
#

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow

from mediocre.window_ui import WindowUI


class Window(QMainWindow, WindowUI):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUI()
        self.connectUI()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def connectUI(self):
        self.hsplitter.splitterMoved.connect(self.splitterMoved)

    def splitterMoved(self, pos, index):
        """Avoid segfault when QTreeView has focus and is going to be collapsed.
        """
        focusedWidget = QApplication.focusWidget()
        if focusedWidget:
            focusedWidget.clearFocus()
