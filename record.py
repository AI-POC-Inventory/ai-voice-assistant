# record.py
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def record_audio(filename="input.wav", duration=8, fs=16000):
    print("🎤 Speak now...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    
    # Convert float32 to int16 for Vosk
    audio_int16 = np.int16(audio * 32767)
    write(filename, fs, audio_int16)
    return filename
