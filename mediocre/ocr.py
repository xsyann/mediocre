#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ocr.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:47:17 2014 (+0100)
# Last-Updated: Thu Nov 27 07:57:01 2014 (+0100)
#           By: Yann KOETH
#     Update #: 208
#

import os
import sys
import hashlib
import pickle
import numpy as np
from analyzer import Analyzer

from mediocre import models
from mediocre.dataset import DatasetItem

class OCR(object):
    MODEL_ANN = 0
    MODEL_KNN = 1
    MODEL_SVM = 2

    def getModelFilename(self, classes, type):
        values = [cl.value for cl in classes]
        values.sort()
        m = hashlib.md5(''.join(values))
        return "{0}_{1}.yml".format(m.hexdigest(), type)

    def saveModel(self):
        root = os.path.dirname(os.path.dirname(__file__))
        folder = os.path.join(root, "models")
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = self.getModelFilename(self.__classes, self.__type)
        if not self.__type == self.MODEL_KNN:
            self.__model.save(os.path.join(folder, filename))
        else:
            arr = (self.__dataset.trainSamples,
                   self.__dataset.trainResponses)
            print arr
            file = open(os.path.join(folder, filename), 'wb')
            print os.path.join(folder, filename)
            pickle.dump(arr, file)
            file.close()

    def loadModel(self, classes, folder, type=MODEL_ANN):
        self.__classes = classes
        filename = self.getModelFilename(classes, type)
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            self.__model = self.__initModel(type)
            if not type == self.MODEL_KNN:
                self.__model.load(path)
            else:
                file = open(path, 'rb')
                samples, responses = pickle.load(file)
                samples = np.array(samples.tolist())
                responses = np.array(responses.tolist())
                file.close()
                self.__model.train(samples, responses)
        else:
            self.__model = None
            print "No model found"

    def trainModel(self, dataset, classes, type=MODEL_ANN, trainRatio=.5,
                   maxPerClass=100, log=None):
        self.__dataset = dataset
        self.__classes = classes
        self.__type = type
        if log:
            log("Pre-processing...\n")
        self.__model = self.__initModel(type)
        self.__dataset.preprocess(classes, maxPerClass, trainRatio,
                                  self.__model.preprocess)
        self.__trainModel(trainRatio=trainRatio, log=log)

    def charFromImage(self, image):
        item = DatasetItem(self.__model.preprocess)
        item.loadFromImage(image)
        return self.__charFromDatasetItem(item).value

    def charFromFile(self, filename):
        item = dataset.DatasetItem(self.__model.preprocess)
        item.loadFromFile(filename)
        return self.__charFromDatasetItem(item)

    def __charFromDatasetItem(self, item):
        sample = np.array([item.sample])
        response = self.__classes[int(self.__model.predict(sample)[0])]
        return response

    def __trainModel(self, trainRatio=.5, log=None):
        if log:
            analyzer = Analyzer(self.__model, self.__dataset, trainRatio)
            analyzer.start()
        self.__model.train(self.__dataset.trainSamples,
                           self.__dataset.trainResponses)
        if log:
            analyzer.stop()
            analyzer.analyze()
            log(str(analyzer))

    def __initModel(self, type):
        """Instanciate the choosen model.
        """
        mods = {
            self.MODEL_ANN: models.ANN,
            self.MODEL_KNN: models.KNN,
            self.MODEL_SVM: models.SVM
        }
        Model = mods[type]
        return Model(len(self.__classes))
