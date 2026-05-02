import yt_dlp

from model import AudioMetadata
from service.audio_downloader_service import AudioDownloaderService


class SpotifyFlatService(AudioDownloaderService):
    """Service for downloading audio from Spotify using YouTube as source."""

    def extract_metadata(self, url: str) -> AudioMetadata:
        # ─── Step 1: extract metadata only (no download yet) ───────────────────
        extract_opts: dict = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,  # full extraction so we get artist/title
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(extract_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if info is None:
            raise ValueError(f"Could not extract info from URL: {url}")

        # yt-dlp exposes Spotify metadata under these keys when resolving via
        # the embedded YouTube match.
        artist: str = (
                info.get("artist")
                or info.get("uploader")
                or "Unknown Artist"
        )
        title: str = (
                info.get("track")
                or info.get("title")
                or "Unknown Title"
        )
        return AudioMetadata(artist=artist, title=title)

    def download(self, url: str, output_path: str) -> None:
        """ Download audio from Spotify using YouTube as source. """


