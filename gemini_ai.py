import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import os

def youtube_transcripts(video_id: str, cache_file: str) -> str| None:
    ytt_api = YouTubeTranscriptApi()
    with open(f'{cache_file}', "a", encoding="utf-8") as f:
        for chunk in ytt_api.fetch(video_id):
            if chunk.text:
                    f.write(chunk.text)  # Write each chunk to the cache file
                    f.flush() # Ensure the file is written immediately
        print(f"\n--- transcript produced succesfully  ---")
    f.close()
    return f.name 

def generate_prompt_for_transcript()-> str:
    prompt= f"""
            You are an AI researcher who generates high-quality voice-note summaries of technical or product YouTube videos for a busy audience of AI developers, ML engineers, startup founders, and VCs.

            Based on the transcript below, determine the purpose of the video — whether it's a product pitch, technical explainer, infrastructure breakdown, or architectural deep dive.

            Then, write a natural, flowing 4–6 minute voice-note style script summarizing the video. If it's product-focused, write in a style appealing to VCs. If it's technical, explain clearly and engagingly for AI engineers. The tone should be clear, intelligent, and spoken — not like a blog post.

            Do NOT use Markdown or code blocks. Do NOT include the transcript itself.
            """
    with open('./curr_prompt_cache_file.txt', "w", encoding="utf-8") as f:
        f.write(prompt)
        f.flush() # Ensure the file is written immediately
    f.close()
    return f.name   

def gemini_streaming_with_fallback_and_cache(
    prompt_path: str,
    cache_file_path: str = "gemini_summary_cache.txt",
    models_to_try: list = None,
    encoding: str = "utf-8"
) -> str:
    """
    Generates content using Gemini models with streaming, by reading a large prompt
    from a file and trying models in order of preference. Output is printed and saved.

    Args:
        prompt_path (str): Path to the file containing the full prompt (transcript + instruction).
        cache_file_path (str): File where generated content is saved.
        models_to_try (list): Ordered list of Gemini model names to try.
        encoding (str): Encoding used when reading/writing files.

    Returns:
        str: Full generated response text or empty string if all models fail.
    """
    if models_to_try is None:
        models_to_try = [ "gemini-2.5-pro","gemini-2.5-flash", "gemini-2.5-flash-lite"]

    # Load the prompt in a memory-safe way
    try:
        with open(prompt_path, "r", encoding=encoding) as f:
            prompt = f.read()
    except Exception as e:
        print(f"❌ Failed to read prompt file {prompt_path}: {e}")
        return ""

    full_response_text = ""

    for model_name in models_to_try:
        print(f"Attempting to use model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response_stream = model.generate_content(prompt, stream=True)

            current_model_response = ""
            print(f"--- Streaming response from {model_name} ---")

            with open(cache_file_path, "w", encoding=encoding) as f:
                for chunk in response_stream:
                    if chunk.text:
                        # print(chunk.text, end="", flush=True)
                        f.write(chunk.text)  # Write each chunk to the cache file
                        f.flush() # Ensure the file is written immediately
                        current_model_response += chunk.text

            full_response_text = current_model_response
            print(f"\n✅ Streaming complete using {model_name}. Response cached to: {cache_file_path}")
            return full_response_text

        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            print("Trying next model...")

    print("🚫 All Gemini models failed to generate content.")
    return ""
 