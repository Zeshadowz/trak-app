from dataclasses import dataclass


@dataclass
class AudioMetadata:
    """Data class representing audio metadata."""
    artist: str
    title: str