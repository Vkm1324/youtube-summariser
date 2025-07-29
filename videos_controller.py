# fetch_youtube_videos.py

import sqlite3 
import googleapiclient.discovery
from config import YOUTUBE_API_KEY, CHANNEL_ID, LOOKBACK_HOURS

import os
import sqlite3

def create_db():
    """Create the SQLite database and videos table if it doesn't exist."""
    # Use an absolute path to the DB file, relative to this script's directory
    db_path = os.path.join(os.path.dirname(__file__), "youtube_video_data.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            published_at TEXT,
            description TEXT,
            url TEXT,
            voice_note_generated INTEGER DEFAULT 0,
            data_updated_in_docs INTEGER DEFAULT 0      
        )
    """)
    
    conn.commit()
    conn.close()

def fetch_new_videos():
    """Fetch videos uploaded in the last N hours from the specified channel."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    print("Fetching new videos from YouTube...")
    # Compute the time threshold (LOOKBACK_HOURS ago from now, in UTC)
    from datetime import datetime, timedelta, timezone
    time_threshold = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Search for videos published after the threshold
    request = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        publishedAfter=time_threshold,
        type="video",
        order="date",
        maxResults=50
    )

    response = request.execute()
    return response.get("items", [])

def store_new_videos(videos):
    """Store only new (not previously stored) videos in the database."""
    conn = sqlite3.connect("youtube_video_data.db")
    cursor = conn.cursor()

    new_count = 0
    for item in videos:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        published_at = item["snippet"]["publishedAt"]
        description = item["snippet"]["description"]
        
        # CORRECTED LINE: Use the standard YouTube video URL format
        url = f"https://www.youtube.com/watch?v={video_id}" 

        try:
            cursor.execute("""
                INSERT INTO videos (video_id, title, published_at, description, url)
                VALUES (?, ?, ?, ?, ?)
            """, (video_id, title, published_at, description, url))
            new_count += 1
        except sqlite3.IntegrityError:
            # Already stored video — skip it
            continue

    conn.commit()
    conn.close()
    return new_count
def get_videos_without_voice_notes():
    """Fetch videos that have voice notes generated."""
    conn = sqlite3.connect("youtube_video_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT video_id,title FROM videos WHERE voice_note_generated = 0
    """)
    videos = cursor.fetchall()

    conn.close()
    return videos

def update_voice_note_status(video_id):
    """Update the voice note generated status for a video."""
    conn = sqlite3.connect("youtube_video_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE videos SET voice_note_generated = 1 WHERE video_id = ?
    """, (video_id,))

    conn.commit()
    conn.close()
    
def update_all_voice_notes_status():
    """Update all voice notes status to 1."""
    conn = sqlite3.connect("youtube_video_data.db")
    cursor = conn.cursor()
    print("Updating all voice notes status to 1..."         )
    cursor.execute("""
        UPDATE videos SET voice_note_generated = 1
    """)

    conn.commit()
    conn.close()
    

def fetch_new_youtube_videos():
    create_db()
    print("Fetching new videos...")
    videos = fetch_new_videos()
    print(f"Fetched {len(videos)} videos from API.")
    new_count = store_new_videos(videos)
    print(f"Stored {new_count} new videos in the database.")

# Only runs if this file is executed directly
if __name__ == "__main__":
    fetch_new_youtube_videos()


