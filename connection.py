from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint

from rectangle import Rectangle

class Connection:
    def __init__(self, rect1: Rectangle, rect2: Rectangle):
        self.rect1 = rect1
        self.rect2 = rect2


    def draw(self, painter: QPainter):
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawLine(self.rect1.center(), self.rect2.center())


    def contains(self, point: QPoint):
        # Create a virtual rectangle for easier click detection on the line
        line_rect = QRect(self.rect1.center(), self.rect2.center()).normalized()
        line_rect = line_rect.adjusted(-5, -5, 5, 5)
        return line_rect.contains(point)
