import asyncio
import base64
import time
import threading
import numpy as np
import sounddevice as sd
import soxr
from openai import AsyncOpenAI

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
from game_ui import GameUI, UIState


class UIRealtimeClient:
    def __init__(self, interrupt_event, ui: GameUI):
        self.interrupt_event = interrupt_event
        self.ui = ui
        self.audio_buffer = b''
        self.audio_player = AudioPlayerAsync()
        self.connection = None
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.connected = asyncio.Event()
        self.should_send_audio = asyncio.Event()
        self.last_response = time.time()
        self.session_config = SESSION_CONFIG
        self.running = False
        
        # Audio data for visualization
        self.current_audio_data = np.zeros(128)

    async def cleanup(self):
        """Cleanup resources when interrupted"""
        if self.audio_player:
            self.audio_player.stop()
        if self.connection:
            await self.connection.close()
        self.should_send_audio.set()
        self.running = False

    async def start(self):
        """Start the realtime client"""
        self.running = True
        self.ui.set_state(UIState.PROCESSING)
        
        # Start all async tasks
        tasks = [
            asyncio.create_task(self.connect()),
            asyncio.create_task(self.send_audio()),
            asyncio.create_task(self.check_interrupt()),
        ]
        
        self.last_response = time.time()
        self.should_send_audio.set()
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in realtime client: {e}")
        finally:
            await self.cleanup()

    async def check_interrupt(self):
        """Check for interrupt signal"""
        while self.running:
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
        print("Recording audio with UI")
        
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
            while self.running:
                if stream.read_available < CHUNK_SIZE:
                    await asyncio.sleep(0)
                    continue
                
                data, _ = stream.read(CHUNK_SIZE)
                connection = await self._get_connection()

                audio = np.frombuffer(data, dtype=np.int16)
                
                # Update UI with audio data for visualization
                self.current_audio_data = audio[:128] if len(audio) >= 128 else np.pad(audio, (0, 128 - len(audio)), 'constant')
                self.ui.update_audio_data(self.current_audio_data)
                
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
                    self.running = False
                    self.ui.set_state(UIState.LISTENING)
                    return
                    
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
                if not self.running:
                    break
                    
                print(event.type)
                if event.type == 'error':
                    print(event.error.type)
                    print(event.error.code)
                    print(event.error.event_id)
                    print(event.error.message)
             
                elif event.type == "response.audio.delta":
                    # receiving response so we stop recording, or it would be interrupting itself
                    self.should_send_audio.clear()
                    self.ui.set_state(UIState.SPEAKING)
                   
                    # decode and add data to the audio player buffer
                    bytes_data = base64.b64decode(event.delta)
                    
                    # Update UI with response audio data
                    audio_np = np.frombuffer(bytes_data, dtype=np.int16)
                    if len(audio_np) > 0:
                        self.ui.update_audio_data(audio_np)
                    
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
                    self.ui.set_state(UIState.PROCESSING)
                    continue
                    
                elif event.type == "response.audio_transcript.delta":
                    # Handle text transcription if needed
                    pass