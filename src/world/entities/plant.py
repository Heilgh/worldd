import random
import math
import pygame
from .entity import Entity
from ...constants import (
    PLANT_TYPES, BIOME_VEGETATION, SEASONS, SEASON_ORDER, TILE_SIZE, ENTITY_TYPES,
    BIOMES
)
from typing import Dict, List, Tuple, Optional
import traceback

class Plant(Entity):
    def __init__(self, world, x: float, y: float, plant_type: str = 'tree'):
        """Initialize a plant entity"""
        # Initialize type and basic properties before super().__init__
        self.type = 'plant'
        self.subtype = plant_type
        
        # Set health and stats before surface initialization
        self.health = 100.0
        self.max_health = 100.0
        self.size = 1.0
        self.max_size = random.uniform(0.8, 1.2)
        self.growth_rate = random.uniform(0.1, 0.3)
        self.color_variation = [random.randint(-20, 20) for _ in range(3)]
        
        # Set sprite based on type
        self.sprite = {
            'tree': '🌳',
            'bush': '🌿',
            'flower': '🌸',
            'grass': '🌱',
            'cactus': '🌵'
        }.get(plant_type, '🌱')
        
        # Initialize rect for UI and collision
        size = int(self.max_size * TILE_SIZE)
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        
        # Call parent constructor after setting required attributes
        super().__init__(world, x, y)
        
        # Initialize growth and health properties
        self.age = 0.0
        self.maturity = 0.0
        self.water_level = random.uniform(50.0, 80.0)
        self.nutrient_level = random.uniform(50.0, 80.0)
        
        # Environmental interaction
        self.sunlight_exposure = 1.0
        self.water_consumption = random.uniform(0.1, 0.3)
        self.nutrient_consumption = random.uniform(0.1, 0.2)
        
        # Reproduction
        self.reproduction_chance = 0.001
        self.reproduction_radius = random.uniform(2.0, 5.0)
        self.reproduction_cooldown = random.uniform(60.0, 180.0)
        self.last_reproduction = 0.0
        
        # Visual properties
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.5, 1.5)
        self.sway_amount = random.uniform(0.02, 0.05)
        
        # Initialize surface
        self._init_surface()
        
        # Update rect position
        self._update_rect()
        
        print(f"Created plant of type {plant_type} at position ({x}, {y})")
        
    def _init_surface(self):
        """Initialize the plant's surface for rendering"""
        size = int(self.max_size * TILE_SIZE)
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self._update_surface()
        
    def _update_surface(self):
        """Update the plant's surface based on current state"""
        if not hasattr(self, 'surface'):
            self._init_surface()
            
        size = int(self.size * TILE_SIZE)
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Calculate color based on health and season
        base_color = list(self.color_variation)
        for i in range(3):
            base_color[i] = max(0, min(255, base_color[i]))
            
        # Adjust color based on health
        health_factor = self.health / 100
        for i in range(3):
            base_color[i] = int(base_color[i] * health_factor)
            
        # Draw plant based on type
        if self.subtype == 'tree':
            self._draw_tree(base_color)
        elif self.subtype == 'bush':
            self._draw_bush(base_color)
        elif self.subtype == 'flower':
            self._draw_flower(base_color)
        elif self.subtype == 'cactus':
            self._draw_cactus(base_color)
        else:  # Default/grass
            self._draw_grass(base_color)
            
    def _draw_tree(self, color):
        """Draw a tree"""
        size = self.surface.get_width()
        # Draw trunk
        trunk_color = (139, 69, 19)  # Brown
        trunk_width = max(2, int(size * 0.2))
        trunk_height = int(size * 0.4)
        pygame.draw.rect(self.surface, trunk_color,
                        (size//2 - trunk_width//2,
                         size - trunk_height,
                         trunk_width, trunk_height))
        
        # Draw foliage
        foliage_radius = int(size * 0.4)
        pygame.draw.circle(self.surface, color,
                         (size//2, size - trunk_height),
                         foliage_radius)
        
    def _draw_bush(self, color):
        """Draw a bush"""
        size = self.surface.get_width()
        for _ in range(3):
            pos = (random.randint(0, size),
                  random.randint(int(size*0.3), size))
            radius = int(size * 0.3)
            pygame.draw.circle(self.surface, color, pos, radius)
            
    def _draw_flower(self, color):
        """Draw a flower"""
        size = self.surface.get_width()
        center = (size//2, size//2)
        
        # Draw stem
        stem_color = (0, 100, 0)
        pygame.draw.line(self.surface, stem_color,
                        (center[0], size),
                        (center[0], center[1]),
                        max(1, int(size * 0.1)))
        
        # Draw petals
        petal_color = (
            random.randint(200, 255),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        radius = int(size * 0.3)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = center[0] + math.cos(rad) * radius
            y = center[1] + math.sin(rad) * radius
            pygame.draw.circle(self.surface, petal_color,
                             (int(x), int(y)),
                             int(radius * 0.4))
            
        # Draw center
        pygame.draw.circle(self.surface, (255, 255, 0),
                         center, int(radius * 0.3))
            
    def _draw_cactus(self, color):
        """Draw a cactus"""
        size = self.surface.get_width()
        
        # Draw main body
        body_height = int(size * 0.8)
        body_width = int(size * 0.3)
        pygame.draw.rect(self.surface, color,
                        (size//2 - body_width//2,
                         size - body_height,
                         body_width, body_height))
        
        # Draw arms
        arm_length = int(size * 0.3)
        arm_width = int(body_width * 0.8)
        for side in [-1, 1]:
            x = size//2 + side * body_width//2
            y = size - int(body_height * 0.7)
            pygame.draw.rect(self.surface, color,
                           (x, y, side * arm_length, arm_width))
            
    def _draw_grass(self, color):
        """Draw grass"""
        size = self.surface.get_width()
        
        # Draw multiple blades
        for _ in range(5):
            start_x = random.randint(0, size)
            control_x = start_x + random.randint(-10, 10)
            end_x = start_x + random.randint(-5, 5)
            
            points = [
                (start_x, size),
                (control_x, size//2),
                (end_x, 0)
            ]
            pygame.draw.lines(self.surface, color, False, points,
                            max(1, int(size * 0.1)))
            
    def _update_rect(self):
        """Update rect position based on current position and size"""
        size = int(self.size * TILE_SIZE)
        self.rect.width = size
        self.rect.height = size
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
    def update(self, world, dt):
        """Update plant state"""
        try:
            super().update(world, dt)
            
            # Update rect position
            self._update_rect()
            
            # Get current season and tile
            current_season = world.time_system['season']
            tile = world.get_tile_at(self.x, self.y)
            
            if not tile:
                self.health -= dt * 10  # Damage plant if not on valid tile
                self.needs_update = True
                return
                
            # Calculate growth modifier based on season
            season_mod = self.seasonal_growth.get(current_season, 1.0)
            if not self.seasonal_behavior:
                season_mod = 1.0  # Plants like cacti ignore seasons
                
            # Calculate environmental factors
            water_factor = self._calculate_water_factor(world, tile)
            sunlight_factor = self._calculate_sunlight_factor(world)
            nutrient_factor = self._calculate_nutrient_factor(tile)
            
            # Update needs
            self._update_needs(water_factor, sunlight_factor, nutrient_factor, dt)
            
            # Update growth if not fully grown and not dormant
            if self.growth < 1.0 and not self.dormant:
                # Calculate overall growth factor
                growth_factor = (water_factor * sunlight_factor * 
                               nutrient_factor * season_mod)
                
                # Apply growth with all factors
                growth_amount = self.growth_rate * dt * growth_factor
                self.growth = min(1.0, self.growth + growth_amount)
                
                # Update size based on growth
                self.size = self.max_size * self.growth
                self.needs_update = True
            
            # Handle reproduction
            if self.reproduction_cooldown > 0:
                self.reproduction_cooldown -= dt
            elif (self.growth >= 0.8 and 
                  random.random() < self.reproduction_rate * dt * season_mod):
                self._try_reproduce(world)
                
            # Handle seasonal effects
            self._handle_seasonal_effects(world, current_season)
            
            # Update health based on environmental conditions
            health_change = 0
            if water_factor < 0.2:
                health_change -= dt * 10
            if sunlight_factor < 0.2:
                health_change -= dt * 5
            if nutrient_factor < 0.2:
                health_change -= dt * 3
                
            # Apply health change
            if health_change != 0:
                self.health = max(0, min(100, self.health + health_change))
                self.needs_update = True
                
            # Die if health reaches 0
            if self.health <= 0:
                world.remove_entity(self)
                
        except Exception as e:
            print(f"Error updating plant: {e}")
            
    def _calculate_water_factor(self, world, tile):
        """Calculate water availability factor"""
        try:
            base_water = tile.get('moisture', 0.5)
            
            # Increase water during rain
            if world.current_weather in ['rain', 'storm']:
                base_water = min(1.0, base_water + 0.3)
                
            # Decrease water in hot weather
            if world.temperature > 30:
                base_water = max(0, base_water - 0.2)
                
            return base_water
            
        except Exception as e:
            print(f"Error calculating water factor: {e}")
            return 0.5
            
    def _calculate_sunlight_factor(self, world):
        """Calculate sunlight availability factor"""
        try:
            hour = world.time_system['hour']
            
            # Night time
            if hour < 6 or hour > 18:
                return 0.2
                
            # Dawn/Dusk
            if hour < 8 or hour > 16:
                return 0.6
                
            # Full daylight
            base_light = 1.0
            
            # Reduce light in bad weather
            if world.current_weather in ['cloudy', 'rain', 'storm']:
                base_light *= 0.7
                
            return base_light
            
        except Exception as e:
            print(f"Error calculating sunlight factor: {e}")
            return 0.5
            
    def _calculate_nutrient_factor(self, tile):
        """Calculate nutrient availability factor"""
        try:
            return tile.get('fertility', 0.5)
        except Exception as e:
            print(f"Error calculating nutrient factor: {e}")
            return 0.5
            
    def _update_needs(self, water_factor, sunlight_factor, nutrient_factor, dt):
        """Update plant's needs"""
        try:
            # Update water level
            if water_factor > self.water_level / 100:
                self.water_level = min(100, self.water_level + 10 * dt)
            else:
                self.water_level = max(0, self.water_level - 5 * dt)
                
            # Update sunlight
            if sunlight_factor > self.sunlight / 100:
                self.sunlight = min(100, self.sunlight + 10 * dt)
            else:
                self.sunlight = max(0, self.sunlight - 5 * dt)
                
            # Update nutrients
            if nutrient_factor > self.nutrients / 100:
                self.nutrients = min(100, self.nutrients + 5 * dt)
            else:
                self.nutrients = max(0, self.nutrients - 2 * dt)
                
            # Mark for visual update if needs changed significantly
            if (abs(self.water_level - self._last_water) > 10 or
                abs(self.sunlight - self._last_sunlight) > 10 or
                abs(self.nutrients - self._last_nutrients) > 10):
                self.needs_update = True
                
            # Store last values
            self._last_water = self.water_level
            self._last_sunlight = self.sunlight
            self._last_nutrients = self.nutrients
            
        except Exception as e:
            print(f"Error updating needs: {e}")
            
    def _handle_seasonal_effects(self, world, season):
        """Handle effects of seasons on the plant"""
        if season == 'winter':
            # Chance to become dormant in winter
            if not self.dormant and random.random() < 0.1:
                self.dormant = True
                self.growth = max(0.3, self.growth - 0.2)  # Shrink a bit
                
        elif season == 'spring':
            # Wake up from dormancy
            if self.dormant:
                self.dormant = False
                
        elif season == 'fall':
            # Chance to prepare for winter
            if random.random() < 0.1:
                self.growth = max(0.5, self.growth - 0.1)
            
    def _try_reproduce(self, world):
        """Attempt to spread to nearby tiles"""
        # Find valid positions in a radius
        radius = int(self.size * 2)
        attempts = 5
        
        for _ in range(attempts):
            # Calculate random position in radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(TILE_SIZE, radius * TILE_SIZE)
            new_x = self.x + math.cos(angle) * distance
            new_y = self.y + math.sin(angle) * distance
            
            # Check if position is valid
            tile = world.get_tile(int(new_x / TILE_SIZE), int(new_y / TILE_SIZE))
            if tile and self._is_suitable_location(tile):
                # Create new plant
                new_plant = Plant(world, new_x, new_y, self.subtype)
                world.entities.append(new_plant)
                world._add_to_grid(new_plant)
                
                # Set reproduction cooldown
                self.reproduction_cooldown = random.uniform(60, 120)
                break
            
    def _is_suitable_location(self, tile):
        """Check if location is suitable for growth"""
        if not tile or 'biome' not in tile:
            return False
            
        # Check if this plant type can grow in this biome
        biome = tile['biome']
        if biome in BIOME_VEGETATION:
            return self.subtype in BIOME_VEGETATION[biome]
            
        return False
        
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw the plant with growth indicators"""
        try:
            # Call parent draw method first
            super().draw(screen, camera_x, camera_y, zoom)
            
            # Calculate screen position
            screen_x = int((self.x - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Draw growth stage indicator
            if hasattr(self, 'growth_stage'):
                stage_size = int(8 * zoom)
                stage_colors = {
                    'seed': (139, 69, 19),      # Brown
                    'sprout': (144, 238, 144),  # Light green
                    'growing': (34, 139, 34),   # Forest green
                    'mature': (0, 100, 0)       # Dark green
                }
                stage_color = stage_colors.get(self.growth_stage, (0, 255, 0))
                
                pygame.draw.circle(screen, stage_color,
                                (screen_x - int(self.size * zoom / 2),
                                 screen_y - int(self.size * zoom / 2)),
                                stage_size)
                
            # Draw growth progress bar
            if hasattr(self, 'growth') and self.growth < 1.0:
                bar_width = int(20 * zoom)
                bar_height = int(2 * zoom)
                growth_width = int(bar_width * self.growth)
                
                # Draw background
                pygame.draw.rect(screen, (100, 100, 100),
                               (screen_x - bar_width//2,
                                screen_y - int(self.size * zoom) - bar_height - 2,
                                bar_width, bar_height))
                # Draw growth
                pygame.draw.rect(screen, (100, 200, 100),
                               (screen_x - bar_width//2,
                                screen_y - int(self.size * zoom) - bar_height - 2,
                                growth_width, bar_height))
                
        except Exception as e:
            print(f"Error drawing plant: {e}")
            traceback.print_exc()
            
    def get_state(self):
        """Get current state for saving"""
        return {
            'type': self.type,
            'subtype': self.subtype,
            'x': self.x,
            'y': self.y,
            'growth': self.growth,
            'size': self.size,
            'state': self.state,
            'health': self.health,
            'dormant': self.dormant
        } 