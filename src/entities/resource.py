import pygame
import random
import traceback
import math
from typing import Dict, List, Optional, Tuple
from ..constants import RESOURCE_TYPES, TILE_SIZE, BIOMES, SEASONS, WEATHER_EFFECTS

class Resource:
    def __init__(self, world, pos: Tuple[float, float], resource_type: str):
        """Initialize resource entity"""
        try:
            print(f"Creating {resource_type} at position {pos}")
            self.world = world
            self.x, self.y = pos
            self.type = resource_type
            self.id = f"resource_{id(self)}"
            
            # Get resource properties from constants
            if resource_type not in RESOURCE_TYPES:
                raise ValueError(f"Invalid resource type: {resource_type}")
            
            self.properties = RESOURCE_TYPES[resource_type].copy()
            
            # Basic attributes
            self.size = TILE_SIZE
            self.max_quantity = self.properties['max_quantity']
            self.quantity = random.randint(int(self.max_quantity * 0.5), self.max_quantity)
            self.regeneration_rate = self.properties.get('regeneration_rate', 0.1)
            self.growth_rate = self.properties.get('growth_rate', 0)
            self.hardness = self.properties.get('hardness', 1)
            self.value = self.properties.get('value', 1)
            self.tool_required = self.properties.get('tool_required', None)
            
            # State tracking
            self.is_active = True
            self.is_depleted = False
            self.last_interaction_time = 0
            self.times_harvested = 0
            self.total_harvested = 0
            self.depletion_time = 0
            self.current_users = set()
            
            # Visual properties
            self.sprite = None
            if 'sprite' in self.properties:
                try:
                    self.sprite = pygame.image.load(self.properties['sprite']).convert_alpha()
                except Exception as e:
                    print(f"Failed to load sprite {self.properties['sprite']}: {e}")
            
            self.growth_stage = 1.0
            self.scale = max(0.5, min(1.0, self.quantity / self.max_quantity))
            self.animation_offset = random.uniform(0, math.pi * 2)
            
            # Environmental properties
            self.biome = self._get_current_biome()
            self.seasonal_modifiers = self._calculate_seasonal_modifiers()
            self.weather_resistance = random.uniform(0.7, 1.0)
            
            print(f"{resource_type} created successfully at {pos}")
            
        except Exception as e:
            print(f"Error creating resource: {e}")
            traceback.print_exc()
            raise
            
    def update(self, dt: float):
        """Update resource state"""
        try:
            # Regenerate resources over time
            if self.quantity < self.max_quantity:
                self.quantity = min(
                    self.max_quantity,
                    self.quantity + self.regeneration_rate * dt
                )
                
            # Update growth stage for plants
            if 'growth_rate' in self.properties:
                self.growth_stage = min(1.0, self.growth_stage + dt * self.properties['growth_rate'])
                
        except Exception as e:
            print(f"Error updating resource: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], zoom: float):
        """Draw resource entity"""
        try:
            # Calculate screen position
            screen_x = (self.x - camera_pos[0]) * zoom
            screen_y = (self.y - camera_pos[1]) * zoom
            
            # Draw resource
            if self.sprite:
                # Scale sprite based on growth stage for plants
                scale = self.growth_stage if 'growth_rate' in self.properties else 1.0
                scaled_size = (int(self.size * zoom * scale), int(self.size * zoom * scale))
                scaled_sprite = pygame.transform.scale(self.sprite, scaled_size)
                surface.blit(scaled_sprite, (screen_x, screen_y))
            else:
                # Fallback: Draw colored rectangle
                color = self._get_color()
                size = int(self.size * zoom)
                pygame.draw.rect(surface, color, (screen_x, screen_y, size, size))
                
            # Draw quantity indicator
            if self.quantity < self.max_quantity:
                self._draw_quantity_bar(surface, (screen_x, screen_y), zoom)
                
        except Exception as e:
            print(f"Error drawing resource: {e}")
            traceback.print_exc()
            
    def interact(self, entity, interaction_type: str) -> float:
        """Handle interaction with entity"""
        try:
            current_time = pygame.time.get_ticks() / 1000
            
            # Check cooldown
            if current_time - self.last_interaction_time < 1.0:
                return 0
                
            self.last_interaction_time = current_time
            
            if interaction_type == 'gather':
                return self._handle_gather(entity)
            elif interaction_type == 'use':
                return self._handle_use(entity)
                
            return 0
            
        except Exception as e:
            print(f"Error handling interaction: {e}")
            traceback.print_exc()
            return 0
            
    def _handle_gather(self, entity) -> float:
        """Handle gathering interaction"""
        try:
            if self.quantity <= 0:
                return 0
                
            # Calculate gather amount based on entity skills if applicable
            base_amount = 10
            if hasattr(entity, 'skills') and 'gathering' in entity.skills:
                base_amount *= (1 + entity.skills['gathering'] / 100)
                
            # Limit by available quantity
            gather_amount = min(base_amount, self.quantity)
            self.quantity -= gather_amount
            
            return gather_amount
            
        except Exception as e:
            print(f"Error handling gather: {e}")
            traceback.print_exc()
            return 0
            
    def _handle_use(self, entity) -> float:
        """Handle use interaction"""
        try:
            if self.quantity <= 0:
                return 0
                
            # Default use amount
            use_amount = 1
            self.quantity = max(0, self.quantity - use_amount)
            
            return use_amount
            
        except Exception as e:
            print(f"Error handling use: {e}")
            traceback.print_exc()
            return 0
            
    def _get_color(self) -> Tuple[int, int, int]:
        """Get color based on resource type"""
        try:
            if 'tree' in self.type or 'plant' in self.type:
                return (34, 139, 34)  # Forest green
            elif 'rock' in self.type or 'ore' in self.type:
                return (169, 169, 169)  # Dark gray
            elif 'water' in self.type:
                return (0, 191, 255)  # Deep sky blue
            elif 'food' in self.type:
                return (255, 140, 0)  # Dark orange
            else:
                return (139, 69, 19)  # Saddle brown
                
        except Exception as e:
            print(f"Error getting resource color: {e}")
            traceback.print_exc()
            return (128, 128, 128)  # Gray fallback
            
    def _draw_quantity_bar(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw resource quantity indicator"""
        try:
            bar_width = self.size * zoom
            bar_height = 4 * zoom
            bar_y_offset = -8 * zoom
            
            # Background
            pygame.draw.rect(surface, (64, 64, 64),
                (pos[0], pos[1] + bar_y_offset, bar_width, bar_height))
                
            # Fill bar
            fill_width = bar_width * (self.quantity / self.max_quantity)
            if fill_width > 0:
                pygame.draw.rect(surface, (0, 255, 0),
                    (pos[0], pos[1] + bar_y_offset, fill_width, bar_height))
                    
        except Exception as e:
            print(f"Error drawing quantity bar: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up resource"""
        try:
            print(f"Cleaning up resource {self.type}")
            self.world = None
            if self.sprite:
                del self.sprite
                
        except Exception as e:
            print(f"Error cleaning up resource: {e}")
            traceback.print_exc()