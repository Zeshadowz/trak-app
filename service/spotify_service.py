"""Spotify audio downloader service."""
import os
from typing import Callable, List, Optional
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

    def extract_metadata(self, url: str) -> List[AudioMetadata]:
        """
        Extract metadata from a Spotify URL (track or playlist).

        Args:
            url: The Spotify URL.

        Returns:
            List of AudioMetadata containing artist, title, and url for each track.

        Raises:
            ValueError: If the URL is invalid or extraction fails.
        """
        if not self._is_valid_spotify_url(url):
            raise ValueError("Invalid Spotify URL")

        try:
            self._init_spotify_client()
            if 'track' in url:
                track_id = self._extract_track_id(url)
                if not track_id:
                    raise ValueError("Could not extract track ID from URL")
                track = self.spotify_client.track(track_id)
                artist = ', '.join([a['name'] for a in track['artists']])
                title = track['name']
                return [AudioMetadata(artist=artist, title=title, url=url)]
            elif 'playlist' in url:
                playlist_id = self._extract_playlist_id(url)
                if not playlist_id:
                    raise ValueError("Could not extract playlist ID from URL")

                try:
                    results = self.spotify_client.playlist_items(playlist_id)
                except Exception as playlist_error:
                    # Check if it's an authentication issue
                    error_msg = str(playlist_error).lower()
                    if '401' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg:
                        raise ValueError(
                            "Unable to access playlist. This may be because:\n"
                            "1. The playlist is private\n"
                            "2. Spotify API credentials are invalid\n"
                            "3. Spotify requires user authentication for this playlist\n\n"
                            "Try using individual track URLs instead, or check your Spotify API credentials."
                        )
                    else:
                        raise ValueError(f"Failed to access playlist: {str(playlist_error)}")

                metadata_list = []
                for item in results['items']:
                    track = item['track']
                    if track:  # Skip None tracks (can happen with local tracks)
                        artist = ', '.join([a['name'] for a in track['artists']])
                        title = track['name']
                        track_url = track['external_urls']['spotify']
                        metadata_list.append(AudioMetadata(artist=artist, title=title, url=track_url))
                return metadata_list
            else:
                raise ValueError("Unsupported Spotify URL type")
        except ValueError:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            raise ValueError(f"Failed to extract Spotify metadata: {str(e)}")

    def download(
        self,
        url,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Download audio from Spotify track by searching YouTube.

        Args:
            url: The Spotify track URL.
            output_path: The directory path to save the file.
            progress_callback: Optional callback to report progress (0-100).
            status_callback: Optional callback to report status messages.

        Raises:
            Exception: If download fails.
        """
        if not self._is_valid_spotify_url(url):
            raise ValueError("Invalid Spotify URL")

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
            metadata_list = self.extract_metadata(url)
            if not metadata_list:
                raise ValueError("No metadata found")
            metadata = metadata_list[0]  # For single track
            search_query = f"ytsearch:{metadata.artist} {metadata.title}"

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_path, '%(uploader)s - %(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook] if progress_callback else [],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_query])
        except Exception as e:
            raise Exception(f"Spotify download failed: {str(e)}")

    def download(
        self,
        data: AudioMetadata,
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Download audio from Spotify track by searching YouTube.

        Args:
            data: AudioMetadata containing the Spotify track URL or string URL
            output_path: The directory path to save the file.
            progress_callback: Optional callback to report progress (0-100).

        Raises:
            Exception: If download fails.
            :param data:
        """
        if not self._is_valid_spotify_url(data.url):
            raise ValueError("Invalid Spotify URL")

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
            metadata_list = self.extract_metadata(data.url)
            if not metadata_list:
                raise ValueError("No metadata found")
            metadata = metadata_list[0]  # For single track
            search_query = f"ytsearch:{metadata.artist} {metadata.title}"

            filename = f"{data.artist} - {data.title}"

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(output_path, filename + '.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook] if progress_callback else [],
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
        return 'spotify' in url and ('track' in url or 'playlist' in url)

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

    @staticmethod
    def _extract_playlist_id(url: str) -> Optional[str]:
        """
        Extract playlist ID from Spotify URL.

        Args:
            url: The Spotify URL.

        Returns:
            The playlist ID or None if extraction fails.
        """
        try:
            # Spotify URL format: https://open.spotify.com/playlist/PLAYLIST_ID?...
            playlist_id = url.split('/playlist/')[-1].split('?')[0]
            return playlist_id if playlist_id else None
        except Exception:
            return None