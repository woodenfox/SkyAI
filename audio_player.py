import threading
import numpy as np
import sounddevice as sd
from config import SPEAKER_INDEX


class AudioPlayerAsync:
    def __init__(self):
        self.CHUNK_LENGTH_S = 0.05  # 100ms
        self.SAMPLE_RATE = 24000
        self.CHANNELS = 1
        self.SPEAKER_INDEX = SPEAKER_INDEX
        self.queue = []
        self.lock = threading.Lock()
        self.stream = None
        self.playing = False
    
    def callback(self, outdata, frames, time, status):  # noqa
        global signal
        with self.lock:
            data = np.empty(0, dtype=np.int16)

            # get next item from queue if there is still space in the buffer
            while len(data) < frames and len(self.queue) > 0:
                item = self.queue.pop(0)
                frames_needed = frames - len(data)
                data = np.concatenate((data, item[:frames_needed]))
                if len(item) > frames_needed:
                    self.queue.insert(0, item[frames_needed:])
            
            # fill the rest of the frames with zeros if there is no more data
            if len(data) < frames:
                data = np.concatenate((data, np.zeros(frames - len(data), dtype=np.int16)))

        outdata[:] = data.reshape(-1, 1)
        signal = np.frombuffer(outdata, dtype=np.int16)
   
    def add_data(self, data: bytes):
        with self.lock:
            # bytes is pcm16 single channel audio data, convert to numpy array
            np_data = np.frombuffer(data, dtype=np.int16)
            self.queue.append(np_data)
            if not self.playing:
                self.start()

    def start(self):
        self.playing = True
        self.stream = sd.OutputStream(
            device = self.SPEAKER_INDEX,
            callback=self.callback,
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype=np.int16,
            blocksize=int(self.CHUNK_LENGTH_S * self.SAMPLE_RATE),
        )
        self.stream.start()

    def stop(self):
        self.playing = False
        self.stream.stop()
        self.terminate()
        with self.lock:
            self.queue = []

    def terminate(self):
        self.stream.close()