import pygame
import sys
import traceback
from typing import Dict, Optional, Tuple
from .world import World
from .constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, TARGET_FPS,
    DISPLAY_FLAGS, WINDOW_TITLE, VSYNC, SCREEN_STATES,
    GRAPHICS_QUALITY, FONTS, FRAME_LENGTH
)
from .ui.screen_manager import ScreenManager
from .ui.screens.main_menu import MainMenuScreen
from .ui.screens.game_screen import GameScreen
from .ui.screens.world_gen import WorldGenScreen
import time
from .ui.ui_system import UISystem

class Game:
    def __init__(self):
        """Initialize game"""
        try:
            print("Initializing game...")
            pygame.init()
            pygame.font.init()
            
            # Create window
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("World Simulation")
            
            # Initialize clock
            self.clock = pygame.time.Clock()
            self.running = True
            self.paused = False
            
            # Set maximum graphics quality
            self.graphics_settings = GRAPHICS_QUALITY['ultra']
            
            # Initialize UI system
            self.ui_system = UISystem()
            
            # Initialize world reference
            self.world = None
            
            # Create screen manager with self reference
            self.screen_manager = ScreenManager(self)
            
            # Start with main menu
            self.screen_manager.switch_screen('mainmenu')
            
            print("Game initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing game: {e}")
            traceback.print_exc()
            sys.exit(1)
            
    def run(self):
        """Main game loop"""
        try:
            last_time = time.time()
            while self.running:
                # Calculate delta time
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.screen_manager.handle_event(event)
                        
                # Update current screen
                self.screen_manager.update(dt)
                
                # Clear screen
                self.screen.fill(UI_COLORS['background'])
                
                # Draw current screen
                self.screen_manager.draw(self.screen)
                
                # Update display
                pygame.display.flip()
                
                # Cap framerate
                self.clock.tick(TARGET_FPS)
                
        except Exception as e:
            print(f"Error in game loop: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()
            
    def initialize_world(self):
        """Initialize the game world"""
        try:
            print("Initializing world generation...")
            
            # Clean up existing world if any
            if self.world:
                self.world.cleanup()
                self.world = None
            
            # Switch to world generation screen
            self.screen_manager.switch_screen('world_gen')
            
        except Exception as e:
            print(f"Error initializing world: {e}")
            traceback.print_exc()
            
    def _update_generation_progress(self, progress: float, status: str):
        """Update world generation progress"""
        try:
            if self.screen_manager.current_screen:
                screen = self.screen_manager.current_screen
                if hasattr(screen, 'update_progress'):
                    screen.update_progress(progress, status)
        except Exception as e:
            print(f"Error updating generation progress: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up game resources"""
        try:
            print("Cleaning up...")
            
            # Clean up world
            if hasattr(self, 'world') and self.world:
                self.world.cleanup()
                self.world = None
                
            # Clean up screen manager
            if hasattr(self, 'screen_manager'):
                self.screen_manager.cleanup()
                self.screen_manager = None
                
            # Clean up pygame
            pygame.quit()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            traceback.print_exc()
            
    def create_world(self):
        """Create new world instance"""
        try:
            if self.world:
                self.world.cleanup()
            self.world = World()
            return True
        except Exception as e:
            print(f"Error creating world: {e}")
            traceback.print_exc()
            return False

if __name__ == "__main__":
    game = Game()
    game.run() 