from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox, \
    QFileDialog


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent=None):
        """Initialize settings dialog."""
        super().__init__(parent)
        self.settings = QSettings("TRAK", "Downloader")
        self.init_ui()

    def init_ui(self):
        """Initialize the settings UI."""
        self.setWindowTitle("Settings")
        self.setGeometry(400, 400, 400, 200)

        layout = QVBoxLayout()

        # Default download path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Default Download Path:"))
        self.path_input = QLineEdit()
        self.path_input.setText(self.settings.value("default_download_path", ""))
        path_layout.addWidget(self.path_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def browse_path(self):
        """Browse for download path."""
        path = QFileDialog.getExistingDirectory(self, "Choose Default Download Folder")
        if path:
            self.path_input.setText(path)

    def accept(self):
        """Save settings on accept."""
        self.settings.setValue("default_download_path", self.path_input.text())
        super().accept()