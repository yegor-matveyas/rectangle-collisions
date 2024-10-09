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
            for rectangle in self.rectangles:
                if rectangle.contains(mouse_pos):
                    if rectangle != self.active_rectangle:
                        self.reset_collisions()

                    self.active_rectangle = rectangle
                    self.offset = mouse_pos - rectangle.topLeft()
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


    def mouseMoveEvent(self, event) -> None:
        if self.active_rectangle:
            current_rect = self.active_rectangle.rect

            new_top_left: QPoint = event.pos() - self.offset
            new_top_left = self.limit_to_window(new_top_left)

            closest_rectangle = self.find_closest_rectangle(new_top_left)

            # Point to which movement is possible
            to: QPoint = None

            # No obstacles on the path from the active rectangle to the cursor point
            if (
                closest_rectangle is None
                and self.collision_y is None
                and self.collision_x is None
            ):
                self.active_rectangle.moveTo(new_top_left)

            # Presence of collision along the OX axis
            elif (
                closest_rectangle is None
                and self.collision_y is None
                and self.collision_x is not None
            ):
                collision_rect = self.collision_x.rectangle.rect
                is_in_y_range = (
                    collision_rect.top() - self.rect_height
                    <= new_top_left.y()
                    <= collision_rect.bottom()
                )

                if self.collision_x.direction == Collision.RL:
                    if (
                        new_top_left.x() < collision_rect.right()
                        and is_in_y_range
                    ):
                        to = QPoint(collision_rect.right(), new_top_left.y())
                        self.active_rectangle.moveTo(to)
                    else:
                        self.collision_x = None
                        to = new_top_left
                else:
                    if (
                        new_top_left.x() + self.rect_width > collision_rect.left()
                        and is_in_y_range
                    ):
                        to = QPoint(collision_rect.left() - self.rect_width, new_top_left.y())
                        self.active_rectangle.moveTo(to)
                    else:
                        self.collision_x = None
                        to = new_top_left

            # Presence of collision along the OY axis
            elif (
                closest_rectangle is None
                and self.collision_y is not None
                and self.collision_x is None
            ):
                collision_rect = self.collision_y.rectangle.rect
                is_in_x_range = (
                    collision_rect.left() - self.rect_width
                    <= new_top_left.x()
                    <= collision_rect.right()
                )

                if self.collision_y.direction == Collision.BT:
                    if (
                        new_top_left.y() < collision_rect.bottom()
                        and is_in_x_range
                    ):
                        to = QPoint(new_top_left.x(), collision_rect.bottom())
                    else:
                        self.collision_y = None
                        to = new_top_left
                else:
                    if (
                        new_top_left.y() + self.rect_height > collision_rect.top()
                        and is_in_x_range
                    ):
                        to = QPoint(new_top_left.x(), collision_rect.top() - self.rect_height)
                    else:
                        self.collision_y = None
                        to = new_top_left

            # Presence of only the closest rectangle
            elif (
                closest_rectangle is not None
                and self.collision_y is None
                and self.collision_x is None
            ):
                closest_rect = closest_rectangle.rect

                if closest_rect.right() - current_rect.left() <= 1:
                    self.collision_x = Collision(closest_rectangle, Collision.RL)
                elif current_rect.right() - closest_rect.left() <= 1:
                    self.collision_x = Collision(closest_rectangle, Collision.LR)
                elif closest_rect.bottom() - current_rect.top() <= 1:
                    self.collision_y = Collision(closest_rectangle, Collision.BT)
                elif current_rect.bottom() - closest_rect.top() <= 1:
                    self.collision_y = Collision(closest_rectangle, Collision.TB)

            # Presence of the closest rectangle and collision along the OX axis
            elif (
                closest_rectangle is not None
                and self.collision_y is None
                and self.collision_x is not None
            ):
                closest_rect = closest_rectangle.rect
                if closest_rect.bottom() - current_rect.top() <= 1:
                    self.collision_y = Collision(closest_rectangle, Collision.BT)
                elif current_rect.bottom() - closest_rect.top() <= 1:
                    self.collision_y = Collision(closest_rectangle, Collision.TB)

            # Presence of the closest rectangle and collision along the OY axis
            elif (
                closest_rectangle is not None
                and self.collision_y is not None
                and self.collision_x is None
            ):
                closest_rect = closest_rectangle.rect
                if closest_rect.right() - current_rect.left() <= 1:
                    self.collision_x = Collision(closest_rectangle, Collision.RL)
                elif current_rect.right() - closest_rect.left() <= 1:
                    self.collision_x = Collision(closest_rectangle, Collision.LR)

            # Presence of the both collisions
            elif (
                self.collision_y is not None
                and self.collision_x is not None
            ):
                rect_x = self.collision_x.rectangle.rect
                rect_y = self.collision_y.rectangle.rect

                # Collision handling in the upper left corner
                if (
                    self.collision_x.direction == Collision.RL
                    and self.collision_y.direction == Collision.BT
                ):
                    if (
                        new_top_left.x() > rect_x.right()
                        and new_top_left.y() > rect_y.bottom()
                    ):
                        to = new_top_left
                    elif (
                        new_top_left.x() < rect_x.right()
                        and new_top_left.y() > rect_y.bottom()
                    ):
                        to = QPoint(rect_x.right(), new_top_left.y())
                        if new_top_left.y() > rect_x.bottom():
                            self.reset_collisions()
                    elif (
                        new_top_left.x() > rect_x.right()
                        and new_top_left.y() < rect_y.bottom()
                    ):
                        to = QPoint(new_top_left.x(), rect_y.bottom())
                        if new_top_left.x() > rect_y.right():
                            self.reset_collisions()

                # Collision handling in the upper right corner
                elif (
                    self.collision_x.direction == Collision.LR
                    and self.collision_y.direction == Collision.BT
                ):
                    current_x = new_top_left.x() + self.rect_width
                    if (
                        current_x < rect_x.left()
                        and new_top_left.y() > rect_y.bottom()
                    ):
                        to = new_top_left
                    elif (
                        current_x > rect_x.left()
                        and new_top_left.y() > rect_y.bottom()
                    ):
                        to = QPoint(rect_x.left() - self.rect_width, new_top_left.y())
                        if new_top_left.y() > rect_x.bottom():
                            self.reset_collisions()
                    elif (
                        current_x < rect_x.left()
                        and new_top_left.y() < rect_y.bottom()
                    ):
                        to = QPoint(new_top_left.x(), rect_y.bottom())
                        if new_top_left.x() < rect_y.left():
                            self.reset_collisions()

                # Collision handling in the lower left corner
                elif (
                    self.collision_x.direction == Collision.RL
                    and self.collision_y.direction == Collision.TB
                ):
                    current_y = new_top_left.y() + self.rect_height
                    if (
                        new_top_left.x() > rect_x.right()
                        and current_y < rect_y.top()
                    ):
                        to = new_top_left
                    elif (
                        new_top_left.x() < rect_x.right()
                        and current_y < rect_y.top()
                    ):
                        to = QPoint(rect_x.right(), new_top_left.y())
                        if current_y < rect_x.top():
                            self.reset_collisions()
                    elif (
                        new_top_left.x() > rect_x.right()
                        and current_y > rect_y.top()
                    ):
                        to = QPoint(new_top_left.x(), rect_y.top() - self.rect_height)
                        if new_top_left.x() > rect_y.right():
                            self.reset_collisions()

                # Collision handling in the lower right corner
                elif (
                    self.collision_x.direction == Collision.LR
                    and self.collision_y.direction == Collision.TB
                ):
                    current_x = new_top_left.x() + self.rect_width
                    current_y = new_top_left.y() + self.rect_height
                    if (
                        current_x < rect_x.left()
                        and current_y < rect_y.top()
                    ):
                        to = new_top_left
                    elif (
                        current_x > rect_x.left()
                        and current_y < rect_y.top()
                    ):
                        to = QPoint(rect_x.left() - self.rect_width, new_top_left.y())
                        if current_y < rect_x.top():
                            self.reset_collisions()
                    elif (
                        current_x < rect_x.left()
                        and current_y > rect_y.top()
                    ):
                        to = QPoint(new_top_left.x(), rect_y.top() - self.rect_height)
                        if new_top_left.x() < rect_y.left():
                            self.reset_collisions()

            if to is not None:
                self.active_rectangle.moveTo(to)

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


    def find_closest_rectangle(self, top_left: QPoint) -> Rectangle:
        """ The nearest rectangle lying on the path
        from the active rectangle to the current cursor position. """

        current_top_left = self.active_rectangle.topLeft()

        area = QRect(
            min(current_top_left.x(), top_left.x()),
            min(current_top_left.y(), top_left.y()),
            abs(current_top_left.x() - top_left.x()) + self.rect_width,
            abs(current_top_left.y() - top_left.y()) + self.rect_height
        )

        min_distance = float('inf')

        closest_rectangle: Rectangle = None

        for rectangle in self.rectangles:
            if rectangle != self.active_rectangle:
                if (
                    (
                        self.collision_x is not None
                        and self.collision_x.rectangle == rectangle
                    ) or (
                        self.collision_y is not None
                        and self.collision_y.rectangle == rectangle
                    )
                ):
                    continue
                rect = rectangle.rect
                if area.intersects(rect):
                    distance = (
                        (area.topLeft().x() - rect.topLeft().x()) ** 2
                        + (area.topLeft().y() - rect.topLeft().y()) ** 2
                    ) ** 0.5

                    if distance < min_distance:
                        min_distance = distance
                        closest_rectangle = rectangle

        return closest_rectangle


    def reset_collisions(self) -> None:
        self.collision_x = None
        self.collision_y = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(
        app_height=800,
        app_width=1200,
        rect_height=80,
    )
    window.show()
    sys.exit(app.exec_())
