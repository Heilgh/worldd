import pygame
import traceback
from typing import Optional

class Screen:
    """Base class for game screens"""
    def __init__(self, screen_manager):
        """Initialize base screen"""
        try:
            self.screen_manager = screen_manager
            self.game = screen_manager.game if hasattr(screen_manager, 'game') else None
            self.initialized = False
            self.active = False
            self.transition_alpha = 255
            self.transition_speed = 5
            self.transition_direction = -1  # -1 for fade in, 1 for fade out
            
        except Exception as e:
            print(f"Error initializing screen: {e}")
            traceback.print_exc()
            
    def initialize(self):
        """Initialize screen resources"""
        try:
            if not self.initialized:
                self._init_resources()
                self.initialized = True
                print(f"{self.__class__.__name__} initialized successfully")
                
        except Exception as e:
            print(f"Error initializing {self.__class__.__name__} resources: {e}")
            traceback.print_exc()
            
    def _init_resources(self):
        """Initialize screen-specific resources"""
        # Override in child classes
        pass
        
    def update(self, dt: float):
        """Update screen state"""
        try:
            if not self.initialized:
                self.initialize()
                
            # Handle screen transition effects
            if self.transition_alpha > 0 and self.transition_direction < 0:
                self.transition_alpha = max(0, self.transition_alpha - self.transition_speed)
            elif self.transition_alpha < 255 and self.transition_direction > 0:
                self.transition_alpha = min(255, self.transition_alpha + self.transition_speed)
                
        except Exception as e:
            print(f"Error updating {self.__class__.__name__}: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface):
        """Draw the screen"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error drawing {self.__class__.__name__}: {e}")
            traceback.print_exc()
            
    def handle_event(self, event: pygame.event.Event):
        """Handle an event"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error handling event in {self.__class__.__name__}: {e}")
            traceback.print_exc()
            
    def on_enter(self, previous_screen: Optional['Screen'] = None):
        """Called when entering this screen"""
        try:
            print(f"Entering {self.__class__.__name__}...")
            self.active = True
            self.initialized = True
            self.transition_alpha = 255
            self.transition_direction = -1
            
        except Exception as e:
            print(f"Error entering {self.__class__.__name__}: {e}")
            traceback.print_exc()
            
    def on_exit(self):
        """Called when exiting this screen"""
        try:
            print(f"Exiting {self.__class__.__name__}...")
            self.active = False
            self.transition_direction = 1
            
        except Exception as e:
            print(f"Error exiting {self.__class__.__name__}: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up screen resources"""
        try:
            print(f"Cleaning up {self.__class__.__name__}...")
            self.initialized = False
            self.active = False
            
        except Exception as e:
            print(f"Error cleaning up {self.__class__.__name__}: {e}")
            traceback.print_exc() 