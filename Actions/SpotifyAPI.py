import spotipy
from spotipy.oauth2 import SpotifyOAuth
from core import config


class SpotifyAPIStrategy:
    def __init__(self):
        # Authentifizierung beim Start
        scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=config.SPOTIFY_REDIRECT_URI,
            scope=scope,  # Diese Scopes sind entscheidend!
            show_dialog=True  # Erzwingt beim nächsten Mal die Rechte-Abfrage
        ))
        print("Spotify API verbunden.")

    def execute_gesture(self, gesture_name, data=None):
        try:
            if gesture_name == "OPEN_HAND":
                # Wiedergabe pausieren oder fortsetzen
                playback = self.sp.current_playback()
                if playback and playback['is_playing']:
                    self.sp.pause_playback()
                else:
                    self.sp.start_playback()

            elif gesture_name == "PEACE":
                self.sp.next_track()


        except Exception as e:
            print(f"Spotify Fehler: {e}")

    # In actions/spotify_action.py

    def set_volume(self, value):
        """Setzt die Lautstärke direkt auf einen bestimmten Prozentwert."""
        try:
            self.sp.volume(value)
            print(f"Volume set to: {value}%")
        except Exception as e:
            print(f"Spotify Volume Error: {e}")