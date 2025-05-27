import pandas as pd
import numpy as np
import logging
from sklearn.metrics.pairwise import cosine_similarity

# Logging
logging.basicConfig(level=logging.INFO)

def get_all_songs(conn):
    """
    Fetch all songs from Kaggle table.

    Args:
        conn: Snowflake connection.

    Returns:
        DataFrame: DataFrame containing all songs with their features.
    """
    query = """
        SELECT TRACK_NAME, ARTIST_NAME, DANCEABILITY, ENERGY, KEY, 
               LIVENESS, LOUDNESS, POPULARITY, TEMPO, VALENCE 
        FROM KAGGLE_DATA_TOP_10000
    """
    df = pd.read_sql(query, conn)
    logging.info("Fetched all songs from database.")
    return df

def match_recent_tracks(recent_tracks_from_spotify, conn):
    """
    Matches recently played Spotify tracks to Kaggle dataset.

    Args:
        recent_tracks_from_spotify (list): List of recent track objects.
        conn: Snowflake connection.

    Returns:
        dict: matched track name -> track row dictionary
    """
    df = get_all_songs(conn)
    matched_tracks = {}

    logging.info("Matching recent Spotify tracks with Kaggle database...")

    for item in recent_tracks_from_spotify:
        track = item["track"]
        artists = [artist['name'] for artist in track['artists']]
        track_name_spotify = track['name'].strip().lower()

        logging.info(f"Checking: {track['name']} by {', '.join(artists)}")

        possible_matches = df[df['TRACK_NAME'].str.strip().str.lower() == track_name_spotify]

        if possible_matches.empty:
            logging.warning(f"No track match found in Kaggle for {track['name']}.")
            continue

        found = False
        for _, row in possible_matches.iterrows():
            artist_from_db = row['ARTIST_NAME'].strip().lower()
            for artist_spotify in artists:
                if artist_spotify.strip().lower() in artist_from_db:
                    matched_tracks[track['name']] = row.to_dict()
                    logging.info(f"Matched with artist: {artist_spotify}")
                    found = True
                    break
            if found:
                break

        if not found:
            logging.warning(f"No matching artist found for track: {track['name']}.")

    logging.info(f"Total matched tracks: {len(matched_tracks)}")
    return matched_tracks

def recommend_similar_songs(matched_song_row, all_songs, top_n=5):
    """
    Recommend similar songs based on feature similarity.

    Args:
        matched_song_row (dict): Matched song data.
        all_songs (DataFrame): All available songs from Kaggle DB.
        top_n (int): Number of recommendations.

    Returns:
        DataFrame: Top-N similar songs
    """
    feature_cols = ['DANCEABILITY', 'ENERGY', 'KEY', 'LIVENESS', 
                    'VALENCE', 'LOUDNESS', 'POPULARITY', 'TEMPO']

    all_songs[feature_cols] = all_songs[feature_cols].apply(pd.to_numeric, errors='coerce')
    all_songs = all_songs.dropna(subset=feature_cols)

    matched_song_row = pd.Series(matched_song_row)
    matched_song_row[feature_cols] = matched_song_row[feature_cols].apply(pd.to_numeric, errors='coerce')

    if matched_song_row[feature_cols].isnull().any():
        logging.warning("Matched song has missing features. Skipping.")
        return None

    target_vector = np.array(matched_song_row[feature_cols]).reshape(1, -1)
    all_vectors = np.array(all_songs[feature_cols])

    similarities = cosine_similarity(target_vector, all_vectors)[0]
    all_songs['similarity'] = similarities

    recommendations = all_songs.sort_values(by='similarity', ascending=False).head(top_n)

    logging.info(f"Generated {top_n} recommendations.")
    return recommendations[['TRACK_NAME', 'ARTIST_NAME', 'similarity']]

def generate_recommendations_for_matched(matched_tracks, conn):
    """
    Generate recommendations for all matched recent tracks.

    Args:
        matched_tracks (dict): recent matched songs
        conn: Snowflake connection

    Returns:
        list: List of recommendation DataFrames
    """
    songs_db = get_all_songs(conn)
    recommendations = []

    for track_name, matched_row in matched_tracks.items():
        logging.info(f"Generating recommendations for: {track_name}")
        song_recommendation = recommend_similar_songs(matched_row, songs_db)
        if song_recommendation is not None:
            recommendations.append(song_recommendation)
        else:
            logging.warning(f"Skipped recommendation for {track_name} due to incomplete data.")

    logging.info(f"Generated recommendations for {len(recommendations)} songs.")
    return recommendations


