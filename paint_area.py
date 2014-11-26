#!/usr/bin/env python
# -*- coding: utf-8 -*-
# paint_area.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 21:35:40 2014 (+0100)
# Last-Updated: Wed Nov 26 23:15:29 2014 (+0100)
#           By: Yann KOETH
#     Update #: 1080
#

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsLineItem,
                             QGraphicsRectItem, QGraphicsItemGroup, QGraphicsScale)
from PyQt5.QtCore import QLineF, QPointF, QRectF, QSizeF
from PyQt5.QtGui import (QPen, QBrush, QCursor, QPainter, QPixmap, QFont, QColor,
                         QTransform, QVector3D)

class PaintArea(QGraphicsView):
    def __init__(self, width=10, parent=None):
        QGraphicsView.__init__(self, parent)
        self._frame = None
        self._instructions = None
        self.setScene(QGraphicsScene(self))
        self._items = self.scene().createItemGroup([])
        self.setMouseTracking(True)
        self.pen = QPen(Qt.black, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.painting = False
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.viewport().setCursor(self.getCursor())
        self.updateScene()

    def updateScene(self):
        if self._frame:
            self.scene().setBackgroundBrush(Qt.gray)
        oldCanvas = self.canvas()
        self.setSceneRect(QRectF(self.contentsRect()))
        self.centerScene()
        self.scaleItems(oldCanvas, self.canvas())

    def centerScene(self):
        self.centerFrame()
        self.centerInstructions()

    def scaleItems(self, oldCanvas, newCanvas):
        pass

    def canvas(self):
        if self._frame:
            return self._frame.rect()
        return QRectF(self.contentsRect())

    def fitInstructions(self):
        textSize = self._instructions.document().size()
        factor = min(self.canvas().size().width() / textSize.width(),
                     self.canvas().size().height() / textSize.height())
        f = self._instructions.font()
        f.setPointSizeF(f.pointSizeF() * factor)
        self._instructions.setFont(f)

    def centerInstructions(self):
        if self._instructions:
            self.fitInstructions()
            size = self.size()
            textSize = self._instructions.document().size()
            self._instructions.setPos((size.width() - textSize.width()) / 2.0,
                                      (size.height() - textSize.height()) / 2.0)

    def setInstructions(self, text):
        if self._instructions:
            self._instructions.setPlainText(text)
        else:
            self._instructions = self.scene().addText(text, QFont('Arial', 10, QFont.Bold))
            self._instructions.setZValue(-1)
            self._instructions.setDefaultTextColor(QColor(220, 220, 220))
        self._text = text
        self.centerInstructions()

    def setFrame(self, width, height):
        if self._frame:
            self._frame.setRect(0, 0, width, height)
        else:
            self.addFrame(QRectF(0, 0, width, height))
        self.centerScene()

    def addFrame(self, rect):
        self._frame = QGraphicsRectItem(rect)
        self._frame.setPen(QPen(Qt.NoPen))
        self._frame.setBrush(Qt.white)
        self._frame.setZValue(-2)
        self.scene().addItem(self._frame)

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
        if self._instructions:
            self.scene().removeItem(self._instructions)
        self.scene().render(painter,
                            source=self.canvas())
        if self._instructions:
            self.scene().addItem(self._instructions)

    def getLines(self):
        items = [item for item in self.scene().items() if item.group() == self._items]
        return self.canvas(), items

    def clear(self):
        for item in self.scene().items():
            if item.group() == self._items:
                self._items.removeFromGroup(item)

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

    def addLine(self, start, end):
        if start == end:
            delta = QPointF(.0001, 0)
            end = start - delta
        line = self.scene().addLine(QLineF(start, end), self.pen)
        self._items.addToGroup(line)

    def drawPoint(self, pos):
        delta = QPointF(.0001, 0)
        line = self.scene().addLine(QLineF(pos, pos - delta), self.pen)
        self._items.addToGroup(line)

    def mousePressEvent(self, event):
        self.start = QPointF(self.mapToScene(event.pos()))
        self.painting = True
        self.addLine(self.start, self.start)

    def mouseReleaseEvent(self, event):
        self.painting = False

    def mouseMoveEvent(self, event):
        pos = QPointF(self.mapToScene(event.pos()))
        if self.painting:
            self.addLine(self.start, pos)
            self.start = pos
