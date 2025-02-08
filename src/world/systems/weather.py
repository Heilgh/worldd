import random
import pygame
from ...constants import UI_COLORS, WEATHER_EFFECTS, WINDOW_WIDTH, WINDOW_HEIGHT
from typing import Dict, List, Optional, Tuple
import math
import traceback

class WeatherSystem:
    def __init__(self):
        """Initialize weather system"""
        self.world = None
        self.current_weather = 'clear'
        self.weather_duration = random.randint(300, 900)  # 5-15 minutes
        self.weather_transition = 0
        self.particles = []
        self.glow_particles = []
        self.wind_speed = 0.0
        self.wind_direction = 0.0
        self.temperature = 20.0
        self.humidity = 0.5
        
        # Visual effects
        self.effects = {
            'darkness': 0.0,
            'fog': 0.0,
            'rain': 0.0,
            'snow': 0.0,
            'thunder': 0.0,
            'cloud_cover': 0.0,
            'lightning': 0.0
        }
        
        # Weather colors for visual effects
        self.weather_colors = {
            'clear': (255, 255, 255),
            'cloudy': (180, 180, 180),
            'rain': (100, 100, 120),
            'storm': (70, 70, 90),
            'snow': (230, 230, 250)
        }
        
        # Weather effects and their properties
        self.weather_types = {
            'clear': {
                'visibility': 1.0,
                'movement_speed': 1.0,
                'temperature_mod': 0,
                'wind_factor': 0.5,
                'color': (255, 255, 255),
                'particle_count': 0,
                'darkness': 0.0,
                'fog': 0.0,
                'thunder': 0.0
            },
            'cloudy': {
                'visibility': 0.8,
                'movement_speed': 0.9,
                'temperature_mod': -2,
                'wind_factor': 1.0,
                'color': (180, 180, 180),
                'particle_count': 0,
                'darkness': 0.2,
                'fog': 0.3,
                'thunder': 0.0
            },
            'rain': {
                'visibility': 0.6,
                'movement_speed': 0.7,
                'temperature_mod': -5,
                'wind_factor': 1.5,
                'color': (100, 150, 255),
                'particle_count': 200,
                'darkness': 0.4,
                'fog': 0.2,
                'thunder': 0.0
            },
            'storm': {
                'visibility': 0.4,
                'movement_speed': 0.5,
                'temperature_mod': -8,
                'wind_factor': 2.0,
                'color': (70, 70, 90),
                'particle_count': 400,
                'darkness': 0.6,
                'fog': 0.4,
                'thunder': 1.0
            },
            'snow': {
                'visibility': 0.7,
                'movement_speed': 0.6,
                'temperature_mod': -10,
                'wind_factor': 0.8,
                'color': (230, 230, 250),
                'particle_count': 150,
                'darkness': 0.3,
                'fog': 0.5,
                'thunder': 0.0
            }
        }
        
        # Initialize particle systems
        self._initialize_particles()
        
        # Weather chances per season
        self.weather_chances = {
            'spring': {
                'clear': 0.3,
                'cloudy': 0.3,
                'rain': 0.3,
                'storm': 0.1
            },
            'summer': {
                'clear': 0.5,
                'cloudy': 0.2,
                'rain': 0.2,
                'storm': 0.1
            },
            'autumn': {
                'clear': 0.2,
                'cloudy': 0.4,
                'rain': 0.3,
                'storm': 0.1
            },
            'winter': {
                'clear': 0.3,
                'cloudy': 0.3,
                'snow': 0.3,
                'storm': 0.1
            }
        }
        
    def initialize(self, world):
        """Initialize weather system with world reference"""
        try:
            print("Initializing weather system...")
            self.world = world
            self.weather_timer = 0
            self.weather_duration = random.randint(300, 900)  # 5-15 minutes
            
            # Initialize particle systems
            self._initialize_particles()
            
            # Set initial weather effects
            self._update_weather_effects()
            
            print("Weather system initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing weather system: {e}")
            traceback.print_exc()
            raise
        
    def _initialize_particles(self):
        """Initialize weather particle systems"""
        self.particles = []
        self.glow_particles = []
        
        # Create initial particles
        self._generate_particles(100)
        self._generate_glow_particles(20)

    def _generate_particles(self, count: int):
        """Generate weather particles"""
        for _ in range(count):
            particle = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(2, 5),
                'size': random.randint(2, 4),
                'alpha': random.randint(100, 255),
                'color': (255, 255, 255, 200)
            }
            self.particles.append(particle)

    def _generate_glow_particles(self, count: int):
        """Generate glowing particles for effects"""
        for _ in range(count):
            particle = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(10, 20),
                'alpha': random.randint(50, 150),
                'color': (200, 220, 255, 100)
            }
            self.glow_particles.append(particle)

    def _update_particles(self, dt: float):
        """Update weather particle positions and properties"""
        wind_factor = self.wind_speed * dt
        
        # Update regular particles
        for particle in self.particles:
            particle['y'] += particle['speed'] * dt * 60
            particle['x'] += math.cos(self.wind_direction) * wind_factor
            
            if particle['y'] > WINDOW_HEIGHT:
                particle['y'] = 0
                particle['x'] = random.randint(0, WINDOW_WIDTH)
            if particle['x'] > WINDOW_WIDTH:
                particle['x'] = 0
            elif particle['x'] < 0:
                particle['x'] = WINDOW_WIDTH
                
        # Update glow particles
        for particle in self.glow_particles:
            particle['y'] += particle['speed'] * dt * 30
            particle['x'] += math.cos(self.wind_direction) * wind_factor * 0.5
            particle['alpha'] = max(50, min(150, particle['alpha'] + random.randint(-5, 5)))
            
            if particle['y'] > WINDOW_HEIGHT:
                particle['y'] = 0
                particle['x'] = random.randint(0, WINDOW_WIDTH)
            if particle['x'] > WINDOW_WIDTH:
                particle['x'] = 0
            elif particle['x'] < 0:
                particle['x'] = WINDOW_WIDTH

    def _update_weather_effects(self):
        """Update weather visual effects"""
        weather = self.weather_types[self.current_weather]
        
        # Update effect intensities
        self.effects['darkness'] = weather['darkness']
        self.effects['fog'] = weather['fog']
        self.effects['rain'] = weather['rain']
        self.effects['snow'] = weather['snow']
        self.effects['thunder'] = weather['thunder']
        
        # Update particle counts based on weather
        target_particles = self._get_target_particle_count()
        current_particles = len(self.particles)
        
        if current_particles < target_particles:
            self._generate_particles(target_particles - current_particles)
        elif current_particles > target_particles:
            self.particles = self.particles[:target_particles]

    def _get_target_particle_count(self) -> int:
        """Get target number of particles based on weather"""
        if self.current_weather == 'rain':
            return 200
        elif self.current_weather == 'snow':
            return 150
        elif self.current_weather == 'storm':
            return 300
        return 50

    def update(self, dt: float):
        """Update weather system"""
        try:
            # Update weather duration
            self.weather_duration -= dt
            
            # Check for weather change
            if self.weather_duration <= 0:
                self._change_random_weather()
                
            # Update particles
            self._update_particles(dt)
            
            # Update wind
            self.wind_direction += math.sin(dt) * 0.1
            self.wind_speed = max(0, min(10, self.wind_speed + random.uniform(-0.1, 0.1)))
            
            # Update effects based on current weather
            weather = self.weather_types[self.current_weather]
            for effect in self.effects:
                target = weather.get(effect, 0.0)
                current = self.effects[effect]
                self.effects[effect] = current + (target - current) * dt
                
            # Random lightning for storms
            if self.current_weather == 'storm' and random.random() < 0.01:
                self.effects['lightning'] = 1.0
                
            # Fade lightning
            self.effects['lightning'] = max(0, self.effects['lightning'] - dt * 2)
            
        except Exception as e:
            print(f"Error updating weather: {e}")

    def _change_random_weather(self):
        """Change to a random weather with proper transitions"""
        season = self.world.current_season if hasattr(self.world, 'current_season') else 'summer'
        chances = self.weather_chances[season]
        
        # Get random weather based on season chances
        roll = random.random()
        cumulative = 0
        for weather, chance in chances.items():
            cumulative += chance
            if roll <= cumulative:
                self.current_weather = weather
                break
                
        # Set new duration
        self.weather_duration = random.randint(300, 900)  # 5-15 minutes
        
        # Update effects
        self._update_weather_effects()

    def draw(self, surface: pygame.Surface, camera: Dict):
        """Draw weather effects"""
        try:
            # Draw base weather overlay
            self._draw_weather_overlay(surface)
            
            # Draw particles
            self._draw_particles(surface, camera)
            
            # Draw lightning
            if self.effects['lightning'] > 0:
                self._draw_lightning(surface)
                
            # Draw clouds
            if self.effects['cloud_cover'] > 0:
                self._draw_clouds(surface)
                
        except Exception as e:
            print(f"Error drawing weather: {e}")

    def _draw_weather_overlay(self, surface: pygame.Surface):
        """Draw weather overlay effects"""
        # Draw darkness overlay
        if self.effects['darkness'] > 0:
            dark = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, int(self.effects['darkness'] * 128)))
            surface.blit(dark, (0, 0))
            
        # Draw fog overlay
        if self.effects['fog'] > 0:
            fog = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            fog.fill((200, 200, 255, int(self.effects['fog'] * 100)))
            surface.blit(fog, (0, 0))

    def _draw_lightning(self, surface: pygame.Surface):
        """Draw lightning effect"""
        if self.effects['lightning'] > 0:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = int(self.effects['lightning'] * 128)
            flash.fill((255, 255, 255, alpha))
            surface.blit(flash, (0, 0))
            
            # Draw actual lightning bolt
            if random.random() < 0.3:
                start = (random.randint(0, WINDOW_WIDTH), 0)
                end = (random.randint(0, WINDOW_WIDTH), random.randint(WINDOW_HEIGHT//2, WINDOW_HEIGHT))
                points = self._generate_lightning_points(start, end)
                pygame.draw.lines(surface, (255, 255, 255), False, points, 2)

    def _generate_lightning_points(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate points for a lightning bolt"""
        points = [start]
        current = start
        while current[1] < end[1]:
            next_y = min(current[1] + random.randint(20, 50), end[1])
            next_x = current[0] + random.randint(-30, 30)
            next_point = (next_x, next_y)
            points.append(next_point)
            current = next_point
        return points

    def _draw_particles(self, surface: pygame.Surface, camera: Dict):
        """Draw weather particles"""
        # Draw glow particles first
        for particle in self.glow_particles:
            x = int(particle['x'] - camera['x'])
            y = int(particle['y'] - camera['y'])
            if 0 <= x <= WINDOW_WIDTH and 0 <= y <= WINDOW_HEIGHT:
                color = (*particle['color'][:3], particle['alpha'])
                pygame.draw.circle(surface, color, (x, y), particle['size'])
                
                # Draw glow effect
                glow = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color[:3], color[3] // 4), 
                                 (glow.get_width() // 2, glow.get_height() // 2), 
                                 particle['size'] * 2)
                surface.blit(glow, (x - glow.get_width() // 2, y - glow.get_height() // 2), 
                           special_flags=pygame.BLEND_RGBA_ADD)
                
        # Draw regular particles
        if self.effects['rain'] > 0 or self.effects['snow'] > 0:
            for particle in self.particles:
                x = int(particle['x'] - camera['x'])
                y = int(particle['y'] - camera['y'])
                if 0 <= x <= WINDOW_WIDTH and 0 <= y <= WINDOW_HEIGHT:
                    if self.effects['rain'] > 0:
                        # Draw rain drop
                        end_y = y + particle['size'] * 2
                        color = (200, 200, 255, particle['alpha'])
                        pygame.draw.line(surface, color, (x, y), (x, end_y), 1)
                    elif self.effects['snow'] > 0:
                        # Draw snowflake
                        color = (255, 255, 255, particle['alpha'])
                        pygame.draw.circle(surface, color, (x, y), particle['size'])
                        
    def _draw_clouds(self, surface: pygame.Surface):
        """Draw cloud effects"""
        if self.effects['cloud_cover'] > 0:
            cloud_color = (40, 40, 60, int(self.effects['cloud_cover'] * 100))
            cloud_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            
            for i in range(5):  # Draw multiple cloud layers
                y = int(WINDOW_HEIGHT * 0.2) + i * 40
                width = random.randint(100, 200)
                height = random.randint(40, 80)
                
                for x in range(0, WINDOW_WIDTH + 100, 200):
                    offset_x = x + math.sin(self.weather_transition + i) * 20
                    offset_y = y + math.cos(self.weather_transition + i) * 10
                    
                    pygame.draw.ellipse(cloud_layer, cloud_color,
                                     (offset_x, offset_y, width, height))
                    
            surface.blit(cloud_layer, (0, 0))

    def get_current_weather(self) -> str:
        """Get current weather state"""
        return self.current_weather
        
    def get_weather_effects(self) -> Dict:
        """Get current weather effects"""
        return self.effects
        
    def force_weather(self, weather: str, transition_time: float = 5.0):
        """Force a specific weather state"""
        if weather in self.weather_types:
            self.current_weather = weather
            self.weather_duration = 0
            self.weather_transition = 0
            self.wind_direction = 0
            self.wind_speed = 0
            self._update_weather_effects()
            
    def get_effects(self):
        return self.effects

# Assuming self.particles is defined somewhere in the class
# This method should be implemented to return the particles list
def get_particles(self):
    return self.particles

# Assuming self.weather_colors is defined somewhere in the class
# This method should be implemented to return the weather_colors dictionary
def get_weather_colors(self):
    return self.weather_colors

# Assuming self.weather_chances is defined somewhere in the class
# This method should be implemented to return the weather_chances dictionary
def get_weather_chances(self):
    return self.weather_chances 