import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Explicitly load .env from project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Get Spotify credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("Error: SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET not set! Check your .env file.")
    exit(1)

# Authenticate with Spotify
auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Set your playlist ID here
  # Replace with your chosen playlist
playlist_id = "4Pxnn3ljvIbXYrcd51Bx9C"

try:
    playlist = sp.playlist(playlist_id)
    print(f"Playlist name: {playlist['name']}")
    print(f"Number of tracks: {playlist['tracks']['total']}")

    # Extract top tracks
    tracks = []
    results = sp.playlist_items(playlist_id, limit=50)
    for item in results.get('items', []):
        track = item.get('track')
        if track:
            tracks.append({
                "track_name": track.get('name'),
                "artist_name": track['artists'][0].get('name') if track.get('artists') else None,
                "album_name": track['album'].get('name') if track.get('album') else None,
                "popularity": track.get('popularity', 0),
                "release_date": track['album'].get('release_date') if track.get('album') else None,
                "track_id": track.get('id')
            })

    print(f"Extracted {len(tracks)} tracks.")
    for t in tracks[:5]:  # Print first 5 tracks as a check
        print(t)

except spotipy.SpotifyException as e:
    print(f"Spotify API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
