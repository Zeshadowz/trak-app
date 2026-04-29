"""Abstract base service for audio downloaders."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AudioMetadata:
    """Data class representing audio metadata."""
    artist: str
    title: str


class AudioDownloaderService(ABC):
    """Abstract base class for audio downloader services."""

    @abstractmethod
    def extract_metadata(self, url: str) -> AudioMetadata:
        """
        Extract metadata from the given URL.

        Args:
            url: The URL to extract metadata from.

        Returns:
            AudioMetadata containing artist and title.

        Raises:
            ValueError: If metadata cannot be extracted.
        """
        pass

    @abstractmethod
    def download(self, url: str, output_path: str) -> None:
        """
        Download audio from the given URL to the output path as MP3.

        Args:
            url: The URL to download from.
            output_path: The directory path to save the file.

        Raises:
            Exception: If download fails.
        """
        pass

