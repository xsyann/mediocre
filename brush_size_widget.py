# brush_size_widget.py
#
# Author: Yann KOETH
# Created: Tue Nov 11 21:51:54 2014 (+0100)
# Last-Updated: Fri Nov 14 20:37:24 2014 (+0100)
#           By: Yann KOETH
#     Update #: 426
#

from PyQt5.QtCore import Qt, QSize, QRectF, QEvent, QRect, QPointF, pyqtSignal
from PyQt5.QtGui import (QPixmap, QIcon, QPainter, QPen, QBrush, QKeySequence,
                         QPainterPath)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QToolButton, QMenu,
                             QWidgetAction, QListWidget, QListWidgetItem,
                             QLabel)

class BrushSizeWidget(QToolButton):

    ICON_SIZE = (12, 12)
    BUTTON_SIZE = (40, 30)
    ITEM_SIZE = (100, 20)
    MARGIN = 7

    brushSizeChanged = pyqtSignal(int)

    def __init__(self, size=10, min_size=1, max_size=50, parent=None):
        super(BrushSizeWidget, self).__init__(parent)
        self._size = size
        self._min_size = min_size
        self._max_size = max_size
        self.initUI()
        self.connectUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.menu = QMenu(self)
        self.setMenu(self.menu)
        self.setFixedSize(*self.BUTTON_SIZE)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.listWidget = self.createListWidget()
        self.listWidget.installEventFilter(self)
        action = QWidgetAction(self)
        action.setDefaultWidget(self.listWidget)
        self.menu.addAction(action)
        self.updateIcon()

    def connectUI(self):
       self.listWidget.itemClicked.connect(self.selectSize)

    def selectSize(self, item):
        self.menu.close()
        self._size = item.data(Qt.UserRole)
        self.updateIcon()
        self.brushSizeChanged.emit(self._size)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress and \
        event.matches(QKeySequence.InsertParagraphSeparator):
            self.selectSize(self.listWidget.currentItem())
        return super(BrushSizeWidget, self).eventFilter(watched, event)

    def createListWidget(self):
        listWidget = QListWidget()
        w, h = self.ITEM_SIZE
        scroll_size = 16
        listWidget.setFixedWidth(w + scroll_size)
        listWidget.setAttribute(Qt.WA_MacShowFocusRect, False);
        for x in xrange(self._min_size, self._max_size):
            h = max(x + self.MARGIN * 2.0, h)
            pixmap = QPixmap(w, h)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            center = h / 2.0
            painter.fillRect(QRectF(self.MARGIN, center - x / 2.0,
                                    w - self.MARGIN * 2.0, x), Qt.black)
            painter.end()
            label = QLabel()
            label.setPixmap(pixmap)
            item = QListWidgetItem(listWidget)
            item.setSizeHint(QSize(w, h))
            item.setData(Qt.UserRole, x)
            listWidget.addItem(item)
            listWidget.setItemWidget(item, label)
            if self._size == x:
                listWidget.setCurrentItem(item)
        return listWidget

    def updateIcon(self):
        self.setText(str(self._size))
        w, h = self.ICON_SIZE
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.black)
        preview_size = min(w - 1, self._size)
        center = (w - preview_size) / 2.0
        painter.drawEllipse(QRect(center, center, preview_size, preview_size))
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(w, h))


