#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ocr.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:47:17 2014 (+0100)
# Last-Updated: Thu Nov 27 00:28:29 2014 (+0100)
#           By: Yann KOETH
#     Update #: 68
#

import os
import sys
import hashlib
from analyzer import Analyzer

from mediocre import models


class OCR(object):
    MODEL_ANN = 0
    MODEL_KNEAREST = 1

    def getModelFilename(self, classes):
        values = [cl.value for cl in classes]
        values.sort()
        m = hashlib.md5(''.join(values))
        return "{0}_{1}.yml".format(m.hexdigest(), self.__type)

    def saveModel(self):
        root = os.path.dirname(os.path.dirname(__file__))
        folder = os.path.join(root, "models")
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = self.getModelFilename(self.__classes)
        self.__model.save(os.path.join(folder, filename))

#    def loadModel(self, filename, type=MODEL_ANN):
#        folders = OCR.generateFolderList(flags=flags)
#        self.__dataset = dataset.Dataset(folders)
#        self.__model = self.__initModel(type)
#        self.__model.load(filename)

    def trainModel(self, dataset, classes, type=MODEL_ANN, trainRatio=.5,
                   maxPerClass=100, verbose=True):
        self.__dataset = dataset
        self.__classes = classes
        self.__type = type
        if verbose:
            print "Pre-processing..."
        self.__dataset.preprocess(classes, maxPerClass, trainRatio)
        self.__model = self.__initModel(type)
        self.__trainModel(verbose=verbose, trainRatio=trainRatio)

#    def charFromImage(self, image):
#        item = dataset.DatasetItem()
#        item.loadFromImage(image)
#        return self.__charFromDatasetItem(item)

#    def charFromFile(self, filename):
#        item = dataset.DatasetItem()
#        item.loadFromFile(filename)
#        return self.__charFromDatasetItem(item)

#    def __charFromDatasetItem(self, item):
#        sample = np.array([item.sample])
#        response = self.__dataset.getResponse(int(self.__model.predict(sample)[0]))
#        return response

    def __trainModel(self, verbose=False, trainRatio=.5):
        if verbose:
            analyzer = Analyzer(self.__model, self.__dataset, trainRatio)
            analyzer.start()
        self.__model.train(self.__dataset.trainSamples,
                           self.__dataset.trainResponses)
        if verbose:
            analyzer.stop()
            analyzer.analyze()
            print analyzer

    def __initModel(self, type):
        """Instanciate the choosen model.
        """
        mods = {
            self.MODEL_ANN: models.ANN,
            self.MODEL_KNEAREST: models.KNearest
            }
        Model = mods[type]
        return Model(len(self.__dataset.classes))
