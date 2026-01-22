# extract.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

def get_spotify_client():
    """
    Create and return a Spotipy client with credentials.
    """
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def extract_multiple_playlists(sp, playlist_ids, limit=50):
    """
    Extract tracks from multiple Spotify playlists with pagination support.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client
        playlist_ids (list): List of Spotify playlist IDs
        limit (int): Number of tracks per request (max 100)

    Returns:
        pd.DataFrame: DataFrame with track information from all playlists
    """
    all_tracks = []

    for pid in playlist_ids:
        try:
            # Fetch playlist metadata
            playlist = sp.playlist(pid)
            playlist_name = playlist.get('name', 'Unknown Playlist')

            results = sp.playlist_items(pid, limit=limit)
            while results:
                for item in results.get('items', []):
                    track = item.get('track')
                    if track:
                        album = track.get('album', {})
                        album_images = album.get('images', [])
                        album_image_url = album_images[0]['url'] if album_images else None

                        all_tracks.append({
                            "track_id": track.get('id'),
                            "track_name": track.get('name'),
                            "artist_name": track['artists'][0].get('name') if track.get('artists') else None,
                            "album_name": album.get('name'),
                            "popularity": track.get('popularity', 0),
                            "release_date": album.get('release_date'),
                            "album_image_url": album_image_url,
                            "preview_url": track.get('preview_url'),
                            "playlist_name": playlist_name,
                            "playlist_id": pid
                        })

                # Move to next page of results if available
                if results.get('next'):
                    results = sp.next(results)
                else:
                    break

        except spotipy.SpotifyException as e:
            print(f"Spotify API error for playlist {pid}: {e}")
        except Exception as e:
            print(f"Unexpected error for playlist {pid}: {e}")

    return pd.DataFrame(all_tracks)
