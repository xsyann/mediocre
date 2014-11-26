#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset.py
#
# Author: Yann KOETH
# Created: Mon Nov 10 14:30:25 2014 (+0100)
# Last-Updated: Wed Nov 26 15:06:14 2014 (+0100)
#           By: Yann KOETH
#     Update #: 188
#

import os
import random

from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsLineItem,
                             QGraphicsItemGroup, QGraphicsRotation)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QVector3D

class RandomParam():
    def __init__(self, count, width, height, minThick, maxThick,
                 xAngle, yAngle, zAngle):
        args = locals()
        args.pop('self')
        for k, v in args.iteritems():
            self.__dict__[k] = v

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

    def randomRotate(self, item, maxAngle, axis):
        transform = QGraphicsRotation()
        transform.setOrigin(QVector3D(item.boundingRect().center()))
        transform.setAngle(random.uniform(-maxAngle, maxAngle))
        transform.setAxis(axis)
        transformations = item.transformations()
        transformations.append(transform)
        item.setTransformations(transformations)

    def generateRandom(self, scene, group, canvas, params):
        penWidth = random.randint(params.minThick, params.maxThick)
        for item in scene.items():
            if item.group() == group:
                pen = item.pen()
                pen.setWidth(penWidth)
                item.setPen(pen)
        self.randomRotate(group, params.xAngle, Qt.XAxis)
        self.randomRotate(group, params.yAngle, Qt.YAxis)
        self.randomRotate(group, params.zAngle, Qt.ZAxis)
        pixmap = QPixmap(params.width, params.height)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        scene.render(painter, source=canvas)
        painter.end()
        group.setTransformations([])
        return pixmap

    def generateData(self, canvas, lines, params):
        scene = QGraphicsScene()
        scene.setSceneRect(canvas)
        group = scene.createItemGroup([])
        for line in lines:
            clone = QGraphicsLineItem(line)
            clone.setLine(line.line())
            clone.setPen(line.pen())
            scene.addItem(clone)
            group.addToGroup(clone)
        pixmaps = []
        for i in xrange(params.count):
            pixmaps.append(self.generateRandom(scene, group, canvas, params))
        return pixmaps
