# EchoMind

EchoMind is a voice AI assistant built on a plain ESP32. The ESP32 listens through an I2S microphone, streams audio over Wi-Fi (WebSocket) to a laptop, and plays the reply through an I2S amplifier and speaker. A small OLED shows the assistant's emotion. All AI processing (speech-to-text, LLM, text-to-speech) runs locally on the laptop, so no cloud API or API key is needed.

## How it works

```
ESP32 (INMP441 mic)
      |  audio over WebSocket (Wi-Fi)
      v
Laptop server (Python)
  faster-whisper (STT) -> Ollama llama3.2:1b (LLM) -> Kokoro (TTS)
      |  reply audio + emotion over WebSocket
      v
ESP32 (MAX98357A amp + speaker, OLED emotion face)
```

| Stage | Tool | Runs on |
|---|---|---|
| Microphone capture | INMP441 (I2S) | ESP32 |
| Speech-to-text | faster-whisper (`base.en` model) | Laptop |
| Language model | Ollama, `llama3.2:1b` | Laptop |
| Text-to-speech | Kokoro | Laptop |
| Audio playback | MAX98357A + speaker | ESP32 |
| Emotion display | 0.96" OLED (SSD1306, 128x64) | ESP32 |

## Project status

| Part | Status |
|---|---|
| Laptop voice loop (STT -> LLM -> TTS) | Working |
| OLED display | Working |
| ESP32 microphone streaming | In progress |
| Wake word | Planned |

Update this table as you finish each part.

## Hardware required

- ESP32 dev module (plain ESP32, not S3)
- INMP441 I2S microphone
- MAX98357A I2S amplifier + speaker
- 0.96" I2C OLED (128x64)
- Breadboard and jumper wires
- USB cable

## Wiring

These are example pins. Change them to match the pin definitions in your firmware.

| Module pin | ESP32 pin |
|---|---|
| INMP441 VDD | 3V3 |
| INMP441 GND | GND |
| INMP441 SCK | GPIO 14 |
| INMP441 WS | GPIO 15 |
| INMP441 SD | GPIO 32 |
| INMP441 L/R | GND |
| MAX98357A VIN | 5V (VIN) |
| MAX98357A GND | GND |
| MAX98357A BCLK | GPIO 26 |
| MAX98357A LRC | GPIO 25 |
| MAX98357A DIN | GPIO 27 |
| OLED VCC | 3V3 |
| OLED GND | GND |
| OLED SDA | GPIO 21 |
| OLED SCL | GPIO 22 |

## Folder structure

Rename the paths below if your files are named differently.

```
Echo/
├── firmware/            # ESP32 code (Arduino / PlatformIO)
│   └── echo_firmware/
│       ├── echo_firmware.ino
│       └── config.example.h
├── server/              # Laptop code (Python)
│   ├── server.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Setup and run

You need two things running: the laptop server first, then the ESP32.

### 1. Laptop server

Requirements: Python 3.11, [Ollama](https://ollama.com), and a Wi-Fi network shared with the ESP32.

```bash
# Clone the repo
git clone https://github.com/ChaitanyaT002/Echo.git
cd Echo/server

# Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the language model (one time)
ollama pull llama3.2:1b

# Download Kokoro voice files (one time)
curl.exe -L -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl.exe -L -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

# Start the server
python server.py
```

On the first run, faster-whisper and Kokoro download their models automatically, so the first start takes longer. When the server is ready it listens for the ESP32 on a WebSocket port (check `server.py` for the exact port).

Find your laptop's IP address with `ipconfig` (use the IPv4 address of your Wi-Fi adapter). You need it in the next step.

### 2. ESP32 firmware

1. Install the [Arduino IDE](https://www.arduino.cc/en/software) and add ESP32 board support (Boards Manager -> "esp32" by Espressif).
2. Install these libraries (Library Manager): `Adafruit SSD1306`, `Adafruit GFX`, and a WebSocket client library such as `WebSockets` by Markus Sattler. Match the libraries used in your code.
3. In `firmware/echo_firmware/`, copy `config.example.h` to `config.h` and fill in your details:

```cpp
#define WIFI_SSID     "your-wifi-name"
#define WIFI_PASSWORD "your-wifi-password"
#define SERVER_IP     "192.168.x.x"   // laptop IP from ipconfig
#define SERVER_PORT   8765            // must match the port in server.py
```

4. Select **Tools -> Board -> ESP32 Dev Module** and choose the correct COM port.
5. Click **Upload**. If upload stalls at "Connecting...", hold the **BOOT** button on the ESP32 until it starts.
6. Open the Serial Monitor at 115200 baud to see the connection status.

### 3. Use it

1. Keep the server running on the laptop.
2. Power the ESP32. It connects to Wi-Fi and then to the server.
3. Speak to the assistant. The reply plays through the speaker and the OLED shows the emotion.

## Troubleshooting

| Problem | Fix |
|---|---|
| ESP32 cannot connect to the server | Laptop and ESP32 must be on the same Wi-Fi network. Check `SERVER_IP`, and allow Python through Windows Firewall (private networks). |
| Microphone returns only zeros or noise | Check that INMP441 L/R is connected to GND, and check the SCK, WS and SD wiring against the pin definitions in the code. |
| No sound from speaker | Check MAX98357A wiring and power it from 5V. Confirm the speaker is connected to the amp output. |
| OLED stays blank | Confirm the I2C address (usually `0x3C`) and the SDA/SCL pins. |
| Replies are slow | Use the `base` or `tiny` Whisper model and keep `llama3.2:1b`. Close other heavy programs, since the laptop has limited RAM. |
| `ollama` command not found | Restart the terminal after installing Ollama, then run `ollama pull llama3.2:1b` again. |

## Security note

Never commit `config.h`. It contains your Wi-Fi password. Only `config.example.h` (with placeholder values) belongs in the repo, and `.gitignore` excludes `config.h`.

## Tech stack

ESP32 (C++ / Arduino), Python 3.11, WebSocket, faster-whisper, Ollama (llama3.2:1b), Kokoro TTS.

## License

Add a license of your choice (for example MIT) before sharing the project publicly.
