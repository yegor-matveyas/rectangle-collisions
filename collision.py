from rectangle import Rectangle

class Collision:
    LR = "LR"
    RL = "RL"
    TB = "TB"
    BT = "BT"


    def __init__(
        self,
        rectangle: Rectangle,
        direction: str,
    ):
        self.rectangle = rectangle
        self.direction = direction
