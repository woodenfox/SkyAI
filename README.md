# SkyAI Voice Assistant

A sophisticated voice assistant that uses OpenAI's GPT-4o Realtime API with wake word detection, designed for Raspberry Pi and Linux systems. Features both headless and UI modes with robust audio handling.

## Features

- **Wake Word Detection**: "Jarvis" wake word using Picovoice Porcupine
- **Realtime AI Conversation**: OpenAI's GPT-4o Realtime API for natural voice interactions
- **Dual Mode Support**: 
  - Headless mode (`main.py`) - Terminal-based operation
  - UI mode (`main_ui.py`) - Full-screen pygame interface with visual effects
- **Audio Interruption**: Say "Jarvis" during conversation to interrupt and start fresh
- **Robust Audio Pipeline**: Optimized buffering to prevent audio underruns
- **Automatic Session Management**: Conversations timeout after periods of silence

## System Architecture

### Core Components

- **`main.py`**: Headless entry point using `RealtimeClient`
- **`main_ui.py`**: UI entry point with pygame graphics using `UIRealtimeClient`
- **`realtime_client.py`**: Core Textual-based client for headless mode
- **`ui_realtime_client.py`**: Plain class client with UI integration
- **`wake_word.py`**: Picovoice wake word detection with background interruption support
- **`audio_player.py`**: Async audio playback with buffer management
- **`audio_utils.py`**: Utility functions including acknowledgment beeps
- **`config.py`**: Centralized configuration for all components

### Audio Pipeline

The system uses a sophisticated audio pipeline:
1. **Input**: 48kHz microphone capture → resampled to 24kHz for OpenAI API
2. **Processing**: Real-time streaming to OpenAI with server-side VAD
3. **Output**: 24kHz API response → buffered playback with underrun prevention

## Prerequisites

- Raspberry Pi running Raspberry Pi OS (or any Linux with Python 3.7+)
- Microphone and speaker connected
- OpenAI API key with Realtime API access
- Picovoice API key for wake word detection

## Installation

### System Dependencies

```bash
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev libatlas-base-dev
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project directory:

```env
OPENAI_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PICOVOICE_KEY=your_picovoice_access_key_here
```

### Audio Device Configuration

Check available audio devices:

```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Adjust `MIC_INDEX` and `SPEAKER_INDEX` in `config.py` to match your hardware.

### Audio Testing

Test your audio setup:

```bash
python3 test_audio.py
```

## Usage

### Headless Mode (Recommended)

```bash
python3 main.py
```

Features:
- Terminal-based operation
- Lower resource usage
- Ideal for headless Raspberry Pi setups
- Continuous wake word detection

### UI Mode

```bash
python3 main_ui.py
```

Features:
- Full-screen pygame interface
- Real-time audio visualizations
- Animated particle effects
- Visual state indicators
- Press ESC or Q to quit
- Press SPACE for manual wake word trigger

```bash
python3 main_ui.py --windowed  # Run in windowed mode
```

### Interaction Flow

1. **Start**: Say "Jarvis" to activate
2. **Acknowledge**: Hear confirmation beep
3. **Speak**: Natural conversation with AI assistant
4. **Interrupt**: Say "Jarvis" anytime to start fresh conversation
5. **Timeout**: Conversation auto-ends after 10 seconds of silence

## Configuration

### `config.py` Settings

```python
# Audio device configuration
MIC_INDEX = 0           # Microphone device index
SPEAKER_INDEX = 1       # Speaker device index

# Audio settings
RECORDING_SAMPLE_RATE = 48000   # Input sample rate
LLM_SAMPLE_RATE = 24000         # OpenAI API sample rate
CHUNK_SIZE = 1024               # Audio chunk size
CONVERSATION_TIMEOUT = 10       # Conversation timeout in seconds

# Session configuration for OpenAI Realtime API
SESSION_CONFIG = {
    "modalities": ["audio", "text"],
    "instructions": 'You are a good friend and a helpful assistant.',
    "voice": "ash",                    # Available: alloy, echo, fable, onyx, nova, shimmer, ash
    "turn_detection": {"type": "server_vad"},
    "temperature": 1
}
```

## Troubleshooting

### Audio Issues

**No audio output**: 
- Check `SPEAKER_INDEX` in config.py
- Run `python3 test_audio.py` to verify audio devices

**Audio underruns/choppy playback**:
- The system includes automatic buffer management
- ALSA underrun messages are normal during heavy processing

**Microphone not working**:
- Check `MIC_INDEX` in config.py
- Verify microphone permissions and levels

### Wake Word Issues

**Wake word not detected**:
- Verify Picovoice API key in `.env`
- Check microphone levels and positioning
- Ensure clear pronunciation of "Jarvis"

### API Issues

**Connection failures**:
- Verify OpenAI API key and Realtime API access
- Check internet connectivity
- Monitor API usage limits

## Recent Improvements

### Audio Buffer Management
- Increased buffer size from 50ms to 100ms
- Added 200ms minimum buffer before playback starts
- Implemented low-latency audio streaming settings
- Prevents ALSA underrun errors and ensures smooth playback

### Wake Word Re-detection Fix
- Fixed issue where subsequent wake words weren't detected after conversation timeout
- RealtimeClient now runs in separate thread to avoid blocking main wake word loop
- Supports continuous "Jarvis" detection for multiple conversations

## Development

### Project Structure
```
skyai/
├── main.py              # Headless entry point
├── main_ui.py           # UI entry point  
├── realtime_client.py   # Core headless client
├── ui_realtime_client.py # UI-integrated client
├── wake_word.py         # Wake word detection
├── audio_player.py      # Audio playback system
├── audio_utils.py       # Audio utilities
├── config.py           # Configuration
├── game_ui.py          # UI components
├── test_audio.py       # Audio testing
└── requirements.txt    # Dependencies
```

### Testing

```bash
# Test audio system
python3 test_audio.py

# Test pygame (UI mode)
python3 test_pygame.py

# Test specific audio components  
python3 test_sound.py
``` 