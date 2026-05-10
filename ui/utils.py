import os

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFrame


def get_icon(filename: str) -> QIcon:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "icons", filename)
    return QIcon(icon_path)


class Separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setStyleSheet("""
            background-color: #CCC;
            border: none;
            max-width: 1px;
            min-width: 1px;
        """)
