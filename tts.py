import os
import edge_tts
import random

from config import CACHE_FOLDER, VOICE_NOTES_FOLDER

VOICE_LIST = [
    {
        "short_name": "en-US-AnaNeural",
        "name": "Ana",
        "gender": "Female",
        "personality": ["Cute","child"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-ChristopherNeural",
        "name": "Christopher",
        "gender": "Male",
        "personality": ["Reliable", "Authority","Base voice"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-EricNeural",
        "name": "Eric",
        "gender": "Male",
        "personality": ["Rational"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-GuyNeural",
        "name": "Guy",
        "gender": "Male",
        "personality": ["Passion"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-JennyNeural",
        "name": "Jenny",
        "gender": "Female",
        "personality": ["Friendly", "Considerate", "Comfort"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-MichelleNeural",
        "name": "Michelle",
        "gender": "Female",
        "personality": ["Friendly", "Pleasant","Base voice"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-RogerNeural",
        "name": "Roger",
        "gender": "Male",
        "personality": ["Lively"],
        "locale": "en-US"
    },
    {
        "short_name": "en-US-SteffanNeural",
        "name": "Steffan",
        "gender": "Male",
        "personality": ["Rational"],
        "locale": "en-US"
    }
]

async def convert_text_to_voice_notes(source_folder, destination_folder):
    fav_characters = ["Ana","Aria", "Eric", "Guy", "Jenny","Roger",]
    # Ensure destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # List all .txt files in source folder
    txt_files = [f for f in os.listdir(source_folder) if f.endswith(".txt")]

    if not txt_files:
        print("⚠️ No .txt files found in source folder.")
        return

    print(f"🔄 Converting {len(txt_files)} text files to voice notes \n")

    for filename in txt_files:
        source_path = os.path.join(source_folder, filename)
        voice_suffix =random.choice(fav_characters)
        voice = f"en-US-{voice_suffix}Neural"

        file = filename[:-4]  # removes '.txt'
        parts = file.split("__", 1)  # split only first two underscores

        if len(parts) != 2:
            print(f"⚠️ Skipped invalid filename: {filename}")
            continue  
        file_id, name = parts        
        dest_filename = f"{name}_{voice_suffix}.mp3"
        dest_path = os.path.join(destination_folder, dest_filename)

        with open(source_path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            print(f"⚠️ Skipped empty file: {filename}")
            continue

        print(f"🎙️ Processing: {name} → {dest_filename}")

        tts = edge_tts.Communicate(text=f'i am {voice_suffix}'+text, voice=voice)
        await tts.save(dest_path)
        os.remove(source_path)  # Remove the cached source file after conversion
    print("\n✅ Done! All voice notes saved in:", destination_folder)
    
if __name__ == "__main__":
    import asyncio

    source_folder = CACHE_FOLDER
    destination_folder = VOICE_NOTES_FOLDER 
    asyncio.run(convert_text_to_voice_notes(source_folder, destination_folder)) 
    exit()  

