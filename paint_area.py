#!/usr/bin/env python
# -*- coding: utf-8 -*-
# paint_area.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 21:35:40 2014 (+0100)
# Last-Updated: Wed Nov 12 17:10:55 2014 (+0100)
#           By: Yann KOETH
#     Update #: 32
#

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsLineItem)
from PyQt5.QtCore import QLineF, QPointF, QRectF, QSizeF
from PyQt5.QtGui import QPen, QBrush, QCursor, QPainter, QPixmap

class PaintArea(QGraphicsView):
    def __init__(self, width=10, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setScene(QGraphicsScene(self))
        self.setSceneRect(QRectF(self.viewport().rect()))
        self.setMouseTracking(True)
        self.pen = QPen(Qt.black, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.painting = False
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.viewport().setCursor(QCursor(Qt.BlankCursor))
        self._cursor = self.scene().addEllipse(0, 0, 0, 0)

    def setBrushSize(self, size):
        self.pen.setWidth(size)

    def updateCursor(self, pos):
        w = self.pen.width()
        self._cursor.setRect(pos.x() - w / 2.0, pos.y() - w / 2.0, w, w)

    def drawPoint(self, pos):
        delta = QPointF(.001, 0)
        self.scene().addLine(QLineF(pos, pos - delta), self.pen)

    def leaveEvent(self, event):
        self._cursor.setRect(0, 0, 0, 0)
        return super(PaintArea, self).leaveEvent(event)

    def mousePressEvent(self, event):
        self.start = QPointF(self.mapToScene(event.pos()))
        self.painting = True
        w = self.pen.width()
        self.drawPoint(self.start)

    def mouseReleaseEvent(self, event):
        self.painting = False

    def mouseMoveEvent(self, event):
        pos = QPointF(self.mapToScene(event.pos()))
        self.updateCursor(pos)
        if self.painting:
            brush = QBrush(Qt.SolidPattern)
            self.scene().addLine(QLineF(self.start, pos), self.pen)
            self.start = pos
