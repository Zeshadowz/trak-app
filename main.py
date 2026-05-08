"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv

from ui.theme_manager import ThemeManager
from ui.widgets.track_app import TrakApp


# from dotenv import load_dotenv
# https://open.spotify.com/track/1uXbwHHfgsXcUKfSZw5ZJ0?si=7752920370c6440e

def main() -> None:
    #
    load_dotenv()

    # High-DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Trak")

    initial_theme = "dark" if "--dark" in sys.argv else "light"
    theme = ThemeManager(app, initial_theme)

    window = TrakApp(theme)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
