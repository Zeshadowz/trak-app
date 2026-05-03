"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QMessageBox, QProgressBar
)

from service import SpotifyFlatService
from service.youtube_service import YouTubeService
from service.spotify_service import SpotifyService
from service.audio_downloader_service import AudioMetadata
from ui.components.feedback.progress.linear_progress import ProgressWorker
# from dotenv import load_dotenv

from ui.components.inputs.action_button import ActionButton
from ui.components.inputs.text_field import TextField


class TrakApp(QWidget):
    """Main application window for TRAK audio downloader."""

    def __init__(self):
        """Initialize the TRAK application."""
        super().__init__()
        # load_dotenv()
        self.url_input = None
        self.artist = ""
        self.title = ""
        self.url = ""
        self.youtube_service = YouTubeService()
        self.spotify_service = SpotifyService()
        self.spotify_flat_service = SpotifyFlatService()
        self.download_worker = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("TRAK")
        self.setGeometry(300, 300, 600, 250)

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

        # Info display
        self.info_label = QLabel("Metadata")
        layout.addWidget(self.info_label)

        # Download button
        self.download_button = ActionButton(
            "Download",
            self.download_file,
            False
        )
        layout.addWidget(self.download_button)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.text()
        self.progress_bar.setVisible(True)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid grey; "
            "min-height: 12px;"
            "max-height: 12px;"
            "border-radius: 5px; text-align: center; }"
        )
        layout.addWidget(self.progress_bar)

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
            # return self.spotify_flat_service.extract_metadata(self.url)
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
            # Disable buttons during download
            self.download_button.setEnabled(False)
            self.search_button.setEnabled(False)
            self.url_input.setEnabled(False)

            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Determine which service to use
            if 'spotify' in self.url:
                service = self.spotify_service
            elif 'youtube' in self.url or 'youtu.be' in self.url:
                service = self.youtube_service
            else:
                raise ValueError("Unsupported URL")

            # Create and start download worker

            self.download_worker = ProgressWorker(
                service,
                self.url,
                folder,
                'spotify' in self.url
            )
            self.download_worker.progress_updated.connect(
                self._on_download_progress
            )
            self.download_worker.download_finished.connect(
                self._on_download_finished
            )
            self.download_worker.download_failed.connect(
                self._on_download_failed
            )
            self.download_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")
            self.progress_bar.setVisible(False)
            self.download_button.setEnabled(True)
            self.search_button.setEnabled(True)
            self.url_input.setEnabled(True)

    def _on_download_progress(self, progress: int):
        """
        Update progress bar.

        Args:
            progress: Progress percentage (0-100).
        """
        self.progress_bar.setValue(progress)

    def _on_download_finished(self):
        """Handle download completion."""
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "Download completed!")
        self._reset_download_state()

    def _on_download_failed(self, error_message: str):
        """
        Handle download failure.

        Args:
            error_message: The error message.
        """
        QMessageBox.critical(self, "Error", f"Download failed: {error_message}")
        self._reset_download_state()

    def _reset_download_state(self):
        """Reset UI after download completes or fails."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.url_input.setEnabled(True)

    @staticmethod
    def _is_valid_spotify_url(url: str) -> bool:
        """Check if URL is a valid Spotify track URL."""
        return 'spotify' in url and 'track' in url


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrakApp()
    window.show()
    sys.exit(app.exec_())
