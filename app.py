import sys
from typing import List
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QPoint, QRect

from rectangle import Rectangle
from connection import Connection
from collision import Collision

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

        self.offset: QPoint = QPoint()
        self.prev_position: QPoint = None
        self.collision_x: Collision = None
        self.collision_y: Collision = None

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
        mouse_pos = event.pos()
        if event.button() == Qt.LeftButton:
            # Check if we are clicking on an existing rectangle
            for rect in self.rectangles:
                if rect.contains(mouse_pos):
                    self.active_rectangle = rect
                    self.offset = mouse_pos - rect.topLeft()
                    break
        elif event.button() == Qt.RightButton:
            # Start creating a connection between two rectangles or remove a connection
            clicked_connection = None
            for conn in self.connections:
                if conn.contains(mouse_pos):
                    clicked_connection = conn
                    break
            if clicked_connection is not None:
                self.connections.remove(clicked_connection)
            else:
                clicked_on_rectangle = False
                for rect in self.rectangles:
                    if rect.contains(mouse_pos):
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


    def mouseMoveEvent(self, event):
        if self.active_rectangle:
            # self.prev_position = self.active_rectangle.topLeft()

            new_top_left: QPoint = event.pos() - self.offset
            new_top_left = self.limit_to_window(new_top_left)

            closest_rectangle = self.find_closest_rectangle(new_top_left)
            if closest_rectangle is not None:
                current_top_left: QPoint = self.active_rectangle.topLeft()
                closest_top_left: QPoint = closest_rectangle.topLeft()
                if (
                    new_top_left.x() < closest_top_left.x()
                    and closest_top_left.x() < current_top_left.x()
                ):
                    self.collision_x = Collision(closest_rectangle, Collision.RL)
                elif (
                    current_top_left.x() < closest_top_left.x()
                    and closest_top_left.x() < new_top_left.x()
                ):
                    self.collision_x = Collision(closest_rectangle, Collision.LR)
                elif (
                    new_top_left.y() < closest_top_left.y()
                    and closest_top_left.y() < current_top_left.y()
                ):
                    self.collision_y = Collision(closest_rectangle, Collision.BT)
                elif (
                    current_top_left.y() < closest_top_left.y()
                    and closest_top_left.y() < new_top_left.y()
                ):
                    self.collision_x = Collision(closest_rectangle, Collision.TB)
                else:
                    self.collision_x = None
                    self.collision_y = None
            else:
                # No obstacles in the way
                self.active_rectangle.moveTo(new_top_left)
            self.update()


    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.active_rectangle = None


    def paintEvent(self, event) -> None:
        painter = QPainter(self)

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


    def limit_to_window(self, pos: QPoint) -> QPoint:
        # Prevents going outside the window in the OY axis
        if pos.y() < 0:
            pos.setY(0)
        elif pos.y() + self.rect_height > self.height():
            pos.setY(self.height() - self.rect_height)

        # Prevents going outside the window in the OX axis
        if pos.x() < 0:
            pos.setX(0)
        elif pos.x() + self.rect_width > self.width():
            pos.setX(self.width() - self.rect_width)

        return pos


    def find_closest_rectangle(self, new_top_left: QPoint) -> Rectangle:
        current_top_left = self.active_rectangle.topLeft()

        area = QRect(
            min(current_top_left.x(), new_top_left.x()),
            min(current_top_left.y(), new_top_left.y()),
            abs(current_top_left.x() - new_top_left.x()) + self.rect_width,
            abs(current_top_left.y() - new_top_left.y()) + self.rect_height
        )

        closest_rectangle: Rectangle = None
        min_distance = float('inf')

        for rectangle in self.rectangles:
            if rectangle != self.active_rectangle:
                rect: QRect = rectangle.rect
                if area.intersects(rect):
                    distance = (
                        (area.topLeft().x() - rect.topLeft().x()) ** 2
                        + (area.topLeft().y() - rect.topLeft().y()) ** 2
                    ) ** 0.5

                    if distance < min_distance:
                        min_distance = distance
                        closest_rectangle = rect

        return closest_rectangle


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(
        app_height=800,
        app_width=1200,
        rect_height=80,
    )
    window.show()
    sys.exit(app.exec_())
