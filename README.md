# YouTube Summarizer

## Overview

**YouTube Summarizer** is an automated pipeline that fetches the latest videos from a specified YouTube channel, generates highly detailed AI-powered summaries, and converts those summaries into voice notes. The project leverages Google Gemini API for summarization and Edge TTS for text-to-speech conversion. All data is managed using SQLite for reliability and easy querying.

---

## Features

- **Automated Video Fetching:**  
  Retrieves new videos from a target YouTube channel using the YouTube Data API.

- **Transcript Extraction:**  
  Extracts video transcripts for accurate, context-rich summarization.

- **AI Summarization:**  
  Uses Google Gemini API to generate conversational, technical summaries tailored for AI/ML content.

- **Voice Note Generation:**  
  Converts summaries into natural-sounding voice notes using Edge TTS.

- **Caching & Database:**  
  Stores video metadata, summaries, and voice notes for efficient reuse and tracking.

---

## Folder Structure

```
youtube_summarizer/
├── cache/                # Stores generated summaries and prompts
├── AIE_insights/         # Output folder for voice notes
├── main.py               # Main pipeline script
├── videos_controller.py  # Database and YouTube API logic
├── gemini_ai.py          # Gemini API integration and prompt generation
├── tts.py                # Text-to-speech conversion logic
├── config.py             # API keys and configuration
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/youtube_summarizer.git
   cd youtube_summarizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   - Create a `config.py` file with your credentials:
     ```python
     YOUTUBE_API_KEY = "your_youtube_api_key"
     GEMINI_API_KEY = "your_gemini_api_key"
     CHANNEL_ID = "your_channel_id"
     LOOKBACK_HOURS = 24  # Number of hours to look back for new videos
     ```

4. **Run the pipeline:**
   ```bash
   python main.py
   ```

---

## How It Works

1. **Fetch Videos:**  
   The pipeline checks for new videos from the configured YouTube channel.

2. **Extract Transcripts:**  
   For each new video, it fetches the transcript (if available).

3. **Generate Summaries:**  
   The transcript and video details are sent to Gemini API, which returns a detailed, conversational summary.

4. **Convert to Voice Notes:**  
   The summary is converted to a voice note using Edge TTS and saved in the output folder.

5. **Database Tracking:**  
   All processed videos are tracked in a local SQLite database to avoid duplicates.

---

## Customization

- **Change Channel:**  
  Update `CHANNEL_ID` in `config.py` to target a different YouTube channel.

- **Adjust Lookback Window:**  
  Modify `LOOKBACK_HOURS` to fetch videos from a different time range.

- **Voice Note Output:**  
  Change `destination_folder` in `main.py` to set a custom output directory.

---

## Troubleshooting

- **API Key Errors:**  
  Ensure your API keys are valid and correctly set in `config.py`.

- **Transcript Issues:**  
  Some videos may not have transcripts available; these will be skipped.

- **Gemini API Limitations:**  
  The Gemini API currently cannot access YouTube videos directly; transcripts must be provided for accurate summaries.

---

## License

MIT License

---

## Credits

- [Google Gemini API](https://ai.google.dev/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Edge TTS](https://github.com/ranyelhousieny/edge-tts)

---

## Author

VK 
[GitHub Profile](https://github.com/Vkm1324)