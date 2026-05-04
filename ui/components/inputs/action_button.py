from collections.abc import Callable

from PyQt6.QtWidgets import QPushButton


class ActionButton(QPushButton):
    """
    Custom QPushButton with additional functionality for enabling/disabling.

    Args:
    - label: The text to display on the button.
    - on_click: Optional callable to connect to the clicked signal.
    - enabled: Whether the button is enabled (Defaults to True).
    - parent: The parent widget (optional).
    """

    def __init__(self, label: str, on_click: Callable | None = None, enabled: bool = True, parent=None) -> None:
        """Initialize the ActionButton."""
        super().__init__(label, parent)
        if on_click is not None:
            self.clicked.connect(on_click)
        self.setEnabled(enabled)

        self.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: rgba(0, 0, 0, 0);
                color: rgba(0, 0, 0, 0);
            }
            QPushButton:hover {
                background-color: #0055FF;
            }
            QPushButton:pressed {
                border: 2px solid #0056b3;
            }
        """)

    def enable(self):
        """Enable the button."""
        self.setEnabled(True)

    def disable(self):
        """Disable the button."""
        self.setEnabled(False)

    def rebind(self, on_click: Callable) -> None:
        """
        Disconnect all existing click handlers and bind a new click handler.
        Useful when the same button is reused across different contexts and needs to trigger different actions.

        Rebind the button to the clicked signal.
        :param on_click:
        :return:
        """
        try:
            self.clicked.disconnect()
        except RuntimeError:
            pass  # no connections to disconnect
        self.clicked.connect(on_click)
