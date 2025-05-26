# 🎵 Spotify Recommender Pipeline (AWS + Docker)

A serverless, containerized music recommendation system that fetches your recently played Spotify tracks, recommends similar songs using audio features, and updates your playlist — all on a scheduled basis.

## Tech Stack

* **Spotify Web API**
* **AWS Lambda (container image)**
* **Snowflake** for feature storage & querying
* **EventBridge** for scheduling
* **SNS** for alerts
* **Docker** for packaging

## What It Does

1. Authenticates with Spotify to fetch recently played tracks.
2. Matches tracks with metadata stored in Snowflake.
3. Recommends similar tracks using audio features.
4. Updates a specified Spotify playlist with recommended tracks.
5. Sends an SNS email notification upon successful run.

## Project Structure

```bash
.
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py
│   ├── spotify_utils.py
│   ├── recommender_utils.py
│   └── snowflake_utils.py
├── README.md
```

## ⚙️ Environment Variables

These should be configured in the Lambda environment or a `.env` file for local testing:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REFRESH_TOKEN=your_refresh_token
SPOTIFY_PLAYLIST_ID=your_playlist_id
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_WAREHOUSE=your_warehouse
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:xxxx:spotify-alerts
```

## Scheduling & Alerts

* Use **AWS EventBridge** to run the recommender daily (e.g., every morning at 8 AM).
* Configure **SNS** with email subscriptions to receive run completion notifications.

## Known Limitations

* Data consisting of songs has 10k entries limiting recommendations.
* Data for recommendations is static.

## Notifications (SNS Email Setup)

1. Create an SNS topic.
2. Subscribe your email address and confirm the email.
3. Attach a policy to the Lambda role allowing `sns:Publish` to your topic.

## Setup Steps

```bash
# Build & tag Docker image
$ docker build -t spotify-recommender .
$ docker tag spotify-recommender:latest <your-ecr-url>

# Authenticate & push
$ aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-ecr-url>
$ docker push <your-ecr-url>
```

Deploy the image to Lambda, set env variables, and connect with EventBridge for scheduled execution.

Happy listening! 🎶
