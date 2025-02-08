import pygame
import math
import random
from typing import Dict, List, Optional, Tuple
from ..constants import ENTITY_TYPES, ENTITY_STATES, ENTITY_NEEDS, THOUGHT_TYPES, ANIMAL_TYPES
from .systems.thought_system import ThoughtSystem

class Entity:
    def __init__(self, world, x: float = 0, y: float = 0):
        """Initialize entity"""
        self.world = world
        self.x = float(x)
        self.y = float(y)
        self.size = 32  # Default size
        self.state = {'active': True}
        self.type = 'generic'
        self.subtype = 'none'
        
        # Get emoji from entity types
        if hasattr(self, 'type') and self.type in ENTITY_TYPES:
            self.emoji = ENTITY_TYPES[self.type].get('sprite', '❓')
        elif hasattr(self, 'subtype') and self.subtype in ANIMAL_TYPES:
            self.emoji = ANIMAL_TYPES[self.subtype].get('sprite', '🐾')
        else:
            self.emoji = '❓'  # Default emoji
            
        self.surface = None
        self.needs_update = True
        
        # Initialize surface
        self._init_surface()
        
    def _init_surface(self):
        """Initialize entity surface with emoji sprite"""
        try:
            # Create surface for emoji
            font_size = int(self.size * 0.8)  # Slightly smaller than entity size
            font = pygame.font.SysFont('segoe ui emoji', font_size)
            
            # Render emoji
            text_surface = font.render(self.emoji, True, (0, 0, 0))
            
            # Create entity surface with alpha
            self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Center emoji on surface
            x = (self.size - text_surface.get_width()) // 2
            y = (self.size - text_surface.get_height()) // 2
            self.surface.blit(text_surface, (x, y))
            
            self.needs_update = False
            
        except Exception as e:
            print(f"Error initializing entity surface: {e}")
            import traceback
            traceback.print_exc()
            
    def update(self, world, dt):
        """Update entity state"""
        try:
            # Update position
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt
            
            # Update state timer
            if self.state_timer > 0:
                self.state_timer -= dt
                if self.state_timer <= 0:
                    self.state = 'idle'
            
            # Update needs
            for need, value in self.needs.items():
                if need in ENTITY_NEEDS:
                    decay = ENTITY_NEEDS[need]['decay_rate'] * dt
                    self.needs[need] = max(0, min(100, value - decay))
            
            # Update systems
            for system in self.systems.values():
                if hasattr(system, 'update'):
                    system.update(dt)
                
            # Update animation
            self.animation_timer += dt
            if self.animation_timer >= 0.2:  # Animation frame duration
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % \
                    ENTITY_TYPES[self.type]['animation_frames']
                
        except Exception as e:
            print(f"Error updating entity: {e}")
            import traceback
            traceback.print_exc()
            
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, camera_zoom: float):
        """Draw entity with all visual effects"""
        try:
            if self.needs_update:
                self._init_surface()
                
            # Calculate screen position
            screen_x = (self.x - camera_x) * camera_zoom + screen.get_width()/2
            screen_y = (self.y - camera_y) * camera_zoom + screen.get_height()/2
            
            # Scale surface based on zoom
            scaled_size = int(self.size * camera_zoom)
            if scaled_size < 1:
                return
                
            scaled_surface = pygame.transform.scale(self.surface, (scaled_size, scaled_size))
            
            # Draw entity
            screen.blit(scaled_surface, (screen_x - scaled_size//2, screen_y - scaled_size//2))
            
            # Draw health bar if entity has health
            if hasattr(self, 'health') and hasattr(self, 'max_health'):
                self._draw_health_bar(screen, screen_x, screen_y, scaled_size)
                
            # Draw status effects
            if hasattr(self, 'status_effects'):
                self._draw_status_effects(screen, screen_x, screen_y, scaled_size)
                
        except Exception as e:
            print(f"Error drawing entity: {e}")
            import traceback
            traceback.print_exc()
            
    def _draw_health_bar(self, screen, screen_x, screen_y, scaled_size):
        """Draw health bar above entity"""
        try:
            # Calculate health bar width
            health_bar_width = int(scaled_size * (self.health / self.max_health))
            
            # Create health bar surface
            health_bar_surface = pygame.Surface((health_bar_width, 5), pygame.SRCALPHA)
            pygame.draw.rect(health_bar_surface, (0, 255, 0), (0, 0, health_bar_width, 5))
            
            # Draw health bar
            screen.blit(health_bar_surface, (screen_x - scaled_size//2, screen_y - scaled_size//2 - 10))
            
        except Exception as e:
            print(f"Error drawing health bar: {e}")
            import traceback
            traceback.print_exc()
            
    def _draw_status_effects(self, screen, screen_x, screen_y, scaled_size):
        """Draw status effects above entity"""
        try:
            # Implementation of drawing status effects
            pass
        except Exception as e:
            print(f"Error drawing status effects: {e}")
            import traceback
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up entity resources"""
        try:
            # Clean up systems
            for system in self.systems.values():
                if hasattr(system, 'cleanup'):
                    system.cleanup()
            self.systems.clear()
            
            # Clean up surfaces
            self.surface = None
            
        except Exception as e:
            print(f"Error cleaning up entity: {e}")
            import traceback
            traceback.print_exc()