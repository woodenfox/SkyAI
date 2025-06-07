#!/usr/bin/env python3

import pygame
import sys

print("Testing pygame display initialization...")

try:
    # Initialize pygame
    pygame.init()
    print("✓ Pygame initialized")
    
    # Get display info
    pygame.display.init()
    info = pygame.display.Info()
    print(f"✓ Display info: {info.current_w}x{info.current_h}")
    
    # Try to create a window
    print("Creating test window...")
    width, height = 800, 600
    
    # Check for fullscreen argument
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
    
    pygame.display.set_caption("SkyAI Display Test")
    print("✓ Window created successfully")
    
    # Fill with color and update
    screen.fill((0, 100, 200))  # Blue background
    
    # Draw a test circle (centered based on actual resolution)
    center_x, center_y = width // 2, height // 2
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 50)
    
    # Add some text (centered)
    font = pygame.font.Font(None, 48)
    text = font.render("SkyAI Display Test", True, (255, 255, 255))
    text_rect = text.get_rect(center=(center_x, center_y - 100))
    screen.blit(text, text_rect)
    
    # Add resolution info
    res_text = font.render(f"Resolution: {width}x{height}", True, (255, 255, 0))
    screen.blit(res_text, (20, 20))
    
    pygame.display.flip()
    print("✓ Display updated")
    
    # Wait for user input
    print("\nDisplay should show a blue window with white circle and text.")
    print("Press SPACE to continue or ESC to quit...")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    print("Space pressed - test passed!")
                    running = False
        
        clock.tick(60)
    
    pygame.quit()
    print("✓ Test completed successfully")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)