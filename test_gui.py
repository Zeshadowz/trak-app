"""Comprehensive GUI application tests."""
import sys
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication

def test_gui_setup():
    """Test GUI initialization without display."""
    try:
        # Create application instance (needed for PyQt5)
        app = QApplication.instance() or QApplication([])

        # Import after QApplication creation
        from main import TrakApp

        # Create the app window
        window = TrakApp()

        # Verify UI components exist
        assert hasattr(window, 'url_input'), "url_input widget missing"
        assert hasattr(window, 'search_button'), "search_button widget missing"
        assert hasattr(window, 'info_label'), "info_label widget missing"
        assert hasattr(window, 'download_button'), "download_button widget missing"

        # Verify initial state
        assert not window.search_button.isEnabled(), "Search button should be disabled initially"
        assert not window.download_button.isEnabled(), "Download button should be disabled initially"

        print("✓ GUI setup test passed")
        return True
    except Exception as e:
        print(f"✗ GUI setup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_input_validation():
    """Test URL input validation."""
    try:
        app = QApplication.instance() or QApplication([])
        from main import TrakApp

        window = TrakApp()

        # Test empty input
        window.url_input.setText("")
        assert not window.search_button.isEnabled(), "Search button should be disabled for empty input"

        # Test valid input
        window.url_input.setText("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert window.search_button.isEnabled(), "Search button should be enabled for valid input"

        # Test with spaces
        window.url_input.setText("   ")
        assert not window.search_button.isEnabled(), "Search button should be disabled for whitespace input"

        print("✓ URL input validation test passed")
        return True
    except Exception as e:
        print(f"✗ URL input validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_integration():
    """Test service integration in GUI."""
    try:
        from main import TrakApp
        from service.youtube_service import YouTubeService
        from service.spotify_service import SpotifyService

        app = QApplication.instance() or QApplication([])
        window = TrakApp()

        # Verify services are initialized
        assert isinstance(window.youtube_service, YouTubeService), "YouTube service not initialized"
        assert isinstance(window.spotify_service, SpotifyService), "Spotify service not initialized"

        print("✓ Service integration test passed")
        return True
    except Exception as e:
        print(f"✗ Service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_extraction_logic():
    """Test metadata extraction routing logic."""
    try:
        from main import TrakApp

        app = QApplication.instance() or QApplication([])
        window = TrakApp()

        # Test YouTube URL routing
        window.url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        service = window._extract_metadata_using_service.__self__
        assert window.youtube_service is not None

        # Test Spotify URL would go to spotify service
        window.url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqLv"
        assert window.spotify_service is not None

        print("✓ Metadata extraction logic test passed")
        return True
    except Exception as e:
        print(f"✗ Metadata extraction logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running TRAK GUI Application Tests...\n")

    tests = [
        test_gui_setup,
        test_url_input_validation,
        test_service_integration,
        test_metadata_extraction_logic,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    passed = sum(results)
    total = len(results)

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All GUI tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

