from model import AudioMetadata
from ui.components.feedback.progress.linear_progress import ProgressWorker


class UiService:

    def progress(self) -> ProgressWorker:
        """Get the progress worker instance."""
        return self._progress_worker


    def __init__(self):
        """Initialize the UI service."""
        self._progress_worker = None

    def create_progress_worker(
            self,
            service,
            metadata: AudioMetadata,
            output_path: str,
            is_spotify: bool
    ) -> ProgressWorker:
        """
        Create a new progress worker instance.

        Args:
            service: The audio downloader service to use.
            metadata: The metadata to use.
            output_path: The path to save the file.
            is_spotify: Whether the URL is a Spotify link.

        Returns:
            A new ProgressWorker instance.
        """
        self._progress_worker = ProgressWorker(
            service,
            metadata,
            output_path,
            is_spotify
        )
        return self._progress_worker