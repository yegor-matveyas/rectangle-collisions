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
        self.rect_width = rect_height * 2

        self.rectangles: List[Rectangle] = []
        self.connections: List[Connection] = []

        self.active_rectangle: Rectangle = None

        # Current rectangle selected for connection
        self.first_connection_rectangle: Rectangle = None

        self.setWindowTitle("Collision of rectangles")
        self.setGeometry(50, 50, app_width, app_height)


    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            mouse_pos = event.pos()

            if self.is_rectangle_within_window(mouse_pos):
                colors = [r.color for r in self.rectangles]
                new_rect = Rectangle(
                    x=event.x(),
                    y=event.y(),
                    height=self.rect_height,
                    colors=colors,
                )
                if not self.has_intersections(new_rect):
                    self.rectangles.append(new_rect)
                    self.update()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if we are clicking on an existing rectangle
            for rect in self.rectangles:
                if rect.contains(event.pos()):
                    self.active_rectangle = rect
                    break
        elif event.button() == Qt.RightButton:
            # Start creating a connection between two rectangles or remove a connection
            clicked_connection = None
            for conn in self.connections:
                if conn.contains(event.pos()):
                    clicked_connection = conn
                    break
            if clicked_connection is not None:
                self.connections.remove(clicked_connection)
            else:
                clicked_on_rectangle = False
                for rect in self.rectangles:
                    if rect.contains(event.pos()):
                        clicked_on_rectangle = True
                        if not self.first_connection_rectangle:
                            # Start the connection
                            self.first_connection_rectangle = rect
                            rect.is_highlighted = True  # Highlight the selected rectangle
                        else:
                            # Complete the connection
                            new_conn = Connection(self.first_connection_rectangle, rect)
                            conn_exists = False
                            for conn in self.connections:
                                if (
                                    (
                                        conn.rect1 == new_conn.rect1
                                        and conn.rect2 == new_conn.rect2
                                    ) or (
                                        conn.rect1 == new_conn.rect2
                                        and conn.rect2 == new_conn.rect1
                                    )
                                ):
                                    conn_exists = True
                                    break
                            if not conn_exists:
                                self.connections.append(new_conn)

                                self.first_connection_rectangle.is_highlighted = False
                                self.first_connection_rectangle = None
                        break

                if not clicked_on_rectangle and self.first_connection_rectangle:
                    # Undo the first connection selection by clicking on empty space
                    self.first_connection_rectangle.is_highlighted = False
                    self.first_connection_rectangle = None

            self.update()


    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.active_rectangle = None


    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        print(f'connections {self.connections}')
        for conn in self.connections:
            conn.draw(painter)

        for rect in self.rectangles:
            rect.draw(painter)


    def is_rectangle_within_window(self, mouse_pos) -> bool:
        if (
            mouse_pos.x() - self.rect_width // 2 < 0
            or mouse_pos.x() + self.rect_width // 2 > self.width()
            or mouse_pos.y() - self.rect_height // 2 < 0
            or mouse_pos.y() + self.rect_height // 2 > self.height()
        ):
            return False
        return True


    def has_intersections(self, rectangle: Rectangle) -> bool:
        for r in self.rectangles:
            if rectangle != r and rectangle.intersects(r):
                return True
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(
        app_height=800,
        app_width=1200,
        rect_height=80,
    )
    window.show()
    sys.exit(app.exec_())
