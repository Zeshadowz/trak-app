# TRAK Application - Architecture Documentation

## Project Structure

```
trak-app/
├── main.py                          # Main GUI application entry point
├── requirements.txt                 # Python dependencies
├── test_services.py                # Service unit tests
├── STANDARDS.md                    # Development standards
└── service/                        # Service layer (business logic)
    ├── __init__.py                 # Package initialization
    ├── audio_downloader_service.py # Abstract base service
    ├── youtube_service.py          # YouTube downloader implementation
    └── spotify_service.py          # Spotify downloader implementation
```

## Architecture Overview

### Clean Architecture Principles

The application follows **Clean Architecture** with clear separation of concerns:

1. **Presentation Layer** (`main.py`)
   - PyQt5 GUI components
   - User interaction handling
   - Error message display

2. **Service Layer** (`service/`)
   - Business logic for metadata extraction
   - Audio download implementations
   - Abstracted interfaces for interchangeability

3. **External Dependencies**
   - `yt_dlp`: YouTube video/audio handling
   - `spotipy`: Spotify API client
   - `PyQt5`: GUI framework

### Service Architecture

#### Abstract Base Service: `AudioDownloaderService`

Defines the interface all downloaders must implement:

```python
class AudioDownloaderService(ABC):
    def extract_metadata(self, url: str) -> AudioMetadata
    def download(self, url: str, output_path: str) -> None
```

**Benefits:**
- Clear contract for all implementations
- Easy to add new services (e.g., SoundCloud, Apple Music)
- Testable with mock implementations
- Dependency Injection ready

#### YouTube Service: `YouTubeService`

Implements audio extraction from YouTube videos:

- Extracts artist/title metadata from video info
- Downloads audio as MP3 (192 kbps)
- Validates YouTube URLs
- Error handling with descriptive messages

#### Spotify Service: `SpotifyService`

Handles Spotify track downloads:

- Extracts artist/title from Spotify API
- Searches YouTube for the track
- Downloads from YouTube search result
- Requires Spotify API credentials (environment variables)

### Data Models

**`AudioMetadata`** (dataclass):
```python
@dataclass
class AudioMetadata:
    artist: str
    title: str
```

Ensures type safety and clear data contracts between layers.

## SOLID Principles Compliance

### Single Responsibility Principle (SRP)
- `YouTubeService`: Only handles YouTube downloads
- `SpotifyService`: Only handles Spotify downloads
- `TrakApp`: Only handles GUI interactions

### Open/Closed Principle (OCP)
- New downloaders can be added by implementing `AudioDownloaderService`
- Existing code doesn't need modification

### Liskov Substitution Principle (LSP)
- All services implement the same interface
- Can be used interchangeably by the GUI layer

### Interface Segregation Principle (ISP)
- `AudioDownloaderService` is focused and minimal
- Only required methods are exposed

### Dependency Inversion Principle (DIP)
- `TrakApp` depends on abstractions (`AudioDownloaderService`)
- Not on concrete implementations

## Configuration

### Environment Variables

For Spotify support, set:
```bash
export SPOTIFY_CLIENT_ID=<your_client_id>
export SPOTIFY_CLIENT_SECRET=<your_client_secret>
```

### External Dependencies

Required system dependencies:
- `ffmpeg`: For audio conversion to MP3

Install via Homebrew on macOS:
```bash
brew install ffmpeg
```

## Testing

Run the test suite:
```bash
python test_services.py
```

Tests verify:
- Service instantiation
- URL validation
- Metadata extraction
- URL parsing

## Future Enhancements

1. **Additional Services**
   - SoundCloud downloader
   - Apple Music support
   - Bandcamp integration

2. **Improved Error Handling**
   - Rate limiting handling
   - Network retry logic
   - User-friendly error messages

3. **Caching Layer**
   - Cache extracted metadata
   - Avoid duplicate API calls

4. **Progress Tracking**
   - Show download progress in UI
   - Cancel downloads mid-operation

5. **Batch Downloads**
   - Support multiple URLs
   - Queue management

## Technical Standards

This project adheres to:
- **PEP 8**: Python code style
- **Type Hints**: Full type annotation
- **Docstrings**: Comprehensive documentation
- **Clean Code**: Small, focused methods
- **SOLID Principles**: Design patterns

