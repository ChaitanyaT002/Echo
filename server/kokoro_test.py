import time
import sounddevice as sd
from kokoro_onnx import Kokoro

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

VOICE = "af_heart"   # try also: af_bella, af_sarah, am_adam, am_michael, bf_emma

while True:
    text = input("Type text to speak (q to quit): ")
    if text.strip().lower() == "q":
        break

    t = time.time()
    audio, sr = kokoro.create(text, voice=VOICE, speed=1.0, lang="en-us")
    gen = time.time() - t
    dur = len(audio) / sr
    print(f"Generated {dur:.1f} s of audio in {gen:.2f} s")

    sd.play(audio, sr)
    sd.wait()