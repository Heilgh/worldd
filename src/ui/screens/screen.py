import pygame
import traceback
from typing import Optional

class Screen:
    def __init__(self, game):
        """Initialize base screen"""
        self.game = game
        self.initialized = False
        
    def initialize(self):
        """Initialize screen resources"""
        try:
            if not self.initialized:
                self._init_resources()
                self.initialized = True
                
        except Exception as e:
            print(f"Error initializing screen: {e}")
            traceback.print_exc()
            
    def _init_resources(self):
        """Initialize screen-specific resources"""
        pass
        
    def update(self, dt: float):
        """Update screen state"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error updating screen: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface):
        """Draw the screen"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error drawing screen: {e}")
            traceback.print_exc()
            
    def handle_event(self, event: pygame.event.Event):
        """Handle an event"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error handling event: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up screen resources"""
        try:
            self.initialized = False
            
        except Exception as e:
            print(f"Error cleaning up screen: {e}")
            traceback.print_exc()
            
    def on_enter(self):
        """Called when entering this screen"""
        try:
            if not self.initialized:
                self.initialize()
                
        except Exception as e:
            print(f"Error entering screen: {e}")
            traceback.print_exc()
            
    def on_exit(self):
        """Called when exiting this screen"""
        try:
            pass
            
        except Exception as e:
            print(f"Error exiting screen: {e}")
            traceback.print_exc() 