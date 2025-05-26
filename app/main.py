import logging
import os


# Logging
logging.basicConfig(level=logging.INFO)
print("Container initialized")
def lambda_handler(event, context):
    logging.info("Lambda handler started")
    
    # Import necessary modules
    import boto3
    from spotify_utils import (
        get_access_token,
        spotpy_authenticate,
        get_recent_tracks_from_spotify,
        clear_playlist,
        add_tracks_to_playlist,
    )

    from recommender_utils import match_recent_tracks, generate_recommendations_for_matched
    from snowflake_utils import connect_to_snowflake


    try:
        logging.info("Lambda started: Fetch, match, recommend, and update playlist")

        # Spotify auth
        access_token = get_access_token()
        sp = spotpy_authenticate()
        user_id = sp.me()['id']
        logging.info(f"Spotify user ID: {user_id}")

        # Fetch recent tracks
        recent_tracks = get_recent_tracks_from_spotify(access_token)
        if not recent_tracks:
            logging.warning("No recent tracks found.")
            return {'statusCode': 200, 'body': 'No recent tracks found'}

        # Connect to Snowflake and match
        conn = connect_to_snowflake()
        matched_tracks = match_recent_tracks(recent_tracks, conn)
        if not matched_tracks:
            logging.warning("No matched tracks found.")
            conn.close()
            return {'statusCode': 200, 'body': 'No matched tracks found'}

        # Generate recommendations
        all_recommendations = generate_recommendations_for_matched(matched_tracks, conn)
        conn.close()

        if not all_recommendations:
            logging.warning("No recommendations generated.")
            return {'statusCode': 200, 'body': 'No recommendations generated'}

        # Search Spotify for track IDs
        recommended_track_names = [
            name for df in all_recommendations for name in df['TRACK_NAME'].tolist()
        ]
        recommended_track_ids = []

        for name in recommended_track_names:
            results = sp.search(q=name, limit=1, type='track')
            if results['tracks']['items']:
                recommended_track_ids.append(results['tracks']['items'][0]['id'])
            else:
                logging.warning(f"Track not found on Spotify: {name}")

        if not recommended_track_ids:
            logging.warning("No valid Spotify track IDs found.")
            return {'statusCode': 200, 'body': 'No valid Spotify track IDs found'}

        # Update Spotify playlist
        playlist_id = os.getenv("SPOTIFY_PLAYLIST_ID")
        if not playlist_id:
            logging.error("Missing SPOTIFY_PLAYLIST_ID in environment variables")
            return {'statusCode': 500, 'body': 'Missing playlist ID'}

        # Clear existing tracks in the playlist
        clear_playlist(sp, playlist_id)

        # Add new recommended tracks to the playlist
        add_tracks_to_playlist(sp, playlist_id, recommended_track_ids)

        logging.info(f"Updated playlist with {len(recommended_track_ids)} tracks.")

        # Send success notification via SNS
        sns = boto3.client('sns')
        SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='✅ Lambda Success: Music Recommendations Updated',
            Message=f'Playlist updated with {len(recommended_track_ids)} tracks.'
        )

        return {'statusCode': 200, 'body': f"Playlist updated with {len(recommended_track_ids)} tracks"}

    except Exception as e:
        logging.exception("Unhandled error in unified Lambda")
        return {'statusCode': 500, 'body': str(e)}
    