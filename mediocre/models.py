#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 23:31:05 2014 (+0100)
# Last-Updated: Wed Nov 26 23:31:45 2014 (+0100)
#           By: Yann KOETH
#     Update #: 2
#

import os
import string
import random
import numpy as np
import cv2


class AbstractStatModel(object):

    def __init__(self, nClass):
        self.classificationCount = nClass

    def load(self, filename):
        if not os.path.isfile(filename):
            raise OSError(2, 'File not found', filename)
        self._model.load(filename)

    def save(self, filename):
        self._model.save(filename)

    def unrollResponses(self, responses):
        """Convert array of form [2, 3] to
        [0, 0, 1, 0, 0, 0 1]
        """
        sampleCount = len(responses)
        newResponses = np.zeros(sampleCount * self.classificationCount, np.int32)
        responsesIndexes = np.int32(responses + np.arange(sampleCount) * self.classificationCount)
        newResponses[responsesIndexes] = 1
        return newResponses


class ANN(AbstractStatModel):

    def __init__(self, nClass):
        super(ANN, self).__init__(nClass)
        self._model = cv2.ANN_MLP()

    def train(self, samples, responses):
        sampleCount, sampleSize = samples.shape
        newResponses = self.unrollResponses(responses).reshape(-1, self.classificationCount)

        layers = np.int32([sampleSize, 16, self.classificationCount])
        self._model.create(layers, cv2.ANN_MLP_SIGMOID_SYM, 1, 1)

        maxIter = 2000 # Maximum number of iterations
        epsilon = 0.002 # Error threshold
        # Stop if maxIter or epsilon is reached
        condition = cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS
        criteria = (condition, maxIter, epsilon)

        params = {
            'term_crit': criteria,
            'train_method': cv2.ANN_MLP_TRAIN_PARAMS_BACKPROP,
            'bp_dw_scale': 0.1, # Stength of the weight gradient term
            'bp_moment_scale': 0.1 # Strength of the momentum term
            }

        self._model.train(inputs=samples,
                  outputs=np.float32(newResponses),
                  sampleWeights=None,
                  params=params)

    def predict(self, samples):
        retval, outputs = self._model.predict(samples)
        return outputs.argmax(-1)


class KNN(AbstractStatModel):

    def __init__(self, nClass):
        super(KNN, self).__init__(nClass)
        self._model = cv2.KNearest()

    def train(self, samples, responses):
        self._model.train(samples, responses)

    def predict(self, samples):
        retval, results, neighborResponses, dists = self._model.find_nearest(samples, k=10)
        return results.ravel()


class SVM(AbstractStatModel):
    BINS_NB = 4

    def __init__(self, nClass):
        super(SVM, self).__init__(nClass)
        self._model = cv2.SVM()

    def _deskew(self, img):
        m = cv2.moments(img)
        if abs(m['mu02']) < 1e-2:
            return img.copy()
        skew = m['mu11']/m['mu02']
        M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
        img = cv2.warpAffine(img,M,(SZ, SZ),flags=affine_flags)
        return img

    def _hog(self, img):
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bins = np.int32(bin_n*ang/(2*np.pi))
        bin_cells = bins[:10,:10], bins[10:,:10], bins[:10,10:], bins[10:,10:]
        mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)
        return hist

    def _before(self, samples):
        deskewed = [map(self._deskew, row) for row in samples]
        hogdata = [map(self._hog, row) for row in deskewed]
        samples = np.float32(hogdata).reshape(-1,64)
        responses = np.float32(np.repeat(np.arange(10), 250)[:, np.newaxis])
        return samples, responses

    def train(self, samples, responses):
        # samples, responses = self._before(samples)
        return self._model.train(samples, responses)

    def predict(self, samples, responses=None):
        # samples, responses = self._before(samples)
        responses = responses or np.array([])
        self._model.predict_all(samples, responses)
        return responses
