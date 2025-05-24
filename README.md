# 🎧 Spotify Recommender Pipeline (AWS + Docker)

A serverless, containerized music recommendation system that fetches your recently played Spotify tracks, recommends similar songs using audio features, and updates your playlist — all on a scheduled basis.

## Tech Stack

- **Spotify Web API**
- **AWS Lambda (containerized)**
- **Snowflake** for feature storage & querying
- **S3** for temporary data exchange
- **EventBridge** for scheduling
- **SNS** for alerts
- **Docker** for packaging

## What It Does

1. Authenticates to Spotify and gets recently played tracks.
2. Matches them to stored metadata in Snowflake.
3. Recommends similar tracks based on audio features.
4. Updates your chosen Spotify playlist with recommendations.
5. Sends an email notification via SNS upon completion.

## Project Structure

```bash
.
├── Dockerfile
├── requirements.txt
├── lambda_function.py
├── utils/
│   ├── spotify_utils.py
│   ├── recommender_utils.py
│   └── snowflake_utils.py
└── README.md
