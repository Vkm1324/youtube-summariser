from config import GEMINI_API_KEY
import google.generativeai as genai
import re
import asyncio
import edge_tts

from videos_controller import get_videos_without_voice_notes
from gemini_ai import (
    gemini_streaming_with_fallback_and_cache,
    generate_prompt_for_transcript,
    youtube_transcripts,
)
from tts import convert_text_to_voice_notes

# === Configuration ===
source_folder = "/home/vk/Desktop/work/personal/youtube_summarizer/cache"
destination_folder = "/home/vk/Desktop/AIE_insights/voice_notes"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured.")
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

except Exception as e:
    print(f"❌ Error during video processing: {e}")
    exit()

# === Convert Summaries to Voice Notes ===
try:
    asyncio.run(convert_text_to_voice_notes(source_folder, destination_folder))
    print(f"✅ Voice notes saved to {destination_folder}")
except Exception as e:
    print(f"❌ TTS conversion failed: {e}")
    exit()
