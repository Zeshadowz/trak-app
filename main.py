"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from service.youtube_service import YouTubeService
from service.spotify_service import SpotifyService
from service.audio_downloader_service import AudioMetadata


class TrakApp(QWidget):
    """Main application window for TRAK audio downloader."""

    def __init__(self):
        """Initialize the TRAK application."""
        super().__init__()
        self.artist = ""
        self.title = ""
        self.url = ""
        self.youtube_service = YouTubeService()
        self.spotify_service = SpotifyService()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("TRAK")
        self.setGeometry(300, 300, 600, 200)

        layout = QVBoxLayout()

        # URL input and search button
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Spotify or YouTube URL...")
        self.url_input.textChanged.connect(self.toggle_search_button)
        self.search_button = QPushButton("Search")
        self.search_button.setEnabled(False)
        self.search_button.clicked.connect(self.search_metadata)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.search_button)
        layout.addLayout(input_layout)

        # Info display
        self.info_label = QLabel("")
        layout.addWidget(self.info_label)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_file)
        self.download_button.setEnabled(False)
        layout.addWidget(self.download_button)

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
            metadata = self._extract_metadata_using_service()
            self.artist = metadata.artist
            self.title = metadata.title
            self.info_label.setText(
                f"Artist: {self.artist}\nTitle: {self.title}"
            )
            self.download_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(
                self, "Not Found",
                f"Could not extract metadata: {str(e)}"
            )
            self.info_label.setText("")
            self.download_button.setEnabled(False)

    def _extract_metadata_using_service(self) -> AudioMetadata:
        """
        Extract metadata using appropriate service.

        Returns:
            AudioMetadata containing artist and title.

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

    def download_file(self):
        """Download the audio file to a user-selected folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Download Folder"
        )
        if not folder:
            return

        try:
            if 'spotify' in self.url:
                self.spotify_service.download(self.url, folder)
            elif 'youtube' in self.url or 'youtu.be' in self.url:
                self.youtube_service.download(self.url, folder)
            else:
                raise ValueError("Unsupported URL")

            QMessageBox.information(self, "Success", "Download completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")

    @staticmethod
    def _is_valid_spotify_url(url: str) -> bool:
        """Check if URL is a valid Spotify track URL."""
        return 'spotify' in url and 'track' in url


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrakApp()
    window.show()
    sys.exit(app.exec_())

