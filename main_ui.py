import asyncio
import threading
import pygame
import sys
from wake_word import wakeup_detect, BackgroundWakeWordDetector
from ui_realtime_client import UIRealtimeClient
from game_ui import GameUI, UIState
from audio_utils import ack_beep


class SkyAIApp:
    def __init__(self, fullscreen=True):
        # Initialize UI
        if fullscreen:
            # Get display info for fullscreen
            pygame.init()
            info = pygame.display.Info()
            self.ui = GameUI(info.current_w, info.current_h, fullscreen=True)
        else:
            self.ui = GameUI(1280, 720, fullscreen=False)
        
        # Global interrupt event
        self.interrupt_event = threading.Event()
        
        # Initialize components
        self.realtime_client = None
        self.wake_detector = None
        
        # Set initial state
        self.ui.set_state(UIState.LISTENING)
        
    def on_wakeword(self):
        """Handle wake word detection by starting the AI assistant."""
        print("Wake word detected! Starting AI assistant...")
        
        # Update UI state
        self.ui.set_state(UIState.WAKE_DETECTED)
        
        # Play acknowledgment beep
        ack_beep()
        
        # Clear any existing interrupt
        self.interrupt_event.clear()
        
        # Start the background wake word detection for interrupts
        if self.wake_detector:
            self.wake_detector.stop()
        self.wake_detector = BackgroundWakeWordDetector(self.interrupt_event)
        self.wake_detector.start()
        
        # Start the AI assistant in a separate thread
        def run_ai():
            asyncio.run(self.start_ai_assistant())
        
        ai_thread = threading.Thread(target=run_ai, daemon=True)
        ai_thread.start()
    
    async def start_ai_assistant(self):
        """Start the AI assistant with UI integration"""
        self.realtime_client = UIRealtimeClient(self.interrupt_event, self.ui)
        
        try:
            await self.realtime_client.start()
        except Exception as e:
            print(f"Error in AI assistant: {e}")
        finally:
            # Cleanup
            if self.wake_detector:
                self.wake_detector.stop()
            self.ui.set_state(UIState.LISTENING)
            print("AI assistant session ended")
    
    def run_wake_detection(self):
        """Run wake word detection in a separate thread"""
        def wake_thread():
            print("SkyAI Voice Assistant starting...")
            print("Listening for wake word 'Jarvis'...")
            wakeup_detect(self.on_wakeword, self.interrupt_event)
        
        wake_thread_obj = threading.Thread(target=wake_thread, daemon=True)
        wake_thread_obj.start()
        return wake_thread_obj
    
    def run(self):
        """Main application loop"""
        # Start wake word detection
        wake_thread = self.run_wake_detection()
        
        # Handle UI events and rendering
        clock = pygame.time.Clock()
        
        try:
            while self.ui.running:
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.ui.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.ui.running = False
                        elif event.key == pygame.K_SPACE:
                            # Manual wake word trigger for testing
                            self.on_wakeword()
                        elif event.key == pygame.K_q:
                            self.ui.running = False
                
                # Update and draw UI
                dt = clock.tick(60) / 1000.0
                self.ui.update(dt)
                self.ui.draw_background()
                self.ui.draw_central_orb()
                self.ui.draw_waveform()
                self.ui.draw_particles(dt)
                self.ui.draw_status_text()
                
                pygame.display.flip()
                
        except KeyboardInterrupt:
            print("\nShutting down SkyAI...")
        finally:
            # Cleanup
            if self.realtime_client:
                self.interrupt_event.set()
            if self.wake_detector:
                self.wake_detector.stop()
            pygame.quit()
            sys.exit()


def main():
    """Main application entry point"""
    # Check for command line arguments
    fullscreen = True
    if len(sys.argv) > 1 and sys.argv[1] == "--windowed":
        fullscreen = False
    
    app = SkyAIApp(fullscreen=fullscreen)
    app.run()


if __name__ == "__main__":
    main()