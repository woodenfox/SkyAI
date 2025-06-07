#!/usr/bin/env python3

import sounddevice as sd
import numpy as np
import time
from config import MIC_INDEX, SPEAKER_INDEX

def test_audio_devices():
    """Test and list all audio devices"""
    print("Available Audio Devices:")
    print("========================")
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
        print(f"   Max inputs: {device['max_input_channels']}")
        print(f"   Max outputs: {device['max_output_channels']}")
        print(f"   Default sample rate: {device['default_samplerate']}")
        print()
    
    print(f"Current config - MIC_INDEX: {MIC_INDEX}, SPEAKER_INDEX: {SPEAKER_INDEX}")
    print()

def test_microphone():
    """Test microphone recording"""
    print("Testing microphone...")
    print("Speak for 3 seconds...")
    
    try:
        duration = 3
        sample_rate = 48000
        
        recording = sd.rec(int(duration * sample_rate), 
                          samplerate=sample_rate, 
                          channels=1, 
                          device=MIC_INDEX,
                          dtype='float64')
        sd.wait()
        
        # Check if we got audio
        max_amplitude = np.max(np.abs(recording))
        print(f"✓ Microphone test completed")
        print(f"Max amplitude: {max_amplitude:.4f}")
        
        if max_amplitude > 0.01:
            print("✓ Microphone is working - audio detected!")
        else:
            print("⚠ Microphone may not be working - very low audio levels")
            
        return recording, sample_rate
        
    except Exception as e:
        print(f"✗ Microphone test failed: {e}")
        return None, None

def test_speaker(recording=None, sample_rate=48000):
    """Test speaker playback"""
    print("Testing speaker...")
    
    try:
        if recording is not None:
            print("Playing back your recorded audio...")
            sd.play(recording, samplerate=sample_rate, device=SPEAKER_INDEX)
            sd.wait()
        else:
            # Generate a test tone
            print("Playing test tone...")
            duration = 2
            frequency = 440  # A note
            t = np.linspace(0, duration, int(sample_rate * duration))
            tone = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            sd.play(tone, samplerate=sample_rate, device=SPEAKER_INDEX)
            sd.wait()
        
        print("✓ Speaker test completed")
        
    except Exception as e:
        print(f"✗ Speaker test failed: {e}")

def test_audio_pipeline():
    """Test the full audio pipeline like SkyAI uses"""
    print("Testing SkyAI audio pipeline...")
    
    try:
        from audio_player import AudioPlayerAsync
        from audio_utils import ack_beep
        
        print("Testing acknowledgment beep...")
        ack_beep()
        time.sleep(1)
        
        print("Testing audio player...")
        player = AudioPlayerAsync()
        
        # Generate test audio data (PCM16)
        duration = 2
        sample_rate = 24000
        t = np.linspace(0, duration, int(sample_rate * duration))
        tone = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        
        print("Playing test tone through AudioPlayerAsync...")
        player.add_data(tone.tobytes())
        time.sleep(duration + 1)
        player.stop()
        
        print("✓ Audio pipeline test completed")
        
    except Exception as e:
        print(f"✗ Audio pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("SkyAI Audio System Test")
    print("======================")
    print()
    
    # Test 1: List devices
    test_audio_devices()
    
    # Test 2: Microphone
    recording, sample_rate = test_microphone()
    print()
    
    # Test 3: Speaker
    test_speaker(recording, sample_rate)
    print()
    
    # Test 4: SkyAI audio pipeline
    test_audio_pipeline()
    print()
    
    print("Audio test completed!")
    print()
    print("If you heard the beep and test tones, audio output is working.")
    print("If microphone detected audio when you spoke, input is working.")
    print("If both work, the issue might be with OpenAI API or network.")

if __name__ == "__main__":
    main()