from collections.abc import Callable

from PyQt6.QtWidgets import QLineEdit


class TextField(QLineEdit):
    """Custom QLineEdit with placeholder text and styling."""

    def __init__(self, placeholder: str = "", bind: Callable | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if bind:
            self.textChanged.connect(bind)
