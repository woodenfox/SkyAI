import pygame
import math
import time
import threading
import numpy as np
from datetime import datetime
from enum import Enum


class UIState(Enum):
    LISTENING = "listening"
    WAKE_DETECTED = "wake_detected"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    IDLE = "idle"


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 150, 255)
    CYAN = (0, 255, 255)
    GREEN = (0, 255, 100)
    PURPLE = (150, 0, 255)
    ORANGE = (255, 150, 0)
    RED = (255, 50, 50)
    DARK_BLUE = (0, 50, 100)
    GRAY = (100, 100, 100)


class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = 2
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
    
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = (*self.color[:3], alpha)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class GameUI:
    def __init__(self, width=1920, height=1080, fullscreen=True):
        pygame.init()
        pygame.mixer.init()
        
        # Get actual display size
        info = pygame.display.Info()
        if fullscreen:
            self.width = info.current_w
            self.height = info.current_h
        else:
            self.width = width
            self.height = height
        
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Set up display with proper fullscreen flags
        if fullscreen:
            # Try different fullscreen methods for better compatibility
            try:
                # Method 1: Hardware fullscreen
                self.screen = pygame.display.set_mode((self.width, self.height), 
                                                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
            except:
                try:
                    # Method 2: Desktop fullscreen (borderless window)
                    self.screen = pygame.display.set_mode((self.width, self.height), 
                                                        pygame.NOFRAME)
                except:
                    # Method 3: Fallback to regular fullscreen
                    self.screen = pygame.display.set_mode((self.width, self.height), 
                                                        pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
        
        pygame.display.set_caption("SkyAI Voice Assistant")
        pygame.mouse.set_visible(False)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = UIState.LISTENING
        
        # Animation variables
        self.time = 0
        self.pulse_intensity = 0
        self.wave_data = np.zeros(128)
        self.particles = []
        
        # Colors and gradients
        self.bg_color = Colors.BLACK
        self.orb_color = Colors.CYAN
        self.wave_color = Colors.BLUE
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # UI state callbacks
        self.state_callbacks = {}
        
    def set_state(self, new_state: UIState):
        """Change UI state and trigger visual effects"""
        if self.state != new_state:
            self.state = new_state
            self._trigger_state_effects()
            if new_state in self.state_callbacks:
                self.state_callbacks[new_state]()
    
    def _trigger_state_effects(self):
        """Trigger visual effects based on state change"""
        if self.state == UIState.WAKE_DETECTED:
            self._create_wake_particles()
            self.orb_color = Colors.GREEN
        elif self.state == UIState.PROCESSING:
            self.orb_color = Colors.ORANGE
        elif self.state == UIState.SPEAKING:
            self.orb_color = Colors.PURPLE
        elif self.state == UIState.LISTENING:
            self.orb_color = Colors.CYAN
        else:
            self.orb_color = Colors.BLUE
    
    def _create_wake_particles(self):
        """Create particle burst when wake word detected"""
        for _ in range(50):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = Colors.GREEN
            lifetime = np.random.uniform(1.0, 2.0)
            particle = Particle(self.center_x, self.center_y, vx, vy, color, lifetime)
            self.particles.append(particle)
    
    def update_audio_data(self, audio_data):
        """Update waveform visualization with new audio data"""
        if len(audio_data) > 0:
            # Downsample audio data for visualization
            if len(audio_data) > 128:
                step = len(audio_data) // 128
                self.wave_data = audio_data[::step][:128]
            else:
                self.wave_data = np.pad(audio_data, (0, 128 - len(audio_data)), 'constant')
            
            # Calculate pulse intensity from audio volume
            self.pulse_intensity = min(1.0, np.mean(np.abs(self.wave_data)) * 10)
    
    def draw_background(self):
        """Draw animated background"""
        self.screen.fill(self.bg_color)
        
        # Draw moving grid lines
        grid_spacing = 50
        offset = (self.time * 20) % grid_spacing
        
        for x in range(-grid_spacing, self.width + grid_spacing, grid_spacing):
            x_pos = x + offset
            color = (*Colors.DARK_BLUE, 30)
            pygame.draw.line(self.screen, Colors.DARK_BLUE, (x_pos, 0), (x_pos, self.height), 1)
        
        for y in range(-grid_spacing, self.height + grid_spacing, grid_spacing):
            y_pos = y + offset
            pygame.draw.line(self.screen, Colors.DARK_BLUE, (0, y_pos), (self.width, y_pos), 1)
    
    def draw_central_orb(self):
        """Draw the main AI assistant orb"""
        base_radius = 80
        pulse_radius = base_radius + (self.pulse_intensity * 30)
        
        # Outer glow effect
        for i in range(5):
            glow_radius = int(pulse_radius + i * 10)
            alpha = max(0, 50 - i * 10)
            glow_color = (*self.orb_color, alpha)
            # Note: pygame doesn't support alpha directly, so we'll use a simpler approach
            pygame.draw.circle(self.screen, self.orb_color, (self.center_x, self.center_y), glow_radius, 2)
        
        # Main orb
        pygame.draw.circle(self.screen, self.orb_color, (self.center_x, self.center_y), int(pulse_radius), 3)
        
        # Inner core with breathing effect
        core_radius = int(pulse_radius * 0.3 + math.sin(self.time * 3) * 5)
        pygame.draw.circle(self.screen, Colors.WHITE, (self.center_x, self.center_y), core_radius)
    
    def draw_waveform(self):
        """Draw audio waveform visualization"""
        if self.state in [UIState.PROCESSING, UIState.SPEAKING]:
            wave_width = 400
            wave_height = 100
            wave_x = self.center_x - wave_width // 2
            wave_y = self.center_y + 150
            
            points = []
            for i, amplitude in enumerate(self.wave_data):
                x = wave_x + (i / len(self.wave_data)) * wave_width
                y = wave_y + amplitude * wave_height * 0.5
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.wave_color, False, points, 2)
    
    def draw_status_text(self):
        """Draw current status and information"""
        status_text = {
            UIState.LISTENING: "Listening for 'Jarvis'...",
            UIState.WAKE_DETECTED: "Wake word detected!",
            UIState.PROCESSING: "Processing...",
            UIState.SPEAKING: "Speaking...",
            UIState.IDLE: "Ready"
        }
        
        text = status_text.get(self.state, "Unknown")
        color = self.orb_color
        
        rendered = self.font_medium.render(text, True, color)
        text_rect = rendered.get_rect(center=(self.center_x, self.center_y + 250))
        self.screen.blit(rendered, text_rect)
        
        # Draw time
        current_time = datetime.now().strftime("%H:%M:%S")
        time_text = self.font_small.render(current_time, True, Colors.GRAY)
        self.screen.blit(time_text, (20, 20))
    
    def draw_particles(self, dt):
        """Update and draw particle effects"""
        # Update particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update(dt)
            particle.draw(self.screen)
    
    def update(self, dt):
        """Update all UI elements"""
        self.time += dt
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Simulate wake word for testing
                    self.set_state(UIState.WAKE_DETECTED)
    
    def draw(self):
        """Main drawing function"""
        dt = self.clock.tick(60) / 1000.0
        
        self.update(dt)
        
        self.draw_background()
        self.draw_central_orb()
        self.draw_waveform()
        self.draw_particles(dt)
        self.draw_status_text()
        
        pygame.display.flip()
    
    def run(self):
        """Main UI loop"""
        while self.running:
            self.draw()
        
        pygame.quit()
    
    def register_state_callback(self, state: UIState, callback):
        """Register callback for state changes"""
        self.state_callbacks[state] = callback


# Example usage and testing
if __name__ == "__main__":
    ui = GameUI(1280, 720, fullscreen=False)  # Windowed for testing
    
    # Simulate state changes for demo
    def demo_states():
        import time
        states = [UIState.LISTENING, UIState.WAKE_DETECTED, UIState.PROCESSING, UIState.SPEAKING]
        i = 0
        while ui.running:
            time.sleep(3)
            ui.set_state(states[i % len(states)])
            i += 1
    
    # Start demo in separate thread
    threading.Thread(target=demo_states, daemon=True).start()
    
    ui.run()