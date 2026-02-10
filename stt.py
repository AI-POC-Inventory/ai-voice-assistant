# stt.py
from vosk import Model, KaldiRecognizer
import wave
import json

print("Loading Vosk models. Please wait...")

# Load models at startup
MODELS = {
    "en": Model("models/vosk/vosk-model-small-en-us-0.15"),
    "fr": Model("models/vosk/vosk-model-small-fr-0.22"),
}

print("Vosk models loaded successfully.")

# Mapping human language names -> model keys
LANG_MAP = {
    "english": "en",
    "french": "fr",
    "français": "fr"
}

def transcribe(filename="input.wav", lang="en"):
    # Normalize lang
    lang_key = LANG_MAP.get(lang.lower(), lang.lower())

    if lang_key not in MODELS:
        print(f"❌ Language model '{lang}' not loaded.")
        return ""

    wf = wave.open(filename, "rb")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("⚠️ Audio must be WAV mono PCM 16kHz")
        return ""

    rec = KaldiRecognizer(MODELS[lang_key], wf.getframerate())
    rec.SetWords(True)

    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text += res.get("text", "") + " "

    final_res = json.loads(rec.FinalResult())
    text += final_res.get("text", "")

    return text.strip()
