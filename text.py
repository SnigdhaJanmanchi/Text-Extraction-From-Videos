from moviepy.editor import VideoFileClip
import speech_recognition as sr
from transformers import pipeline
import os

recognizer = sr.Recognizer()
punctuation_model = pipeline("token-classification", model="oliverguhr/fullstop-punctuation-multilang-large", aggregation_strategy="simple")

def extract_audio_chunks(video_path, chunk_duration=30):
    video = VideoFileClip(video_path)
    duration = int(video.duration)
    chunks_dir = "chunks"
    os.makedirs(chunks_dir, exist_ok=True)
    chunk_paths = []

    for start in range(0, duration, chunk_duration):
        end = min(start + chunk_duration, duration)
        chunk = video.subclip(start, end)
        audio_path = os.path.join(chunks_dir, f"chunk_{start}_{end}.wav")
        chunk.audio.write_audiofile(audio_path, codec='pcm_s16le', verbose=False, logger=None)
        chunk_paths.append(audio_path)

    return chunk_paths

def transcribe_audio(file_path):
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
    except Exception as e:
        print(f"❌ Error processing chunk: {e}")
        return ""

def restore_punctuation(text):
    tokens = punctuation_model(text)
    restored_text = ""
    last_end = 0

    for token in tokens:
        start = token['start']
        end = token['end']
        label = token['entity_group']

        restored_text += text[last_end:start]
        restored_text += text[start:end]

        if label == "PERIOD":
            restored_text += "."
        elif label == "COMMA":
            restored_text += ","
        elif label == "QUESTION":
            restored_text += "?"

        last_end = end

    restored_text += text[last_end:]

    # Ensure final punctuation
    restored_text = restored_text.strip()
    if restored_text and restored_text[-1] not in ['.', '?', '!']:
        restored_text += '.'

    return restored_text

def process_video(video_path):
    chunk_paths = extract_audio_chunks(video_path)
    combined_text = ""

    for chunk in chunk_paths:
        text = transcribe_audio(chunk)
        if text:
            combined_text += " " + text

    if combined_text.strip():
        final_text = restore_punctuation(combined_text)
    else:
        final_text = "No speech detected in video."

    return final_text.strip()
