from typing import List

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar, QScrollArea, QMessageBox

from model import AudioMetadata
from service import YouTubeService, SpotifyService
from ui.components.inputs.search_bar import SearchBar
from ui.dialog.modal import SettingsDialog
from ui.theme_manager import ThemeManager
from ui.widgets.trackCard import TrackCard


class TrakApp(QMainWindow):
    """Main application window for TRAK audio downloader."""

    def __init__(self, theme_manager: ThemeManager) -> None:

        """Initialize the TRAK application."""
        super().__init__()
        self._theme_manager = theme_manager

        self.settings = QSettings("TRAK", "Downloader")
        self.default_download_path = self.settings.value("default_download_path", "")
        self.url_input = None
        self.url = ""
        self.youtube_service = YouTubeService()
        self.spotify_service = SpotifyService()

        self.track_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setObjectName("AppWindows")
        self.setWindowTitle("TRAK")
        self.setGeometry(300, 300, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

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
        self.search_bar = SearchBar("Fügen Sie eine URL ein und drücken Sie die Eingabetaste...", self)
        self.search_bar.search_submitted.connect(self.search_metadata)
        self.search_bar.setMinimumWidth(400)
        layout.addWidget(self.search_bar)

        # Scrollable area for tracks
        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

    def search_metadata(self, url) -> None:
        """Search for metadata using the appropriate service."""
        if url is not None:
            self.url = url
        else:
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
            track_widget = TrackCard(metadata, service, self.default_download_path)
            self.scroll_layout.addWidget(track_widget)
            self.track_widgets.append(track_widget)

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.default_download_path = self.settings.value("default_download_path", "")
            # Update existing widgets
            for widget in self.track_widgets:
                widget.default_path = self.default_download_path
