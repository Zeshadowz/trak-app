from PyQt6.QtCore import QThread, pyqtSignal

from service.audio_downloader_service import AudioDownloaderService


class ProgressWorker(QThread):
    """Worker thread for simulating linear progress."""

    progress_updated = pyqtSignal(int)
    download_finished = pyqtSignal()
    download_failed = pyqtSignal(str)

    def __init__(
            self,
            service: AudioDownloaderService,
            url: str,
            output_path: str,
            is_spotify: bool
    ):
        """
        Initialize the linear progress thread.

        Args:
            service: The progress of the service
            url: The url to download from.
            output_path: The path to save the progress.
            is_spotify: Whether the progress is a spotify progress.
        """
        super().__init__()
        self.service = service
        self.url = url
        self.output_path = output_path
        self.is_spotify = is_spotify

    def run(self):
        """ Run the linear progress in a separate thread. """

        try:
            self.service.download(
                self.url,
                self.output_path,
                progress_callback=self._on_progress
            )
            self.download_finished.emit()
        except Exception as e:
            self.download_failed.emit(str(e))

    def _on_progress(self, progress: int):
        """
        Handle progress updates.

        Args:
            progress: Progress percentage (0-100).
        """
        self.progress_updated.emit(progress)
