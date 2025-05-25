import os
from dotenv import load_dotenv
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

logging.basicConfig(level=logging.INFO)

# Get credentials from environment variables
load_dotenv(override=True)
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

# Function to get a new access token using the refresh token
def get_access_token():
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
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit}
    response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch recent tracks: {response.text}")
    return response.json().get("items", [])

def spotpy_authenticate():
    # Authenticate with Spotify using OAuth    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-modify-public',
        cache_path=None
    ))

    return sp

def clear_playlist(sp, playlist_id):
    """Remove all tracks from a Spotify playlist."""
    # Get all track URIs in the playlist
    results = sp.playlist_items(playlist_id)
    track_uris = [item['track']['uri'] for item in results['items']]

    if track_uris:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
        logging.debug(f"Cleared {len(track_uris)} tracks from playlist.")
    else:
        logging.info("Playlist already empty.")

def add_tracks_to_playlist(sp, playlist_id, recommended_track_ids):
    """Add new recommended tracks to the playlist."""
    # track_uris = []

    # for rec_df in recommendations:
    #     for index, row in rec_df.iterrows():
    #         query = f"track:{row['TRACK_NAME']} artist:{row['ARTIST_NAME']}"
    #         result = sp.search(q=query, type='track', limit=1)
    #         tracks = result.get('tracks', {}).get('items', [])
    #         if tracks:
    #             track_uri = tracks[0]['uri']
    #             track_uris.append(track_uri)
    #         else:
    #             logging.debug(f"Couldn't find {row['TRACK_NAME']} by {row['ARTIST_NAME']}")

    if recommended_track_ids:
        sp.playlist_add_items(playlist_id, recommended_track_ids)
        logging.info(f"Added {len(recommended_track_ids)} tracks to playlist.")
    else:
        logging.info("No tracks found to add.")



# # Retrieve and print the recent tracks
# if __name__ == "__main__":
#     access_token = get_access_token()
#     recent_tracks_from_spotify = get_recent_tracks_from_spotify(access_token)

#     print("Recent tracks from Spotify:", type(recent_tracks_from_spotify))
#     for item in recent_tracks_from_spotify:
#         track = item["track"]
#         print(f"- {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")

