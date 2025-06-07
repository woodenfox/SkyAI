import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_KEY')
PICOVOICE_KEY = os.getenv('PICOVOICE_KEY')

# Audio device configuration
MIC_INDEX = 0  # set to the index of your microphone
SPEAKER_INDEX = 1  # id of the speaker hardware for audio output

# Session configuration for OpenAI Realtime API
SESSION_CONFIG = {
    "modalities": ["audio", "text"],
    "instructions": 'You are a good friend and a helpful assistant.',
    "voice": "ash",
    "turn_detection": {"type": "server_vad"},
    "temperature": 1
}

# Audio settings
RECORDING_SAMPLE_RATE = 48000
LLM_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
CONVERSATION_TIMEOUT = 10  # seconds 