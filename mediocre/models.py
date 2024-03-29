#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models.py
#
# Author: Yann KOETH
# Created: Wed Nov 26 23:31:05 2014 (+0100)
# Last-Updated: Thu Nov 27 15:35:42 2014 (+0100)
#           By: Yann KOETH
#     Update #: 306
#

import os

import cv2
import numpy as np
from numpy.linalg import norm


class StatModel(object):
    RESIZE = 16

    def __init__(self, nClass):
        self.classificationCount = nClass

    def __mergeContours(self, contours):
        """Merge all bounding boxes.
        Returns x, y, w, h.
        """
        x, y, x1, y1 = [], [], [], []
        for cnt in contours:
            pX, pY, pW, pH = cv2.boundingRect(cnt)
            x.append(pX)
            y.append(pY)
            x1.append(pX + pW)
            y1.append(pY + pH)
        bbX, bbY = min(x), min(y)
        bbW, bbH = max(x1) - bbX, max(y1) - bbY
        return bbX, bbY, bbW, bbH

    def _cropToFit(self, image):
        """Crop image to fit the bounding box.
        """
        clone = image.copy()
        contours, hierarchy = cv2.findContours(clone, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image
        x, y, w, h = self.__mergeContours(contours)
        return image[y: y + h, x: x + w]

    def _ratioResize(self, image):
        """Resize image to get an aspect ratio of 1:1 (square).
        """
        h, w = image.shape
        ratioSize = max(h, w)
        blank = np.zeros((ratioSize, ratioSize), np.uint8)
        x = (ratioSize - w) / 2.0
        y = (ratioSize - h) / 2.0
        blank[y: y + h, x: x + w] = image
        return blank

    def _deskew(self, img):
        affine_flags = cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR
        m = cv2.moments(img)
        if abs(m['mu02']) < 1e-2:
            return img.copy()
        skew = m['mu11'] / m['mu02']
        M = np.float32([[1, skew, -0.5 * self.RESIZE * skew], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (self.RESIZE, self.RESIZE), flags=affine_flags)
        return img

    def _hog(self, img):
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bin_n = 16
        bin = np.int32(bin_n * ang / (2 * np.pi))
        bin_cells = bin[:10, :10], bin[10:, :10], bin[:10, 10:], bin[10:, 10:]
        mag_cells = mag[:10, :10], mag[10:, :10], mag[:10, 10:], mag[10:, 10:]
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n)
                 for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)

        eps = 1e-7
        hist /= hist.sum() + eps
        hist = np.sqrt(hist)
        hist /= norm(hist) + eps
        return hist

    def preprocess(self, filename):
        """Pre-process image :
        - Convert To Grayscale
        - Gaussian Blur (remove noise)
        - Threshold (black and white image)
        - Crop to fit bounding box
        - Resize
        """
        self.input = cv2.imread(filename, cv2.CV_LOAD_IMAGE_COLOR)
        gray = cv2.cvtColor(self.input, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(src=gray, ksize=(5, 5), sigmaX=0)
        thresh = cv2.adaptiveThreshold(src=blur, maxValue=255,
                                       adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       thresholdType=cv2.THRESH_BINARY_INV,
                                       blockSize=31, C=2)
        cropped = self._cropToFit(thresh)
        squared = self._ratioResize(cropped)
        resized = cv2.resize(squared, (self.RESIZE, self.RESIZE))
        return resized

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


class ANN(StatModel):

    def __init__(self, nClass):
        super(ANN, self).__init__(nClass)
        self._model = cv2.ANN_MLP()
        self._samples = np.array([])
        self._responses = np.array([])

    def train(self, samples, responses, updateBase=False):
        if updateBase:
            if self._samples.any():
                samples = np.vstack([samples, self._samples])
                responses = self.unrollResponses(responses).reshape(-1, self.classificationCount)
                responses = np.vstack([responses, self._responses])
            else:
                return self._model
        else:
            responses = self.unrollResponses(responses).reshape(-1, self.classificationCount)

        sampleCount, sampleSize = samples.shape
        layers = np.int32([sampleSize, 16, self.classificationCount])
        self._model.create(layers, cv2.ANN_MLP_SIGMOID_SYM, 1, 1)

        maxIter = 2000
        epsilon = 0.002
        condition = cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS
        criteria = (condition, maxIter, epsilon)

        params = {
            'term_crit': criteria,
            'train_method': cv2.ANN_MLP_TRAIN_PARAMS_BACKPROP,
            'bp_dw_scale': 0.1,
            'bp_moment_scale': 0.1
        }
        self._samples = samples
        self._responses = np.float32(responses)
        self._model.train(inputs=samples, outputs=self._responses,
                          sampleWeights=None, params=params)

    def predict(self, samples):
        retval, outputs = self._model.predict(samples)
        return outputs.argmax(-1)


class KNN(StatModel):

    def __init__(self, nClass):
        super(KNN, self).__init__(nClass)
        self._model = cv2.KNearest()

    def train(self, samples, responses, updateBase=False):
        self._model.train(samples, responses, updateBase=updateBase)

    def predict(self, samples):
        _, results, _, _ = self._model.find_nearest(samples, k=6)
        return results.ravel()


class SVM(StatModel):
    BINS_NB = 16
    RESIZE = 20

    def __init__(self, nClass):
        super(SVM, self).__init__(nClass)
        self._model = cv2.SVM()

    def preprocess(self, filename):
        self.input = cv2.imread(filename, 0)
        self.input = cv2.adaptiveThreshold(src=self.input, maxValue=255,
                                           adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           thresholdType=cv2.THRESH_BINARY_INV,
                                           blockSize=11, C=2)
        self.input = self._ratioResize(self._cropToFit(self.input))
        self.input = cv2.resize(self.input, (self.RESIZE, self.RESIZE))
        self.input = self._deskew(self.input)
        self.input = self._hog(self.input)
        return np.float32(self.input)

    def train(self, samples, responses, updateBase=False):
        if updateBase:
            if self._samples.any():
                samples = np.vstack([samples, self._samples])
                responses = np.append(responses, self._responses)
            else:
                return self._model
        if updateBase:
            return self._model
        svm_params = dict(kernel_type=cv2.SVM_RBF, svm_type=cv2.SVM_C_SVC,
                          C=2.67, gamma=5.383)
        self._samples = samples
        self._responses = responses
        return self._model.train(samples, responses, params=svm_params)

    def predict(self, samples):
        predict = self._model.predict_all(samples)
        return predict.ravel()
