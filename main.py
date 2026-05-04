"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys
from typing import List
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from service import SpotifyFlatService
from service.youtube_service import YouTubeService
from service.spotify_service import SpotifyService
from service.audio_downloader_service import AudioMetadata
from ui.components.feedback.progress.linear_progress import ProgressWorker
# from dotenv import load_dotenv

from ui.components.inputs.action_button import ActionButton
from ui.components.inputs.text_field import TextField


class TrackWidget(QFrame):
    """Widget representing a single track with editable metadata and download."""

    def __init__(self, metadata: AudioMetadata, service, parent=None):
        """Initialize track widget."""
        super().__init__(parent)
        self.metadata = metadata
        self.service = service
        self.download_folder = ""
        self.init_ui()

    def init_ui(self):
        """Initialize the track widget UI."""
        self.setFrameStyle(QFrame.Box)
        layout = QGridLayout()

        # Artist label and input
        layout.addWidget(QLabel("Artist:"), 0, 0)
        self.artist_input = QLineEdit(self.metadata.artist)
        layout.addWidget(self.artist_input, 0, 1)

        # Title label and input
        layout.addWidget(QLabel("Title:"), 1, 0)
        self.title_input = QLineEdit(self.metadata.title)
        layout.addWidget(self.title_input, 1, 1)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_track)
        layout.addWidget(self.download_button, 0, 2, 2, 1)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid grey; "
            "min-height: 12px; max-height: 12px; "
            "border-radius: 5px; text-align: center; }"
        )
        layout.addWidget(self.progress_bar, 2, 0, 1, 3)

        self.setLayout(layout)

    def download_track(self):
        """Download the track."""
        if not self.download_folder:
            self.download_folder = QFileDialog.getExistingDirectory(
                self, "Choose Download Folder"
            )
            if not self.download_folder:
                return

        # Disable button and show progress
        self.download_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create worker
        self.worker = ProgressWorker(
            self.service,
            self.metadata.url,
            self.download_folder,
            'spotify' in self.metadata.url
        )
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.download_finished.connect(self._on_finished)
        self.worker.download_failed.connect(self._on_failed)
        self.worker.start()

    def _on_progress(self, progress: int):
        """Update progress bar."""
        self.progress_bar.setValue(progress)

    def _on_finished(self):
        """Handle download completion."""
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "Download completed!")
        self._reset()

    def _on_failed(self, error: str):
        """Handle download failure."""
        QMessageBox.critical(self, "Error", f"Download failed: {error}")
        self._reset()

    def _reset(self):
        """Reset UI after download."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(True)


class TrakApp(QWidget):
    """Main application window for TRAK audio downloader."""

    def __init__(self):
        """Initialize the TRAK application."""
        super().__init__()
        # load_dotenv()
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

        layout = QVBoxLayout()

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

        self.setLayout(layout)

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
            track_widget = TrackWidget(metadata, service)
            self.scroll_layout.addWidget(track_widget)
            self.track_widgets.append(track_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrakApp()
    window.show()
    sys.exit(app.exec_())
