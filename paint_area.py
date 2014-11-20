#!/usr/bin/env python
# -*- coding: utf-8 -*-
# paint_area.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 21:35:40 2014 (+0100)
# Last-Updated: Thu Nov 20 20:27:43 2014 (+0100)
#           By: Yann KOETH
#     Update #: 392
#

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsLineItem,
                             QGraphicsRectItem)
from PyQt5.QtCore import QLineF, QPointF, QRectF, QSizeF
from PyQt5.QtGui import QPen, QBrush, QCursor, QPainter, QPixmap

class PaintArea(QGraphicsView):
    def __init__(self, width=10, parent=None):
        QGraphicsView.__init__(self, parent)
        self._frame = None
        self.setScene(QGraphicsScene(self))
        self.setMouseTracking(True)
        self.pen = QPen(Qt.black, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.painting = False
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.viewport().setCursor(self.getCursor())
        self.updateScene()

    def updateScene(self):
        self.scene().setBackgroundBrush(Qt.gray)
        self.setSceneRect(QRectF(self.contentsRect()))
        self.centerFrame()

    def setFrame(self, width, height):
        if self._frame:
            self._frame.setRect(0, 0, width, height)
        else:
            self.addFrame(QRectF(0, 0, width, height))

    def addFrame(self, rect):
        self._frame = QGraphicsRectItem(rect)
        self._frame.setPen(QPen(Qt.NoPen))
        self._frame.setBrush(Qt.white)
        self.scene().addItem(self._frame)
        self.centerFrame()
        self.updateScene()

    def centerFrame(self):
        if self._frame:
            rect = self._frame.rect()
            size = self.contentsRect()
            factor = min((size.width() + 1) / rect.width(),
                         (size.height() + 1) / rect.height())
            w, h = rect.width() * factor, rect.height() * factor
            self._frame.setRect(size.x() + (size.width() - w) / 2.0,
                                size.y() + (size.height() - h) / 2.0,
                                w, h)

    def resizeEvent(self, event):
        self.updateScene()

    def setBrushSize(self, size):
        self.pen.setWidth(size)
        self.viewport().setCursor(self.getCursor())

    def render(self, painter):
        self.scene().render(painter,
                            source=self._frame.rect())

    def clear(self):
        rect = None
        if self._frame:
            rect = self._frame.rect()
        self.scene().clear()
        self.setScene(QGraphicsScene())
        if rect:
            self.addFrame(rect)

    def getCursor(self):
        antialiasing_margin = 1
        size = self.pen.width()
        pixmap = QPixmap(size + antialiasing_margin * 2,
                         size + antialiasing_margin * 2)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.drawEllipse(QRectF(QPointF(antialiasing_margin, antialiasing_margin),
                                   QSizeF(size, size)))
        painter.end()
        return QCursor(pixmap)

    def drawPoint(self, pos):
        delta = QPointF(.0001, 0)
        self.scene().addLine(QLineF(pos, pos - delta), self.pen)

    def mousePressEvent(self, event):
        self.start = QPointF(self.mapToScene(event.pos()))
        self.painting = True
        w = self.pen.width()
        self.drawPoint(self.start)

    def mouseReleaseEvent(self, event):
        self.painting = False

    def mouseMoveEvent(self, event):
        pos = QPointF(self.mapToScene(event.pos()))
        if self.painting:
            brush = QBrush(Qt.SolidPattern)
            self.scene().addLine(QLineF(self.start, pos), self.pen)
            self.start = pos
