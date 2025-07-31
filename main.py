from config import GEMINI_API_KEY
import google.generativeai as genai
import re
import asyncio
from datetime import datetime
from videos_controller import fetch_new_youtube_videos, get_videos_without_voice_notes, update_voice_note_status
from gemini_ai import (
    gemini_streaming_with_fallback_and_cache,
    generate_prompt_for_transcript,
    youtube_transcripts,
)
from tts import convert_text_to_voice_notes

# === Configuration ===
source_folder = "/home/vk/Desktop/work/personal/youtube_summarizer/cache"
destination_folder = "/home/vk/Desktop/AIE_insights/voice_notes"

log_data = {
    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "retrieved_videos": 0,
    "videos_without_voice_notes": 0,
    "converted_videos": 0,
    "failed_conversions": 0,
    "end_time": None
}

try: 
        
    log_data["retrieved_videos"],log_data["videos_without_voice_notes"] =fetch_new_youtube_videos()
    genai.configure(api_key=GEMINI_API_KEY)
    # print("✅ Gemini API configured.")
except KeyError:
    print("❌ GEMINI_API_KEY not set. Define it in your config.py.")
    exit()

# === Generate Prompts and Summaries ===
try:
    videos = get_videos_without_voice_notes()
    for video_id, title in videos:
        print(f"\n🎬 Starting voice-note prompt generation for video: {title}")

        # Step 1: Prepare prompt file
        prompt_file = generate_prompt_for_transcript()
        prompt_file = youtube_transcripts(video_id=video_id, cache_file=prompt_file)

        # Step 2: Prepare cache filename for output summary
        raw_title = title.split("—")[0].strip()
        safe_title = re.sub(r"[^\w\-_.]", "_", raw_title)
        summary_file_path = f"{source_folder}/{video_id}__{safe_title}_voice_note.txt"
        # Step 3: Generate summary
        gemini_streaming_with_fallback_and_cache(
            prompt_path=prompt_file,
            cache_file_path=summary_file_path
        )
        print(f"✅ Summary generated and saved to {summary_file_path}")
        update_voice_note_status(video_id)

except Exception as e:
    print(f"❌ Error during video processing: {e}")
    exit()

# === Convert Summaries to Voice Notes ===
try:
    asyncio.run(convert_text_to_voice_notes(source_folder, destination_folder))
    print(f"✅ Voice notes saved to {destination_folder}")
except Exception as e:
    log_data["failed_conversions"] += 1
    print(f"❌ TTS conversion failed: {e}")
log_data["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Write analytics to logs.csv
with open('logs.csv', 'a') as log_file:
    log_file.write(
        f'{log_data["start_time"]},{log_data["end_time"]},{log_data["retrieved_videos"]},{log_data["videos_without_voice_notes"]},{log_data["converted_videos"]},{log_data["failed_conversions"]}\n'
    )
    exit()
