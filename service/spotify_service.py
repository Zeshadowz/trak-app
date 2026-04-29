"""Spotify audio downloader service."""
import os
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from .audio_downloader_service import AudioDownloaderService, AudioMetadata


class SpotifyService(AudioDownloaderService):
    """Service for downloading audio from Spotify using YouTube as source."""

    def __init__(self) -> None:
        """Initialize Spotify service with API credentials."""
        self.spotify_client: Optional[spotipy.Spotify] = None

    def _init_spotify_client(self) -> None:
        """
        Initialize Spotify API client.

        Raises:
            ValueError: If Spotify credentials are not set.
        """
        if self.spotify_client is not None:
            return

        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        if not client_id or not client_secret:
            msg = ("Spotify credentials not set: "
                   "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
            raise ValueError(msg)

        try:
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.spotify_client = spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            raise ValueError(f"Failed to initialize Spotify client: {str(e)}")

    def extract_metadata(self, url: str) -> AudioMetadata:
        """
        Extract metadata from a Spotify track URL.

        Args:
            url: The Spotify track URL.

        Returns:
            AudioMetadata containing artist and title.

        Raises:
            ValueError: If the URL is invalid or extraction fails.
        """
        if not self._is_valid_spotify_url(url):
            raise ValueError("Invalid Spotify URL or not a track URL")

        try:
            self._init_spotify_client()
            track_id = self._extract_track_id(url)

            if not track_id:
                raise ValueError("Could not extract track ID from URL")

            track = self.spotify_client.track(track_id)
            artist = ', '.join([a['name'] for a in track['artists']])
            title = track['name']
            return AudioMetadata(artist=artist, title=title)
        except Exception as e:
            raise ValueError(f"Failed to extract Spotify metadata: {str(e)}")

    def download(self, url: str, output_path: str) -> None:
        """
        Download audio from Spotify track by searching YouTube.

        Args:
            url: The Spotify track URL.
            output_path: The directory path to save the file.

        Raises:
            Exception: If download fails.
        """
        if not self._is_valid_spotify_url(url):
            raise ValueError("Invalid Spotify URL")

        if not os.path.isdir(output_path):
            raise ValueError(f"Output path does not exist: {output_path}")

        try:
            metadata = self.extract_metadata(url)
            search_query = f"ytsearch:{metadata.artist} {metadata.title}"

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
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_query])
        except Exception as e:
            raise Exception(f"Spotify download failed: {str(e)}")

    @staticmethod
    def _is_valid_spotify_url(url: str) -> bool:
        """
        Check if the URL is a valid Spotify track URL.

        Args:
            url: The URL to validate.

        Returns:
            True if it's a Spotify track URL, False otherwise.
        """
        return 'spotify' in url and 'track' in url

    @staticmethod
    def _extract_track_id(url: str) -> Optional[str]:
        """
        Extract track ID from Spotify URL.

        Args:
            url: The Spotify URL.

        Returns:
            The track ID or None if extraction fails.
        """
        try:
            # Spotify URL format: https://open.spotify.com/track/TRACK_ID?...
            track_id = url.split('/track/')[-1].split('?')[0]
            return track_id if track_id else None
        except Exception:
            return None

