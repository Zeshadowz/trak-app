"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys
from typing import List

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QScrollArea, QToolBar, QAction, QDialog,
    QDialogButtonBox, QWidget
)

from service import SpotifyFlatService
from service.audio_downloader_service import AudioMetadata
from service.spotify_service import SpotifyService
from service.youtube_service import YouTubeService
from ui.components.inputs.action_button import ActionButton
from ui.components.inputs.text_field import TextField
from ui.widgets.track_widget import TrackWidget


# from dotenv import load_dotenv


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
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
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

class TrakApp(QMainWindow):
    """Main application window for TRAK audio downloader."""

    def __init__(self):
        """Initialize the TRAK application."""
        super().__init__()
        # load_dotenv()
        self.settings = QSettings("TRAK", "Downloader")
        self.default_download_path = self.settings.value("default_download_path", "")
        self.url_input = None
        self.url = ""
        self.youtube_service = YouTubeService()
        self.spotify_service = SpotifyService()
        self.spotify_flat_service = SpotifyFlatService()
        self.track_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("TRAK")
        self.setGeometry(300, 300, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Menu action (placeholder)
        menu_action = QAction("Menu", self)
        self.toolbar.addAction(menu_action)

        # Spacer
        self.toolbar.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_action)

        # URL input and search button
        input_layout = QHBoxLayout()
        self.url_input = TextField(
            "Enter Spotify or YouTube URL...",
            self.toggle_search_button
        )
        self.search_button = ActionButton(
            "Search",
            self.search_metadata,
            False
        )
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.search_button)
        layout.addLayout(input_layout)

        # Scrollable area for tracks
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

    def toggle_search_button(self):
        """Enable/disable search button based on URL input."""
        self.search_button.setEnabled(bool(self.url_input.text().strip()))

    def search_metadata(self):
        """Search for metadata using the appropriate service."""
        self.url = self.url_input.text().strip()
        if not self.url:
            return

        try:
            metadata_list = self._extract_metadata_using_service()
            self._display_tracks(metadata_list)
        except Exception as e:
            QMessageBox.warning(
                self, "Not Found",
                f"Could not extract metadata: {str(e)}"
            )

    def _extract_metadata_using_service(self) -> List[AudioMetadata]:
        """
        Extract metadata using appropriate service.

        Returns:
            List of AudioMetadata.

        Raises:
            ValueError: If URL is not supported or extraction fails.
        """
        if 'spotify' in self.url:
            return self.spotify_service.extract_metadata(self.url)
        elif 'youtube' in self.url or 'youtu.be' in self.url:
            return self.youtube_service.extract_metadata(self.url)
        else:
            msg = "Unsupported URL. Please provide a Spotify or YouTube URL."
            raise ValueError(msg)

    def _display_tracks(self, metadata_list: List[AudioMetadata]):
        """Display the list of tracks."""
        # Clear previous tracks
        for widget in self.track_widgets:
            widget.setParent(None)
        self.track_widgets = []

        # Determine service
        service = self.spotify_service if 'spotify' in self.url else self.youtube_service

        # Add new tracks
        for metadata in metadata_list:
            track_widget = TrackWidget(metadata, service, self.default_download_path)
            self.scroll_layout.addWidget(track_widget)
            self.track_widgets.append(track_widget)

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.default_download_path = self.settings.value("default_download_path", "")
            # Update existing widgets
            for widget in self.track_widgets:
                widget.default_path = self.default_download_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrakApp()
    window.show()
    sys.exit(app.exec_())
