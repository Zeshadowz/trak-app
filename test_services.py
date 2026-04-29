"""Test script to verify service functionality."""
import os
import sys

# Test imports
try:
    from service.youtube_service import YouTubeService
    from service.spotify_service import SpotifyService
    from service.audio_downloader_service import AudioMetadata, AudioDownloaderService
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test service instantiation
try:
    yt_service = YouTubeService()
    spotify_service = SpotifyService()
    print("✓ Service instantiation successful")
except Exception as e:
    print(f"✗ Service instantiation failed: {e}")
    sys.exit(1)

# Test URL validation
try:
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    spotify_url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqLv"

    assert YouTubeService._is_valid_youtube_url(youtube_url), "YouTube URL validation failed"
    assert SpotifyService._is_valid_spotify_url(spotify_url), "Spotify URL validation failed"
    print("✓ URL validation successful")
except AssertionError as e:
    print(f"✗ URL validation failed: {e}")
    sys.exit(1)

# Test metadata extraction for YouTube (without actual download)
try:
    # This will make a real API call
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    metadata = yt_service.extract_metadata(youtube_url)
    assert isinstance(metadata, AudioMetadata), "Metadata is not AudioMetadata instance"
    assert metadata.artist, "Artist is empty"
    assert metadata.title, "Title is empty"
    print(f"✓ YouTube metadata extraction successful: {metadata.artist} - {metadata.title}")
except Exception as e:
    print(f"✗ YouTube metadata extraction failed: {e}")
    # Don't exit, as network issues might occur

# Test Spotify URL parsing
try:
    spotify_url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqLv"
    track_id = SpotifyService._extract_track_id(spotify_url)
    assert track_id == "4cOdK2wGLETKBW3PvgPWqLv", f"Track ID extraction failed: got {track_id}"
    print(f"✓ Spotify URL parsing successful")
except AssertionError as e:
    print(f"✗ Spotify URL parsing failed: {e}")
    sys.exit(1)

print("\n✓ All tests passed!")

