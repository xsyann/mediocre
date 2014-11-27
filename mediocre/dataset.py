#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dataset.py
#
# Author: Yann KOETH
# Created: Mon Nov 10 14:30:25 2014 (+0100)
# Last-Updated: Thu Nov 27 11:14:05 2014 (+0100)
#           By: Yann KOETH
#     Update #: 326
#

import os
import random
import cv2
import numpy as np

from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsLineItem,
                             QGraphicsItemGroup, QGraphicsRotation)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QVector3D, QImage


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
        self._classes = None
        self._last = []

    @property
    def trainSampleCount(self):
        if self.trainSamples.size == 0:
            return 0
        trainSampleCount, size = self.trainSamples.shape
        return trainSampleCount

    @property
    def testSampleCount(self):
        if self.testSamples.size == 0:
            return 0
        testSampleCount, size = self.testSamples.shape
        return testSampleCount

    def getResponse(self, index):
        return self.classes[int(index)]

    def addDatum(self, prefix, cl, pixmap, format):
        folder = cl.folder
        dirs = os.path.join(self._folder, folder)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        filename = prefix + folder
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

    def folder(self):
        return self._folder

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

    def preprocess(self, classes, maxPerClass, trainRatio, preprocess):
        self.maxPerClass = maxPerClass
        self.trainRatio = trainRatio
        self.classes = classes
        self.__stackArrays(self.__getItems(self.trainRatio, preprocess))

    def __getItems(self, trainRatio, preprocess):
        """Create dataset items.
        """
        trainItems = []
        testItems = []
        for cl in self.classes:
            folder = os.path.join(self._folder, cl.folder)
            images = self.__getImages(folder)
            random.shuffle(images)
            currentClassItems = []
            for i, image in enumerate(images):
                if i >= self.maxPerClass:
                    break
                item = DatasetItem(preprocess, cl)
                item.loadFromFile(image)
                currentClassItems.append(item)
            trainCount = int(np.ceil(min(len(images), self.maxPerClass) * trainRatio))
            trainItems.extend(currentClassItems[:trainCount])
            testItems.extend(currentClassItems[trainCount:])
        return (trainItems, testItems)

    def __getImages(self, folder):
        """Returns a list of all images in folder.
        """
        imgExt = [".bmp", ".png"]
        images = []
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                filename, ext = os.path.splitext(file)
                if ext.lower() in imgExt:
                    images.append(os.path.join(folder, file))
        return images

    def __stackArraysAux(self, items):
        """Create samples and responses arrays.
        """
        if not items:
            return (np.array([]), np.array([]))
        samples = []
        responses = []
        nClass = len(self.classes)
        for item in items:
            responses.append(self.classes.index(item.cl))
            samples.append(item.sample)
        return (np.vstack(samples), np.array(responses))

    def __stackArrays(self, items):
        trainItems, testItems = items
        self.trainSamples, self.trainResponses = self.__stackArraysAux(trainItems)
        self.testSamples, self.testResponses = self.__stackArraysAux(testItems)


class DatasetItem(object):
    """An item in the data set.
    Handle pre-processing of that item.
    """
    RESIZE = 16

    def __init__(self, preprocess=None, cl=None):
        self.input = None
        self.preprocessed = None
        self.preprocess = preprocess
        self.cl = cl

    def loadFromFile(self, filename):
        if not os.path.isfile(filename):
            raise OSError(2, 'File not found', filename)
        self.preprocessed = self.preprocess(filename)

    def loadFromImage(self, img):
        img.save("/tmp/buffer.bmp", "BMP")
        self.loadFromFile("/tmp/buffer.bmp")
        os.remove("/tmp/buffer.bmp")

    @property
    def sample(self):
        sample = np.array(self.preprocessed)
        return sample.ravel().astype(np.float32)
