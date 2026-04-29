import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class TrakApp(QWidget):
    def __init__(self):
        super().__init__()
        self.artist = ""
        self.title = ""
        self.url = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TRAK")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # Header
        header = QLabel("TRAK")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        # URL input and search button
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.textChanged.connect(self.toggle_search_button)
        self.search_button = QPushButton("Search")
        self.search_button.setEnabled(False)
        self.search_button.clicked.connect(self.search_metadata)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.search_button)
        layout.addLayout(input_layout)

        # Info display
        self.info_label = QLabel("")
        layout.addWidget(self.info_label)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_file)
        self.download_button.setEnabled(False)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def toggle_search_button(self):
        self.search_button.setEnabled(bool(self.url_input.text().strip()))

    def search_metadata(self):
        self.url = self.url_input.text().strip()
        if not self.url:
            return

        try:
            if 'spotify' in self.url:
                self.extract_spotify_metadata()
            elif 'youtube' in self.url or 'youtu.be' in self.url:
                self.extract_youtube_metadata()
            else:
                raise ValueError("Unsupported URL")

            self.info_label.setText(f"Artist: {self.artist}\nTitle: {self.title}")
            self.download_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Not Found", f"Could not extract metadata: {str(e)}")
            self.info_label.setText("")
            self.download_button.setEnabled(False)

    def extract_youtube_metadata(self):
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            self.artist = info.get('artist', info.get('uploader', 'Unknown'))
            self.title = info.get('title', 'Unknown')

    def extract_spotify_metadata(self):
        # Assuming Spotify API credentials are set
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not set")

        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
        # Extract track ID from URL
        if 'track' in self.url:
            track_id = self.url.split('/')[-1].split('?')[0]
            track = sp.track(track_id)
            self.artist = ', '.join([artist['name'] for artist in track['artists']])
            self.title = track['name']
        else:
            raise ValueError("Only Spotify track URLs supported")

    def download_file(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Download Folder")
        if not folder:
            return

        try:
            if 'spotify' in self.url:
                # For Spotify, perhaps search on YouTube and download
                # But for simplicity, assume we have the title, search YouTube
                search_url = f"ytsearch:{self.artist} {self.title}"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([search_url])
            else:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])

            QMessageBox.information(self, "Success", "Download completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrakApp()
    window.show()
    sys.exit(app.exec_())
