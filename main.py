import threading
from wake_word import wakeup_detect, BackgroundWakeWordDetector
from realtime_client import RealtimeClient


# Global interrupt event
interrupt_event = threading.Event()


def on_wakeword():
    """Handle wake word detection by starting the AI assistant."""
    # Clear any existing interrupt
    interrupt_event.clear()
    # Start the background wake word detection
    detector = BackgroundWakeWordDetector(interrupt_event)
    detector.start()
    
    # Start the AI assistant in a separate thread so wake word detection can continue
    def run_assistant():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            app = RealtimeClient(interrupt_event)
            app.run(headless=True)
        finally:
            # Cleanup after conversation ends
            detector.stop()
            loop.close()
    
    assistant_thread = threading.Thread(target=run_assistant, daemon=True)
    assistant_thread.start()


def main():
    """Main application entry point."""
    print("SkyAI Voice Assistant starting...")
    print("Listening for wake word 'Jarvis'...")
    wakeup_detect(on_wakeword, interrupt_event)


if __name__ == "__main__":
    main()