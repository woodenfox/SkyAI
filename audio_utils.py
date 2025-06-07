import math
import numpy as np
import pyaudio
from config import SPEAKER_INDEX


def make_sinewave(frequency, length, sample_rate=48000):
    """Generate a sine wave for audio feedback."""
    length = int(length * sample_rate)
    factor = float(frequency) * (math.pi * 1) / sample_rate
    waveform = np.sin(np.arange(length) * factor)
    return waveform


# Pre-generate acknowledgment beep waves
wave1 = make_sinewave(500, 0.08)
wave2 = make_sinewave(400, 0.08)


def ack_beep():
    """Play acknowledgment beep when wake word is detected."""
    beep = pyaudio.PyAudio()
    stream = beep.open(
        output_device_index=SPEAKER_INDEX, 
        format=pyaudio.paFloat32, 
        channels=1, 
        rate=48000, 
        output=1,
    )
    stream.write(wave2.astype(np.float32).tobytes())
    stream.write(wave1.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    beep.terminate()