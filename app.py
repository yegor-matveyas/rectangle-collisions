import sys
from typing import List
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from rectangle import Rectangle
from connection import Connection

class MainWindow(QWidget):
    def __init__(
        self,
        app_height: int = 800,
        app_width: int = 800,
        rect_height: int = 40,
    ):
        super().__init__()
        self.rect_height = rect_height

        self.rectangles: List[Rectangle] = []
        self.connections: List[Connection] = []

        self.active_rectangle: Rectangle = None

        self.setWindowTitle("Collision of rectangles")
        self.setGeometry(50, 50, app_width, app_height)


    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            new_rect = Rectangle(x=event.x(), y=event.y(), height=self.rect_height)
            self.rectangles.append(new_rect)
            self.update()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if we are clicking on an existing rectangle
            for rect in self.rectangles:
                if rect.contains(event.pos()):
                    self.active_rectangle = rect
                    break


    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.active_rectangle = None


    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        for conn in self.connections:
            conn.draw(painter)

        for rect in self.rectangles:
            rect.draw(painter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(
        app_height=800,
        app_width=1200,
        rect_height=80,
    )
    window.show()
    sys.exit(app.exec_())
