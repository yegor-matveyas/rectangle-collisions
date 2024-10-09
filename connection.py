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


    def contains(self, point: QPoint, variance: int = 10 ):
        center1 = self.rect1.center()
        center2 = self.rect2.center()

        x0, y0 = point.x(), point.y()
        x1, y1 = center1.x(), center1.y()
        x2, y2 = center2.x(), center2.y()

        # Calculate the distance from the point to the line
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        distance = numerator / denominator if denominator != 0 else float('inf')

        if distance <= variance:
            if (
                min(x1, x2) <= x0 <= max(x1, x2)
                and min(y1, y2) <= y0 <= max(y1, y2)
            ):
                return True
        return False
