#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ocr.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 17:47:17 2014 (+0100)
# Last-Updated: Wed Nov 26 23:10:02 2014 (+0100)
#           By: Yann KOETH
#     Update #: 10
#

class OCR(object):

    MODEL_ANN = 0
    MODEL_KNEAREST = 1

    def saveModel(self, filename):
        self.__model.save(filename)

#    def loadModel(self, filename, type=MODEL_ANN):
#        folders = OCR.generateFolderList(flags=flags)
#        self.__dataset = dataset.Dataset(folders)
#        self.__model = self.__initModel(type)
#        self.__model.load(filename)

    def trainModel(self, dataset, classes, type=MODEL_ANN, trainRatio=.5,
                   maxPerClass=100, verbose=True):
        #folders = OCR.generateFolderList(flags=flags)
        self.__dataset = dataset
        self.__classes = classes
    #    self.__dataset.maxPerClass = maxPerClass
        self.__dataset.preprocess(classes, maxPerClass, trainRatio)
#        self.__model = self.__initModel(type)
#        self.__trainModel(verbose=verbose, trainRatio=trainRatio)

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
#        if verbose:
#            analyzer = Analyzer(self.__model, self.__dataset, trainRatio)
#            analyzer.start()
 #       if self.__dataset.trainSampleCount > 0:
        self.__model.train(self.__dataset.trainSamples, self.__dataset.trainResponses)
        #if verbose:
        #    analyzer.stop()
        #    analyzer.analyze()
        #    print analyzer

    def __initModel(self, type):
        """Instanciate the choosen model.
        Be sure that MODEL constants are in the same order
        as the models array.
        """
        models = [mod.ANN, mod.KNearest]
        Model = models[type]
        return Model(self.__dataset.classificationCount)
