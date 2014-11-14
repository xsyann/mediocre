#!/usr/bin/env python
# -*- coding: utf-8 -*-
# paint_area.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 21:35:40 2014 (+0100)
# Last-Updated: Fri Nov 14 18:32:27 2014 (+0100)
#           By: Yann KOETH
#     Update #: 110
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
        self.viewport().setCursor(self.getCursor())

    def setFixedSize(self, w, h):
        self.setSceneRect(QRectF(0, 0, 1, 1))
        super(PaintArea, self).setFixedSize(w, h)

    def setBrushSize(self, size):
        self.pen.setWidth(size)
        self.viewport().setCursor(self.getCursor())

    def render(self, painter):
        self.scene().render(painter)

    def clear(self):
        self.scene().clear()

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
