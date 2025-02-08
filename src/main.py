#!/usr/bin/env python3
import os
import sys
import pygame
import traceback

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_STATES, DISPLAY_FLAGS, WINDOW_TITLE

def center_window():
    """Center the pygame window on the screen"""
    try:
        # Get display info
        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h
        
        if screen_width == 0 or screen_height == 0:
            # Fallback to a common resolution if can't get display info
            screen_width = 1920
            screen_height = 1080
        
        # Calculate window position
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        
        # Set window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
        
    except Exception as e:
        print(f"Warning: Could not center window: {e}")
        # Fallback to default position if centering fails
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"

def main():
    """Main entry point"""
    try:
        print("Starting game...")
        
        # Initialize pygame with all modules
        pygame.init()
        if not pygame.get_init():
            raise Exception("Failed to initialize pygame")
            
        # Set up display
        pygame.display.init()
        if not pygame.display.get_init():
            raise Exception("Failed to initialize display")
            
        # Initialize font system
        pygame.font.init()
        if not pygame.font.get_init():
            raise Exception("Failed to initialize font system")
            
        # Initialize sound system
        pygame.mixer.init()
        if not pygame.mixer.get_init():
            print("Warning: Failed to initialize sound system")
            
        # Center window before creating it
        center_window()
        
        # Set up display with hardware acceleration and vsync
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF | DISPLAY_FLAGS
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, vsync=1)
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Set icon
        try:
            icon = pygame.Surface((32, 32))
            icon.fill((40, 44, 52))
            pygame.draw.circle(icon, (100, 200, 255), (16, 16), 14)
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        
        # Clear screen to prevent black flash
        screen.fill((40, 44, 52))  # Dark background color
        pygame.display.flip()
        
        print("Pygame initialized successfully")
        
        # Import game after pygame is initialized
        from src.game import Game
        
        # Create and run game
        game = Game()
        game.run()
        
        # Normal exit
        sys.exit(0)
        
    except Exception as e:
        print(f"Fatal error running game: {e}")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up
        try:
            print("Cleaning up pygame...")
            pygame.mixer.quit()
            pygame.font.quit()
            pygame.display.quit()
            pygame.quit()
            print("Cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    main() 