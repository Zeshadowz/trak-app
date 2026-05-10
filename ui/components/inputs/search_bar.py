from typing import Callable

from PyQt6.QtCore import QSize, pyqtSignal, QEvent, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QPushButton, QLineEdit

from ui.utils import get_icon, Separator


class IconMenu(QPushButton):

    def __init__(self,
                 icon: str,
                 active: bool = True,
                 on_click: Callable | None = None,
                 tooltip: str = None,
                 clickable: bool = True,
                 parent=None):
        super().__init__(parent)

        self.active = active
        self.icon = icon
        self.on_click = on_click
        self.tooltip = tooltip
        self.clickable = clickable
        self.installEventFilter(self)
        self.setup_ui()

        if on_click is not None:
            self.clicked.connect(on_click)

    def setup_ui(self):
        self.setEnabled(self.active)
        self.setIcon(get_icon(f"{self.icon}"))  # or use custom icon
        self.setIconSize(QSize(20, 20))
        self.setFixedSize(28, 28)
        self.setToolTip(self.tooltip)
        self.setProperty("class", "icon_menu")
        self.setStyleSheet(
            """
            QPushButton.icon_menu, QPushButton.icon_menu:hover {
                background: transparent;
                border: none;
            }
            """
        )

    def eventFilter(self, obj, e):
        if self.clickable:
            if e.type() == QEvent.Type.Enter:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                return True
            elif e.type() == QEvent.Type.Leave:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return True
            return super().eventFilter(obj, e)
        return False


class SearchBar(QWidget):
    # Define a signal that sends the value of the QlineEdit
    search_submitted = pyqtSignal(str)  # Emitted when Enter is pressed or Search is clicked
    download_clicked = pyqtSignal()  # Example action

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__()
        self.clear_button = None
        self.left_icon = None
        self.text_field = None
        self.search_button = None

        self.placeholder = placeholder
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 8, 25, 8)
        layout.setSpacing(12)

        # Main container with rounded background
        container = QFrame()
        container.setObjectName("SearchContainer")
        container.setStyleSheet("""
            QFrame#SearchContainer {
                background: transparent;
                border: 1px solid #CCC;
                border-radius: 5px;
                padding: 4px;
            }
            QFrame#SearchContainer:hover {
                border: 1px solid #F09400;
            }
        """)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        # Left Icon (URL icon)
        self.left_icon = IconMenu("link_40dp_F09400.svg", clickable=False)

        # Search Input
        self.text_field = QLineEdit()
        self.setStyleSheet(
            """
                QLineEdit {
                    background: transparent;
                    border: none;
                    color: {text};
                    font-size: 14px;
                    padding: 4px 8px;
                }
                
                QLineEdit:focus {
                    outline: none;
                }
            """
        )
        self.text_field.setPlaceholderText(self.placeholder)
        self.text_field.setClearButtonEnabled(False)
        self.text_field.textChanged.connect(self.update_button_state)
        self.text_field.returnPressed.connect(self._on_return_search)

        # Right side actions
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        ## Clear the input
        self.clear_button = IconMenu("close_40dp_F09400.svg", False,
                                     self.clear, None)
        right_layout.addWidget(self.clear_button)

        # Separator
        right_layout.addWidget(Separator())

        # Search Button
        self.search_button = IconMenu(
            "search_40dp_F09400.svg", False, self._on_return_search)
        right_layout.addWidget(self.search_button)

        # Assemble
        container_layout.addWidget(self.left_icon)
        container_layout.addWidget(self.text_field, 1)
        container_layout.addWidget(right_widget)

        layout.addWidget(container)

    def _on_return_search(self):
        # Sent the signal with the actual value of the QLineEdit
        text = self.text_field.text().strip()
        if text:
            print("Url: " + text)
            self.search_submitted.emit(text)

    def text(self) -> str:
        return self.text_field.text()

    def clear(self) -> None:
        self.text_field.clear()

    def update_button_state(self):
        """Enable/disable the clean and search button based on the input text."""
        state = bool(self.text_field.text().strip())
        self.search_button.setEnabled(state)
        self.clear_button.setEnabled(state)
