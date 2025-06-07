# SkyAI Voice Assistant

This project is a voice assistant that uses OpenAI's GPT-4o Realtime API and wake word detection, designed for Raspberry Pi.

## Prerequisites

- Raspberry Pi running Raspberry Pi OS (or any Linux with Python 3.7+)
- Microphone and speaker connected
- OpenAI API key

## System Dependencies

Before installing Python packages, run:

```
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev libatlas-base-dev
```

## Python Dependencies

Install all Python dependencies with:

```
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project directory with your OpenAI API key:

```
OPENAI_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Model File

Download or place your OpenWakeWord model file (e.g., `hey_jarvis_v0.1.tflite`) in the project directory.

## Audio Device Indexes

You may need to adjust `mic_index` and `speaker_index` in `main.py` to match your hardware. List devices with:

```
python3 -m sounddevice
```

## Running the App

Run the main script:

```
python3 main.py
```

The assistant will listen for the wake word and respond using OpenAI's GPT-4o Realtime API. 