"""TRAK Application - Spotify and YouTube to MP3 Downloader."""
import sys

from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv

from ui.widgets.track_app import TrakApp

# from dotenv import load_dotenv
# https://open.spotify.com/track/1uXbwHHfgsXcUKfSZw5ZJ0?si=7752920370c6440e

if __name__ == "__main__":
    app = QApplication(sys.argv)

    load_dotenv()

    with open("ui/styles/app.qss", "r", encoding="utf8") as f:
        app.setStyleSheet(f.read())

    window = TrakApp()
    window.show()
    
    sys.exit(app.exec())
