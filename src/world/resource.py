import pygame
import random
import math
from typing import Dict, Optional, Tuple
from ..constants import (
    RESOURCE_TYPES, TILE_SIZE, SEASONS,
    WEATHER_EFFECTS, BIOMES
)

class Resource:
    def __init__(self, world, position: Tuple[float, float], resource_type: str):
        """Initialize a resource with advanced features"""
        self.world = world
        self.x, self.y = position
        self.type = resource_type
        self.id = f"resource_{id(self)}"  # Unique identifier
        
        # Get base properties
        self.properties = RESOURCE_TYPES[resource_type].copy()
        self.sprite = self.properties['sprite']
        
        # Resource properties
        self.max_quantity = self.properties['max_quantity']
        self.quantity = random.uniform(self.max_quantity * 0.5, self.max_quantity)
        self.regeneration_rate = self.properties.get('regeneration_rate', 0)
        self.growth_rate = self.properties.get('growth_rate', 0)
        
        # Quality and value
        self.quality = random.uniform(0.7, 1.0)  # Resource quality (affects value)
        self.base_value = self.properties.get('value', 1.0)
        
        # Visual properties
        self.size = TILE_SIZE
        self.scale = max(0.5, min(1.0, self.quantity / self.max_quantity))
        self.color = (255, 255, 255)  # Base color for tinting
        self.animation_offset = random.uniform(0, math.pi * 2)  # For visual effects
        
        # State
        self.is_active = True
        self.is_depleted = False
        self.depletion_time = 0  # Time when resource was depleted
        self.last_harvest_time = 0  # Time of last harvest
        self.times_harvested = 0  # Track harvest count
        
        # Environmental influence
        self.biome = self._get_current_biome()
        self.seasonal_modifiers = self._calculate_seasonal_modifiers()
        self.weather_resistance = random.uniform(0.7, 1.0)  # Resistance to weather effects
        
        # Interaction
        self.current_users = set()  # Track entities currently using this resource
        self.total_harvested = 0  # Total amount harvested from this resource
        
    def update(self, dt: float) -> bool:
        """Update resource state with enhanced features"""
        if not self.is_active:
            return True
            
        try:
            current_time = self.world.time
            
            # Update seasonal modifiers
            if self.world.current_season != self._get_current_season():
                self.seasonal_modifiers = self._calculate_seasonal_modifiers()
                
            if self.is_depleted:
                # Check if enough time has passed for regeneration
                if self.regeneration_rate > 0:
                    time_since_depletion = current_time - self.depletion_time
                    if time_since_depletion > self._get_regeneration_delay():
                        regeneration_amount = self._calculate_regeneration_rate(dt)
                        self.quantity += regeneration_amount
                        
                        if self.quantity >= self.max_quantity * 0.1:  # 10% threshold
                            self.is_depleted = False
                            self._update_visual_properties()
            else:
                # Natural growth with environmental factors
                if self.growth_rate > 0 and self.quantity < self.max_quantity:
                    growth_amount = self._calculate_growth_rate(dt)
                    self.quantity = min(self.max_quantity, self.quantity + growth_amount)
                    self._update_visual_properties()
                    
                # Apply weather effects
                self._apply_weather_effects(dt)
                
            # Update animation
            self.animation_offset = (self.animation_offset + dt) % (math.pi * 2)
            
            return False
            
        except Exception as e:
            print(f"Error updating resource: {e}")
            return False
            
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], zoom: float, effects: Dict = None):
        """Draw the resource with enhanced visuals"""
        if not self.is_active:
            return
            
        try:
            # Calculate screen position
            screen_x = int((self.x - camera_pos[0]) * zoom)
            screen_y = int((self.y - camera_pos[1]) * zoom)
            
            # Apply visual effects
            current_scale = self.scale * (1 + math.sin(self.animation_offset) * 0.05)
            current_color = self._get_display_color(effects)
            
            # Draw sprite/emoji with effects
            if isinstance(self.sprite, str):  # Emoji fallback
                font = pygame.font.SysFont('segoe ui emoji', int(self.size * zoom * current_scale))
                text = font.render(self.sprite, True, current_color)
                text_rect = text.get_rect(center=(screen_x, screen_y))
                surface.blit(text, text_rect)
            else:  # Image sprite
                scaled_size = (
                    int(self.size * zoom * current_scale),
                    int(self.size * zoom * current_scale)
                )
                scaled_sprite = pygame.transform.scale(self.sprite, scaled_size)
                tinted_sprite = self._apply_color_tint(scaled_sprite, current_color)
                sprite_rect = tinted_sprite.get_rect(center=(screen_x, screen_y))
                surface.blit(tinted_sprite, sprite_rect)
                
            # Draw quantity indicator
            if not self.is_depleted:
                self._draw_quantity_indicator(surface, (screen_x, screen_y), zoom)
                
            # Draw interaction indicator
            if self.current_users:
                self._draw_interaction_indicator(surface, (screen_x, screen_y), zoom)
                
        except Exception as e:
            print(f"Error drawing resource: {e}")
            
    def harvest(self, amount: float, harvester=None) -> float:
        """Harvest resource with enhanced features"""
        if self.is_depleted or not self.is_active:
            return 0
            
        try:
            current_time = self.world.time
            
            # Calculate actual harvest amount with modifiers
            efficiency = self._calculate_harvest_efficiency(harvester)
            max_harvest = self.quantity * efficiency
            harvested = min(amount, max_harvest)
            
            # Update resource state
            self.quantity -= harvested
            self.total_harvested += harvested
            self.times_harvested += 1
            self.last_harvest_time = current_time
            
            # Track user
            if harvester:
                self.current_users.add(harvester.id)
                
            # Check for depletion
            if self.quantity <= 0:
                self.quantity = 0
                self.is_depleted = True
                self.depletion_time = current_time
                
            # Update visual properties
            self._update_visual_properties()
            
            return harvested
            
        except Exception as e:
            print(f"Error harvesting resource: {e}")
            return 0
            
    def get_info(self) -> Dict:
        """Get detailed resource information"""
        try:
            return {
                'id': self.id,
                'type': self.type,
                'quantity': self.quantity,
                'max_quantity': self.max_quantity,
                'quality': self.quality,
                'value': self._calculate_current_value(),
                'is_depleted': self.is_depleted,
                'position': (self.x, self.y),
                'biome': self.biome,
                'seasonal_modifiers': self.seasonal_modifiers,
                'times_harvested': self.times_harvested,
                'total_harvested': self.total_harvested,
                'current_users': len(self.current_users)
            }
            
        except Exception as e:
            print(f"Error getting resource info: {e}")
            return {'type': self.type, 'error': str(e)}
            
    def _get_current_biome(self) -> str:
        """Get the biome at resource's location"""
        try:
            chunk_x = int(self.x // (TILE_SIZE * self.world.chunk_size))
            chunk_y = int(self.y // (TILE_SIZE * self.world.chunk_size))
            
            if (chunk_x, chunk_y) in self.world.chunks:
                chunk = self.world.chunks[(chunk_x, chunk_y)]
                tile_x = int((self.x % (TILE_SIZE * self.world.chunk_size)) // TILE_SIZE)
                tile_y = int((self.y % (TILE_SIZE * self.world.chunk_size)) // TILE_SIZE)
                return chunk.tiles[tile_y][tile_x]['biome']
                
            return 'plains'  # Default
            
        except Exception as e:
            print(f"Error getting current biome: {e}")
            return 'plains'
            
    def _get_current_season(self) -> str:
        """Get current season"""
        return self.world.current_season
        
    def _calculate_seasonal_modifiers(self) -> Dict[str, float]:
        """Calculate seasonal influence on resource"""
        try:
            modifiers = {
                'growth_rate': 1.0,
                'regeneration_rate': 1.0,
                'quality': 1.0
            }
            
            season_data = SEASONS[self.world.current_season]
            
            # Apply season-specific modifiers
            if self.type in ['wood', 'food']:
                modifiers['growth_rate'] = season_data['growth_mod']
                if self.world.current_season == 'Winter':
                    modifiers['quality'] = 0.8
                elif self.world.current_season == 'Summer':
                    modifiers['quality'] = 1.2
                    
            elif self.type in ['stone', 'ore']:
                # Less affected by seasons
                modifiers['regeneration_rate'] = 0.9 + season_data['precipitation'] * 0.2
                
            return modifiers
            
        except Exception as e:
            print(f"Error calculating seasonal modifiers: {e}")
            return {'growth_rate': 1.0, 'regeneration_rate': 1.0, 'quality': 1.0}
            
    def _calculate_regeneration_rate(self, dt: float) -> float:
        """Calculate actual regeneration rate with modifiers"""
        try:
            base_rate = self.regeneration_rate * dt
            
            # Apply modifiers
            rate = base_rate * self.seasonal_modifiers['regeneration_rate']
            
            # Biome influence
            if self.biome in BIOMES:
                rate *= BIOMES[self.biome].get('fertility', 1.0)
                
            return max(0, rate)
            
        except Exception as e:
            print(f"Error calculating regeneration rate: {e}")
            return 0
            
    def _calculate_growth_rate(self, dt: float) -> float:
        """Calculate actual growth rate with modifiers"""
        try:
            base_rate = self.growth_rate * dt
            
            # Apply modifiers
            rate = base_rate * self.seasonal_modifiers['growth_rate']
            
            # Weather influence
            weather_effects = WEATHER_EFFECTS.get(self.world.current_weather, {})
            if 'growth_mod' in weather_effects:
                rate *= weather_effects['growth_mod']
                
            return max(0, rate)
            
        except Exception as e:
            print(f"Error calculating growth rate: {e}")
            return 0
            
    def _calculate_harvest_efficiency(self, harvester) -> float:
        """Calculate harvest efficiency based on various factors"""
        try:
            base_efficiency = 0.8  # Base efficiency
            
            if harvester:
                # Consider harvester's skills
                if hasattr(harvester, 'skills'):
                    if self.type == 'wood' and 'woodcutting' in harvester.skills:
                        base_efficiency += harvester.skills['woodcutting'] * 0.1
                    elif self.type == 'ore' and 'mining' in harvester.skills:
                        base_efficiency += harvester.skills['mining'] * 0.1
                        
            # Weather penalty
            weather_effects = WEATHER_EFFECTS.get(self.world.current_weather, {})
            if 'harvest_mod' in weather_effects:
                base_efficiency *= weather_effects['harvest_mod']
                
            return max(0.1, min(1.0, base_efficiency))
            
        except Exception as e:
            print(f"Error calculating harvest efficiency: {e}")
            return 0.8
            
    def _calculate_current_value(self) -> float:
        """Calculate current resource value"""
        try:
            base_value = self.base_value * self.quality
            
            # Quantity influence
            quantity_factor = self.quantity / self.max_quantity
            
            # Rarity factor (more valuable when depleted)
            rarity_factor = 1.0 + max(0, (1 - quantity_factor) * 0.5)
            
            # Season influence
            season_factor = self.seasonal_modifiers['quality']
            
            return base_value * quantity_factor * rarity_factor * season_factor
            
        except Exception as e:
            print(f"Error calculating current value: {e}")
            return self.base_value
            
    def _get_regeneration_delay(self) -> float:
        """Calculate delay before regeneration starts"""
        try:
            base_delay = 60.0  # Base delay in seconds
            
            # More harvests = longer delay
            harvest_factor = min(2.0, 1.0 + (self.times_harvested * 0.1))
            
            # Season influence
            season_data = SEASONS[self.world.current_season]
            season_factor = 1.0 / season_data['growth_mod']
            
            return base_delay * harvest_factor * season_factor
            
        except Exception as e:
            print(f"Error calculating regeneration delay: {e}")
            return 60.0
            
    def _apply_weather_effects(self, dt: float):
        """Apply weather effects to resource"""
        try:
            weather = self.world.current_weather
            if weather in ['storm', 'rain']:
                # Damage based on weather resistance
                damage = (1 - self.weather_resistance) * dt
                if weather == 'storm':
                    damage *= 2
                    
                self.quantity = max(0, self.quantity - damage)
                if self.quantity <= 0:
                    self.is_depleted = True
                    self.depletion_time = self.world.time
                    
        except Exception as e:
            print(f"Error applying weather effects: {e}")
            
    def _update_visual_properties(self):
        """Update visual properties based on current state"""
        try:
            # Update scale based on quantity
            self.scale = max(0.5, min(1.0, self.quantity / self.max_quantity))
            
            # Update color based on quality and season
            r = g = b = 255
            if self.quality < 0.8:
                r = g = b = int(200 + self.quality * 50)
            elif self.quality > 1.0:
                g = b = int(255 - (self.quality - 1.0) * 50)
                
            self.color = (r, g, b)
            
        except Exception as e:
            print(f"Error updating visual properties: {e}")
            
    def _get_display_color(self, effects: Dict = None) -> Tuple[int, int, int]:
        """Get current display color with effects"""
        try:
            base_color = self.color
            
            # Apply weather effects
            if effects and 'visibility' in effects:
                visibility = effects['visibility']
                return tuple(int(c * visibility) for c in base_color)
                
            return base_color
            
        except Exception as e:
            print(f"Error getting display color: {e}")
            return (255, 255, 255)
            
    def _apply_color_tint(self, surface: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        """Apply color tint to surface"""
        try:
            tinted = surface.copy()
            tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
            return tinted
            
        except Exception as e:
            print(f"Error applying color tint: {e}")
            return surface
            
    def _draw_quantity_indicator(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw resource quantity indicator"""
        try:
            bar_width = 20 * zoom
            bar_height = 3 * zoom
            y_offset = -10 * zoom
            
            # Draw background
            pygame.draw.rect(surface, (50, 50, 50),
                           (pos[0] - bar_width/2, pos[1] + y_offset,
                            bar_width, bar_height))
                            
            # Draw fill
            fill_width = bar_width * (self.quantity / self.max_quantity)
            if fill_width > 0:
                pygame.draw.rect(surface, (100, 200, 100),
                               (pos[0] - bar_width/2, pos[1] + y_offset,
                                fill_width, bar_height))
                                
        except Exception as e:
            print(f"Error drawing quantity indicator: {e}")
            
    def _draw_interaction_indicator(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw indicator when resource is being used"""
        try:
            radius = 5 * zoom
            angle = self.animation_offset * 2
            
            # Draw spinning dots
            for i in range(3):
                dot_angle = angle + (i * math.pi * 2 / 3)
                dot_x = pos[0] + math.cos(dot_angle) * radius
                dot_y = pos[1] + math.sin(dot_angle) * radius
                pygame.draw.circle(surface, (255, 255, 255),
                                 (int(dot_x), int(dot_y)), int(2 * zoom))
                                 
        except Exception as e:
            print(f"Error drawing interaction indicator: {e}")
            
    def cleanup(self):
        """Clean up resource"""
        try:
            self.is_active = False
            self.world = None
            self.current_users.clear()
            
        except Exception as e:
            print(f"Error cleaning up resource: {e}") 