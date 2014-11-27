#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ocr.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:47:17 2014 (+0100)
# Last-Updated: Thu Nov 27 14:56:07 2014 (+0100)
#           By: Yann KOETH
#     Update #: 374
#

import hashlib
import os
import pickle

import numpy as np

from analyzer import Analyzer
from mediocre import models
from mediocre.dataset import DatasetItem


class ModelException(Exception):
    pass


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
            file = open(os.path.join(folder, filename), 'wb')
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
                file.close()
                self.__model.train(samples, responses)
        else:
            self.__model = None
            raise ModelException()

    def trainModel(self, dataset, classes, type=MODEL_ANN, trainRatio=.5,
                   maxPerClass=100, errorsIteration=0, log=None):
        self.__dataset = dataset
        self.__classes = classes
        self.__type = type
        if log:
            log("Pre-processing...\n")
        self.__model = self.__initModel(type)
        self.__dataset.preprocess(classes, maxPerClass, trainRatio,
                                  self.__model.preprocess)
        self.__trainModel(trainRatio=trainRatio, errorsIteration=errorsIteration, log=log)

    def charFromImage(self, image):
        item = DatasetItem(self.__model.preprocess)
        item.loadFromImage(image)
        return self.__charFromDatasetItem(item).value

    def charFromFile(self, filename):
        item = DatasetItem(self.__model.preprocess)
        item.loadFromFile(filename)
        return self.__charFromDatasetItem(item)

    def __charFromDatasetItem(self, item):
        sample = np.array([item.sample])
        response = self.__classes[int(self.__model.predict(sample)[0])]
        return response

    def __stackArrays(self, items):
        """Create samples and responses arrays.
        """
        if not items:
            return (np.array([]), np.array([]))
        samples = []
        responses = []
        for item in items:
            responses.append(self.classes.index(item.cl))
            samples.append(item.sample)
        return (np.vstack(samples), np.array(responses))

    def __injectErrors(self, samples, responses):
        predict = self.__model.predict(samples)
        errorSamples, errorResponses = [], []
        goodSamples, goodResponses = [], []
        for i, error in enumerate(predict != responses):
            if error:
                errorSamples.append(samples[i])
                errorResponses.append(responses[i])
            else:
                goodSamples.append(samples[i])
                goodResponses.append(responses[i])
        if errorSamples:
            self.__dataset.trainSamples = np.vstack([self.__dataset.trainSamples, errorSamples])
            self.__dataset.trainResponses = np.append(self.__dataset.trainResponses, errorResponses)
            errorSamples = np.vstack(errorSamples)
            errorResponses = np.array(errorResponses)
            self.__model.train(errorSamples,
                               errorResponses, True)
        if goodSamples:
            goodSamples = np.vstack(goodSamples)
        goodResponses = np.array(goodResponses)
        return goodSamples, goodResponses

    def __trainModel(self, trainRatio=.5, errorsIteration=0, log=None):
        if log:
            analyzer = Analyzer(self.__model, self.__dataset, trainRatio)
            analyzer.start()
        self.__model.train(self.__dataset.trainSamples,
                           self.__dataset.trainResponses)
        samples, responses = self.__dataset.testSamples, self.__dataset.testResponses
        i = 0
        while responses.any() and i < errorsIteration:
            samples, responses = self.__injectErrors(samples, responses)
            i += 1
        self.__dataset.testSamples = samples
        self.__dataset.testResponses = responses
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
