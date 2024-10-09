from dataclasses import dataclass

from rectangle import Rectangle


@dataclass
class Collision:
    LR = "LR"
    RL = "RL"
    TB = "TB"
    BT = "BT"

    rectangle: Rectangle
    direction: str
