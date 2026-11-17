import asyncio
import json

import sounddevice as sd
import websockets

URL = "ws://localhost:8765"
SR = 16000
BLOCK = 512          # 32 ms per frame, similar to what the ESP32 will send


async def main():
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()

    def cb(indata, frames, t, status):
        loop.call_soon_threadsafe(q.put_nowait, bytes(indata))

    async with websockets.connect(URL, max_size=None) as ws:
        print("Connected. Speak after 'listening'. Ctrl+C to quit.")

        async def sender():
            while True:
                await ws.send(await q.get())

        async def receiver():
            out = None
            async for msg in ws:
                if isinstance(msg, bytes):
                    if out:
                        out.write(msg)
                    continue
                d = json.loads(msg)
                print("<-", d)
                if d["type"] == "audio_start":
                    out = sd.RawOutputStream(samplerate=d["rate"], channels=1, dtype="int16")
                    out.start()
                elif d["type"] == "audio_end" and out:
                    out.stop()
                    out.close()
                    out = None

        with sd.RawInputStream(samplerate=SR, channels=1, dtype="int16",
                               blocksize=BLOCK, callback=cb):
            await asyncio.gather(sender(), receiver())


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Bye.")