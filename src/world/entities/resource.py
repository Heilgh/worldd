import pygame
import random
from typing import Tuple, Optional, Dict, Any

from .entity import Entity
from ...constants import RESOURCE_TYPES, TILE_SIZE, UI_COLORS

class Resource(Entity):
    def __init__(self, world, position: Tuple[float, float], resource_type: str):
        """Initialize a resource entity"""
        super().__init__(world, position)
        
        # Resource properties
        self.type = 'resource'
        self.resource_type = resource_type
        self.size = TILE_SIZE / 2
        self.quantity = random.randint(5, 20)  # Random initial quantity
        
        # Get resource type data
        resource_data = RESOURCE_TYPES.get(resource_type, {})
        self.max_quantity = resource_data.get('max_quantity', 20)
        self.respawn_time = resource_data.get('respawn_time', 300)  # Time to respawn in seconds
        self.last_harvest = 0
        self.color = resource_data.get('color', UI_COLORS['resource_default'])
        
        # Visual properties
        self.sprite = None
        self._init_sprite()
    
    def _init_sprite(self):
        """Initialize the resource sprite"""
        try:
            # Create a simple colored circle for now
            size = int(self.size * 2)
            self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, self.color, (size//2, size//2), size//2)
        except Exception as e:
            print(f"Error initializing resource sprite: {e}")
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw the resource"""
        try:
            if not self.sprite:
                return
                
            # Calculate screen position
            screen_x = (self.x - camera_x) * zoom + screen.get_width() / 2
            screen_y = (self.y - camera_y) * zoom + screen.get_height() / 2
            
            # Scale sprite based on zoom
            scaled_size = int(self.size * 2 * zoom)
            if scaled_size > 0:
                scaled_sprite = pygame.transform.scale(self.sprite, (scaled_size, scaled_size))
                screen.blit(scaled_sprite, (screen_x - scaled_size//2, screen_y - scaled_size//2))
                
                # Draw quantity if resource is selected
                if self.world.selected_entity == self:
                    font = pygame.font.Font(None, int(24 * zoom))
                    text = font.render(str(self.quantity), True, UI_COLORS['text_highlight'])
                    text_rect = text.get_rect(center=(screen_x, screen_y - scaled_size))
                    screen.blit(text, text_rect)
        
        except Exception as e:
            print(f"Error drawing resource: {e}")
    
    def update(self, dt: float):
        """Update resource state"""
        try:
            super().update(dt)
            
            # Check for respawn
            current_time = self.world.time_system.get_time()
            if self.quantity < self.max_quantity and (current_time - self.last_harvest) > self.respawn_time:
                self.quantity = min(self.quantity + 1, self.max_quantity)
                self.last_harvest = current_time
        
        except Exception as e:
            print(f"Error updating resource: {e}")
    
    def harvest(self, amount: int) -> int:
        """Harvest a specified amount from the resource"""
        try:
            if amount <= 0:
                return 0
                
            harvested = min(self.quantity, amount)
            self.quantity -= harvested
            self.last_harvest = self.world.time_system.get_time()
            
            # Remove resource if depleted
            if self.quantity <= 0:
                self.world.remove_entity(self)
            
            return harvested
            
        except Exception as e:
            print(f"Error harvesting resource: {e}")
            return 0
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the resource"""
        return {
            'type': self.type,
            'resource_type': self.resource_type,
            'quantity': self.quantity,
            'max_quantity': self.max_quantity,
            'position': (self.x, self.y)
        } 