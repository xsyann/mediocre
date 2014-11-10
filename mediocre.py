#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mediocre.py
#
# Author: Yann KOETH
# Created: Sun Nov  9 14:56:03 2014 (+0100)
# Last-Updated: Sun Nov  9 15:22:01 2014 (+0100)
#           By: Yann KOETH
#     Update #: 30
#

import sys
from PyQt5.QtWidgets import QApplication

from window import Window

APP_NAME = 'Mediocre'

def main():

    app = QApplication(sys.argv)

    main = Window()
    main.setWindowTitle(APP_NAME)
    main.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
