import asyncio
import base64
import time
import numpy as np
import sounddevice as sd
import soxr
from openai import AsyncOpenAI
from textual.app import App

from config import (
    OPENAI_API_KEY, 
    SESSION_CONFIG, 
    MIC_INDEX, 
    RECORDING_SAMPLE_RATE, 
    LLM_SAMPLE_RATE, 
    CHUNK_SIZE, 
    CONVERSATION_TIMEOUT
)
from audio_player import AudioPlayerAsync
from audio_utils import ack_beep


class RealtimeClient(App[None]):
    def __init__(self, interrupt_event):
        super().__init__()
        self.interrupt_event = interrupt_event
        self.audio_buffer = b''
        self.audio_player = AudioPlayerAsync()
        self.connection = None
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.connected = asyncio.Event()
        self.should_send_audio = asyncio.Event()
        self.last_response = time.time()
        self.session_config = SESSION_CONFIG

    async def cleanup(self):
        """Cleanup resources when interrupted"""
        if self.audio_player:
            self.audio_player.stop()
        if self.connection:
            await self.connection.close()
        self.should_send_audio.set()  # Allow recording to continue
        self.exit()

    async def on_mount(self) -> None:
        self.run_worker(self.connect())
        self.run_worker(self.send_audio())
        self.run_worker(self.check_interrupt())  # Add interrupt checker
        self.last_response = time.time()
        self.should_send_audio.set()

    async def check_interrupt(self):
        """Check for interrupt signal"""
        while True:
            if self.interrupt_event.is_set():
                await self.cleanup()
                break
            await asyncio.sleep(0.1)

    async def _get_connection(self):
        await self.connected.wait()
        assert self.connection is not None
        return self.connection

    async def send_audio(self):
        """Record audio and send to LLM"""
        print("Recording audio")
        # Play acknowledgement beep
        ack_beep()
        
        # Audio will need to be resampled to 24kHz for the LLM
        rs_to_llm = soxr.ResampleStream(
            RECORDING_SAMPLE_RATE,    # input samplerate
            LLM_SAMPLE_RATE,          # target samplerate
            1,                        # channel(s)
            dtype='int16'             # data type
        )

        stream = sd.InputStream(
            device=MIC_INDEX,
            channels=1,
            samplerate=RECORDING_SAMPLE_RATE,
            dtype="int16",
        )
        stream.start()

        try:
            while True:
                if stream.read_available < CHUNK_SIZE:
                    await asyncio.sleep(0)
                    continue
                
                data, _ = stream.read(CHUNK_SIZE)
     
                connection = await self._get_connection()

                audio = np.frombuffer(data, dtype=np.int16)
                audio_resampled = rs_to_llm.resample_chunk(audio)
                if not audio_resampled.size > 0:
                    await asyncio.sleep(0)
                    continue

                # wait to see if audio can be recorded
                await self.should_send_audio.wait()
                # Encode and send audio chunk through the API connection
                await connection.input_audio_buffer.append(
                    audio=base64.b64encode(audio_resampled).decode("utf-8")
                )
                
                # If timeout seconds have passed since the last response was received,
                # we end the chat. We don't want this to be constantly recording and processing audio.
                if time.time() - self.last_response > CONVERSATION_TIMEOUT:
                    stream.stop()
                    stream.close()
                    self.exit()
                await asyncio.sleep(0)
        
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop()
            stream.close()
            print("audio recording stopped")
            
    async def connect(self):        
        """Handle API connection and response events"""
        async with self.client.beta.realtime.connect(model="gpt-4o-realtime-preview-2025-06-03") as conn:
            await conn.session.update(session=self.session_config)
            self.connection = conn
            self.connected.set()
            
            # Need to resample for output. May not be needed if the output can take 24kHz directly
            self.rs_to_output = soxr.ResampleStream(
                LLM_SAMPLE_RATE,         # input samplerate
                RECORDING_SAMPLE_RATE,   # target samplerate
                1,                       # channel(s)
                dtype='int16'            # data type
            )
            
            async for event in conn:
                print(event.type)
                if event.type == 'error':
                    print(event.error.type)
                    print(event.error.code)
                    print(event.error.event_id)
                    print(event.error.message)
             
                elif event.type == "response.audio.delta":
                    # receiving response so we stop recording, or it would be interrupting itself
                    self.should_send_audio.clear()
                   
                    # decode and add data to the audio player buffer
                    bytes_data = base64.b64decode(event.delta)
                    self.audio_player.add_data(bytes_data)
                    continue
                    
                elif event.type == "response.done":
                    # The API is done responding
                    # The audio player is closed and we can start recording again
                    while len(self.audio_player.queue) > 0:
                        await asyncio.sleep(0.1)
                    self.audio_player.stop()
                    self.last_response = time.time()
                    self.should_send_audio.set()
                    continue