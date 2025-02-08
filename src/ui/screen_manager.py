import pygame
import traceback
from typing import Dict, Optional
from ..constants import SCREEN_STATES, UI_COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, FONTS
from .screens.main_menu_screen import MainMenuScreen
from .screens.world_gen_screen import WorldGenScreen
from .screens.game_screen import GameScreen
from .screens.pause_screen import PauseScreen
from .screens.options_screen import OptionsScreen
from .screen import Screen

class ScreenManager:
    def __init__(self, game):
        """Initialize screen manager"""
        self.game = game
        self.screens = {}
        self.current_screen = None
        self.previous_screen = None
        self._initialize_screens()
        
    def _initialize_screens(self):
        """Initialize all game screens"""
        try:
            # Create screen instances with screen_manager reference
            self.screens = {
                'mainmenu': MainMenuScreen(self),
                'game': GameScreen(self),
                'pause': PauseScreen(self),
                'options': OptionsScreen(self),
                'world_gen': WorldGenScreen(self)
            }
            
            # Set initial screen
            self.set_current_screen('mainmenu')
            
        except Exception as e:
            print(f"Error initializing screens: {e}")
            traceback.print_exc()
            
    def add_screen(self, screen_name: str, screen_instance: Screen):
        """Add a new screen to the manager"""
        try:
            if screen_name in self.screens:
                print(f"Warning: Replacing existing screen '{screen_name}'")
            self.screens[screen_name] = screen_instance
            print(f"Added screen: {screen_name}")
        except Exception as e:
            print(f"Error adding screen: {e}")
            import traceback
            traceback.print_exc()
            
    def set_current_screen(self, screen_name: str):
        """Set the current screen"""
        try:
            if screen_name not in self.screens:
                raise ValueError(f"Screen '{screen_name}' not found")
                
            # Exit current screen
            if self.current_screen:
                self.current_screen.on_exit()
                self.previous_screen = self.current_screen
                
            # Enter new screen
            self.current_screen = self.screens[screen_name]
            self.current_screen.on_enter(self.previous_screen)
            
        except Exception as e:
            print(f"Error setting screen: {e}")
            import traceback
            traceback.print_exc()
            
    def switch_screen(self, screen_name: str):
        """Switch to another screen"""
        self.set_current_screen(screen_name)
        
    def update(self, dt: float):
        """Update current screen"""
        try:
            if self.current_screen:
                self.current_screen.update(dt)
                
        except Exception as e:
            print(f"Error updating screen: {e}")
            
    def draw(self, surface: pygame.Surface):
        """Draw current screen"""
        try:
            if self.current_screen:
                self.current_screen.draw(surface)
                
        except Exception as e:
            print(f"Error drawing screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle events for current screen"""
        try:
            if self.current_screen:
                self.current_screen.handle_event(event)
                
        except Exception as e:
            print(f"Error handling event: {e}")
            
    def quit_game(self):
        """Quit the game"""
        try:
            if self.current_screen:
                self.current_screen.on_exit()
            self.game.quit()
            
        except Exception as e:
            print(f"Error quitting game: {e}")
            
    def return_to_previous_screen(self):
        """Return to the previous screen"""
        try:
            if self.previous_screen:
                self.set_current_screen(self.previous_screen.__class__.__name__.lower().replace('screen', ''))
                
        except Exception as e:
            print(f"Error returning to previous screen: {e}")
            
    def cleanup(self):
        """Clean up all screen resources"""
        try:
            # Clean up each screen
            for screen in self.screens.values():
                if hasattr(screen, 'cleanup'):
                    screen.cleanup()
            
            # Clear screen references
            self.screens.clear()
            self.current_screen = None
            self.previous_screen = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Error during screen manager cleanup: {e}")
            import traceback
            traceback.print_exc() 