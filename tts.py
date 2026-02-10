# tts.py
import asyncio
import edge_tts
import pyglet
import time
from pathlib import Path
from gtts import gTTS

VOICE_MAP = {
    "en": "en-US-JennyNeural",
    "fr": "fr-FR-DeniseNeural"
}

def speak(text, lang="en"):
    """
    Smart TTS:
    - Edge-TTS for EN / FR
    - gTTS fallback for HI
    """
    if lang in ["en", "fr"]:
        voice = VOICE_MAP[lang]
        asyncio.run(_speak_edge(text, voice))
    elif lang == "hi":
        _speak_gtts(text, "hi")
    else:
        asyncio.run(_speak_edge(text, VOICE_MAP["en"]))


# ---------- EDGE TTS ----------
async def _speak_edge(text, voice):
    output_file = "tts_edge.mp3"
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        music = pyglet.media.load(output_file, streaming=False)
        music.play()
        time.sleep(music.duration)
    except Exception as e:
        print("❌ Edge TTS failed:", e)
    finally:
        Path(output_file).unlink(missing_ok=True)


# ---------- GTTS (Hindi) ----------
def _speak_gtts(text, lang):
    output_file = "tts_gtts.mp3"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)

        music = pyglet.media.load(output_file, streaming=False)
        music.play()
        time.sleep(music.duration)
    except Exception as e:
        print("❌ gTTS failed:", e)
    finally:
        Path(output_file).unlink(missing_ok=True)
