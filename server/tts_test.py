import time
import numpy as np
import sounddevice as sd
from piper import PiperVoice

voice = PiperVoice.load("en_US-lessac-medium.onnx")
sr = voice.config.sample_rate
print("Voice loaded, sample rate:", sr)


def synth(text):
    chunks = []
    if hasattr(voice, "synthesize_stream_raw"):      # older Piper versions
        for b in voice.synthesize_stream_raw(text):
            chunks.append(np.frombuffer(b, dtype=np.int16))
    else:                                            # newer Piper versions
        for c in voice.synthesize(text):
            chunks.append(np.frombuffer(c.audio_int16_bytes, dtype=np.int16))
    return np.concatenate(chunks)


while True:
    text = input("Type text to speak (q to quit): ")
    if text.strip().lower() == "q":
        break

    t = time.time()
    audio = synth(text)
    gen = time.time() - t
    dur = len(audio) / sr
    print(f"Generated {dur:.1f} s of audio in {gen:.2f} s")

    sd.play(audio, sr)
    sd.wait()
