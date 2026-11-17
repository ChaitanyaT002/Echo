import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SR = 16000          # Whisper expects 16 kHz
SECONDS = 5

print("Loading model (first run downloads about 140 MB)...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Ready.\n")

while True:
    cmd = input("Press Enter, then speak for 5 seconds (type q to quit): ")
    if cmd.strip().lower() == "q":
        break

    print("Recording...")
    audio = sd.rec(int(SECONDS * SR), samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    audio = audio.flatten()
    print(f"Peak level: {np.max(np.abs(audio)):.3f}")

    t = time.time()
    segments, info = model.transcribe(audio, language="en",
                                      beam_size=1, vad_filter=True)
    text = " ".join(s.text.strip() for s in segments)
    print(f"You said: {text}")
    print(f"Transcription took {time.time() - t:.1f} s\n")