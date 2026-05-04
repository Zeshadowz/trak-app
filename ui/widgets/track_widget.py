from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog, QMessageBox

from model import AudioMetadata
from ui.components.feedback.progress.linear_progress import ProgressWorker


class TrackWidget(QFrame):
    """Widget representing a single track with editable metadata and download."""

    def __init__(self, metadata: AudioMetadata, service, default_path: str = "", parent=None):
        """Initialize track widget."""
        super().__init__(parent)
        self.metadata = metadata
        self.service = service
        self.default_path = default_path
        self.download_folder = ""
        self.init_ui()

    def init_ui(self):
        """Initialize the track widget UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedHeight(95)
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
        if self.default_path:
            self.download_folder = self.default_path
        else:
            self.download_folder = QFileDialog.getExistingDirectory(
                self, "Choose Download Folder"
            )
            if not self.download_folder:
                return
            # Set as default
            settings = QSettings("TRAK", "Downloader")
            settings.setValue("default_download_path", self.download_folder)

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
