import sys
from typing import List
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter

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

        self.setWindowTitle("Collision of rectangles")
        self.setGeometry(50, 50, app_width, app_height)


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
