import random
from typing import List

from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint

class Rectangle:
    def __init__(self, x: int, y: int, height: int = 40, colors: List[QColor] = []):
        self.height = height
        self.width = self.height * 2
        self.rect = QRect(
            x - self.width // 2,
            y - height // 2,
            self.width,
            self.height,
        )

        # Checks if the rectangle is selected for the connection
        self.is_highlighted = False

        self.color = self.get_color(colors)


    def move(self, x, y) -> None:
        self.rect.moveCenter(QPoint(x, y))


    def contains(self, point) -> bool:
        return self.rect.contains(point)


    def center(self) -> QPoint:
        return self.rect.center()


    def draw(self, painter: QPainter) -> None:
        painter.setBrush(self.color)
        if self.is_highlighted is True:
            painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
        else:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawRect(self.rect)


    def get_color(self, colors: List[QColor] = []) -> QColor:
        while True:
            color: QColor = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            if color not in colors:
                return color
