import pyaudio
import pvporcupine
import struct
import threading
import time
from config import PICOVOICE_KEY, MIC_INDEX


def wakeup_detect(wakeword_callback, interrupt_event):
    """Detect wake word and call callback when detected."""
    # Create Porcupine wake word engine instance with the default wakeword
    porcupine = pvporcupine.create(keywords=["jarvis"], access_key=PICOVOICE_KEY)

    # Open audio stream from microphone
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        input_device_index=MIC_INDEX,
    )

    print("Listening for wake word...")
    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm_unpacked)
            if result >= 0:
                print("Wake word detected!")
                if interrupt_event.is_set():
                    # If AI is currently talking, interrupt it
                    print("Interrupting current conversation...")
                    time.sleep(0.5)  # Small delay to let cleanup happen
                    interrupt_event.clear()
                else:
                    # Start new conversation
                    wakeword_callback()
                time.sleep(1)  # Prevent multiple triggers
    except KeyboardInterrupt:
        print("Stopping wake word detection...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()


class BackgroundWakeWordDetector:
    """Background thread for wake word detection during conversations."""
    def __init__(self, interrupt_event):
        self.thread = None
        self.running = False
        self.interrupt_event = interrupt_event

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_detection)
        self.thread.daemon = True
        self.thread.start()

    def _run_detection(self):
        wakeup_detect(lambda: None, self.interrupt_event)  # Empty callback since we use the interrupt event

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()