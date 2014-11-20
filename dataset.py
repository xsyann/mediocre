#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset.py
#
# Author: Yann KOETH
# Created: Mon Nov 10 14:30:25 2014 (+0100)
# Last-Updated: Thu Nov 20 20:38:57 2014 (+0100)
#           By: Yann KOETH
#     Update #: 104
#

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap

class Dataset(object):

    def __init__(self, folder):
        self._folder = folder
        self._last = []

    def addDatum(self, prefix, cl, pixmap, format):
        folder = cl.folder
        dirs = os.path.join(self._folder, folder)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        filename =  prefix + folder
        path = self.generateFilename(dirs, prefix, format)
        if pixmap.save(path, format):
            self._last.append(path)
            print "Write", path

    def removeLast(self):
        if self._last:
            path = self._last[-1]
            os.remove(path)
            print "Remove", path
            self._last.pop(-1)
            return True
        return False

    def generateFilename(self, folder, prefix, ext):
        """Generate a filename in folder.
        folder/prefix-folder.0.ext
        """
        filename = os.path.basename(os.path.normpath(folder))
        filename = "{0}{1}".format(prefix, filename)
        path = self.getIncrementedFilename(os.path.join(folder, filename), ext)
        return path

    def getIncrementedFilename(self, filename, ext):
        i = 0
        while os.path.isfile("{0}.{1}.{2}".format(filename, i, ext)):
            i += 1
        return "{0}.{1}.{2}".format(filename, i, ext)

    def setFolder(self, folder):
        self._folder = folder
