import random
from typing import List

from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint


HIGHLIGHTED_BORDER_COLOR = Qt.black

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


    def move(self, x: int, y: int) -> None:
        self.rect.moveCenter(QPoint(x, y))


    def contains(self, point: QPoint) -> bool:
        return self.rect.contains(point)


    def intersects(self, rect: "Rectangle") -> bool:
        return self.rect.intersects(rect.rect)


    def center(self) -> QPoint:
        return self.rect.center()


    def draw(self, painter: QPainter) -> None:
        painter.setBrush(self.color)

        border_color = Qt.transparent
        if self.is_highlighted is True:
            border_color = HIGHLIGHTED_BORDER_COLOR

        painter.setPen(QPen(border_color, 2, Qt.SolidLine))
        painter.drawRect(self.rect)


    def get_color(self, colors: List[QColor] = []) -> QColor:
        while True:
            color: QColor = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            reserved_colors = colors + [HIGHLIGHTED_BORDER_COLOR]
            if color not in reserved_colors:
                return color
