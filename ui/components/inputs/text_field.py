from collections.abc import Callable

from PyQt5.QtWidgets import QLineEdit


class TextField(QLineEdit):
    """Custom QLineEdit with placeholder text and styling."""

    def __init__(self, placeholder: str = "", bind: Callable | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007BFF;
            }
        """)
        if bind:
            self.textChanged.connect(bind)
