#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mediocre.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 14:56:03 2014 (+0100)
# Last-Updated: Thu Nov 13 19:04:43 2014 (+0100)
#           By: Yann KOETH
#     Update #: 72
#

import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QPalette, QColor

from window import Window

APP_NAME = 'Mediocre'

def main():

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    main = Window()
    main.resize(800, 400)
    main.setWindowTitle(APP_NAME)
    main.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
