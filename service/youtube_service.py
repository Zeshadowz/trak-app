"""YouTube audio downloader service."""
import os
from typing import Callable, Optional
import yt_dlp
from .audio_downloader_service import AudioDownloaderService, AudioMetadata


class YouTubeService(AudioDownloaderService):
    """Service for downloading audio from YouTube."""

    def extract_metadata(self, url: str) -> AudioMetadata:
        """
        Extract metadata from a YouTube URL.

        Args:
            url: The YouTube URL.

        Returns:
            AudioMetadata containing artist (uploader) and title.

        Raises:
            ValueError: If the URL is invalid or extraction fails.
        """
        if not self._is_valid_youtube_url(url):
            raise ValueError("Invalid YouTube URL")

        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                artist = info.get('artist', info.get('uploader', 'Unknown'))
                title = info.get('title', 'Unknown')
                return AudioMetadata(artist=artist, title=title)
        except Exception as e:
            raise ValueError(f"Failed to extract YouTube metadata: {str(e)}")

    def download(
        self,
        url: str,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Download audio from YouTube URL as MP3.

        Args:
            url: The YouTube URL.
            output_path: The directory path to save the file.
            progress_callback: Optional callback to report progress (0-100).

        Raises:
            Exception: If download fails.
        """
        if not self._is_valid_youtube_url(url):
            raise ValueError("Invalid YouTube URL")

        if not os.path.isdir(output_path):
            raise ValueError(f"Output path does not exist: {output_path}")

        def progress_hook(info):
            """Handle progress updates from yt_dlp."""
            if progress_callback is None:
                return
            if info['status'] == 'downloading':
                total = info.get('total_bytes', 0)
                downloaded = info.get('downloaded_bytes', 0)
                if total > 0:
                    progress = int((downloaded / total) * 100)
                    progress_callback(min(progress, 99))
            elif info['status'] == 'finished':
                progress_callback(100)

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook] if progress_callback else [],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise Exception(f"YouTube download failed: {str(e)}")

    @staticmethod
    def _is_valid_youtube_url(url: str) -> bool:
        """
        Check if the URL is a valid YouTube URL.

        Args:
            url: The URL to validate.

        Returns:
            True if it's a YouTube URL, False otherwise.
        """
        return 'youtube' in url or 'youtu.be' in url
