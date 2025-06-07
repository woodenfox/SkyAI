#!/usr/bin/env python3

import pygame
import sys
import traceback

def main():
    try:
        print("Starting SkyAI Debug UI...")
        
        # Initialize pygame
        pygame.init()
        print("Pygame initialized")
        
        # Get display info
        info = pygame.display.Info()
        print(f"Display resolution: {info.current_w}x{info.current_h}")
        
        # Create screen - try windowed first
        width, height = 1280, 720
        if len(sys.argv) > 1 and sys.argv[1] == "--fullscreen":
            width, height = info.current_w, info.current_h
            print(f"Attempting fullscreen: {width}x{height}")
            
            # Try different fullscreen methods
            try:
                print("Trying hardware fullscreen...")
                screen = pygame.display.set_mode((width, height), 
                                               pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                print("✓ Hardware fullscreen successful")
            except Exception as e:
                print(f"Hardware fullscreen failed: {e}")
                try:
                    print("Trying borderless window...")
                    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
                    print("✓ Borderless window successful")
                except Exception as e:
                    print(f"Borderless window failed: {e}")
                    print("Falling back to basic fullscreen...")
                    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((width, height))
            print(f"Windowed mode: {width}x{height}")
        
        pygame.display.set_caption("SkyAI Debug")
        clock = pygame.time.Clock()
        
        print("Window created successfully!")
        print("You should see a window with animations...")
        print("Press ESC to quit, SPACE for effects")
        
        # Animation variables
        time = 0
        particles = []
        
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            time += dt
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Add some particles
                        import random
                        import math
                        for _ in range(20):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(50, 150)
                            particles.append({
                                'x': width // 2,
                                'y': height // 2,
                                'vx': math.cos(angle) * speed,
                                'vy': math.sin(angle) * speed,
                                'life': 2.0
                            })
            
            # Clear screen
            screen.fill((0, 0, 20))  # Dark blue
            
            # Draw animated circle in center
            import math
            center_x, center_y = width // 2, height // 2
            radius = 50 + int(math.sin(time * 3) * 20)
            color_intensity = int(128 + 127 * math.sin(time * 2))
            pygame.draw.circle(screen, (0, color_intensity, 255), (center_x, center_y), radius, 3)
            
            # Draw particles
            for particle in particles[:]:
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                particle['life'] -= dt
                
                if particle['life'] <= 0:
                    particles.remove(particle)
                else:
                    alpha = int(255 * (particle['life'] / 2.0))
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(particle['x']), int(particle['y'])), 3)
            
            # Draw status text
            font = pygame.font.Font(None, 36)
            text = font.render("SkyAI Debug UI - Press SPACE for effects", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            
            # Draw FPS
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (0, 255, 0))
            screen.blit(fps_text, (50, 100))
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
        print("Debug UI closed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()