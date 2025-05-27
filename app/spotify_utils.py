import os
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

logging.basicConfig(level=logging.INFO)

# Get credentials from environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

def get_access_token():
    
    """
    This function uses the client credentials and refresh token to request a new access token
    from Spotify's API.
    
    Returns:
        str: New access token.
    """

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    return response.json().get("access_token")

def get_recent_tracks_from_spotify(token, limit=20):
    
    """
    Fetch recent tracks from Spotify using the provided access token.
    Args:
        token (str): Spotify access token.
        limit (int): Number of recent tracks to fetch. Default is 20.
    Returns:
        list: List of recent track.
    """

    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit}
    response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch recent tracks: {response.text}")
    return response.json().get("items", [])

def spotpy_authenticate():
    
    """
    Authenticate with Spotify using Spotipy and return the Spotify client.
    Returns:
        spotipy.Spotify: Authenticated Spotify client.
    """ 

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-modify-public',
        cache_path=None
    ))

    return sp

def clear_playlist(sp, playlist_id):
    
    """Remove all tracks from a Spotify playlist.
    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.
        playlist_id (str): ID of the playlist to clear.
    """

    # Get all track URIs in the playlist
    results = sp.playlist_items(playlist_id)
    track_uris = [item['track']['uri'] for item in results['items']]

    if track_uris:
        # Remove all occurrences of the tracks in the playlist
        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
        logging.debug(f"Cleared {len(track_uris)} tracks from playlist.")
    else:
        logging.info("Playlist already empty.")

def add_tracks_to_playlist(sp, playlist_id, recommended_track_ids):
    
    """Add new recommended tracks to the playlist.
    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.
        playlist_id (str): ID of the playlist to update.
        recommended_track_ids (list): List of Spotify track IDs to add.
    """


    if recommended_track_ids:
        sp.playlist_add_items(playlist_id, recommended_track_ids)
        logging.info(f"Added {len(recommended_track_ids)} tracks to playlist.")
    else:
        logging.info("No tracks found to add.")
