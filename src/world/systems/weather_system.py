import math
import random
import pygame
import traceback
from typing import Dict, List, Optional, Tuple
from ...constants import (
    WEATHER_TYPES, SEASONS, SEASON_ORDER,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TIME_SPEEDS
)

class WeatherSystem:
    def __init__(self):
        """Initialize weather system"""
        self.world = None
        self.current_weather = 'clear'
        self.weather_duration = random.randint(300, 900)  # 5-15 minutes
        self.weather_timer = 0
        self.weather_transition = 0
        self.previous_weather = None
        self.transition_progress = 0.0
        self.lightning_flash = 0.0
        self.overlay_alpha = 0.0
        
        # Weather effects
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
        
        # Status effects
        self.active_effects = set()
        
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
            
    def update(self, dt: float):
        """Update weather system"""
        try:
            if not self.world:
                return
                
            # Update weather timer
            self.weather_timer += dt
            
            # Check for weather change
            if self.weather_timer >= self.weather_duration:
                self._change_random_weather()
            
            # Update weather systems
            self._update_wind(dt)
            self._update_visual_effects(dt)
            self._update_particle_systems(dt)
            self._update_status_effects(self.world)
            
            # Update weather transition
            if self.transition_progress < 1.0:
                self.transition_progress = min(1.0, self.transition_progress + dt * 0.5)
            
        except Exception as e:
            print(f"Error updating weather: {e}")
            traceback.print_exc()
            
    def _update_temperature(self):
        """Update temperature based on time and season"""
        try:
            if not self.world or not hasattr(self.world, 'time_system'):
                return
                
            # Get current season and hour
            season = SEASON_ORDER[self.world.time_system.season]
            hour = self.world.time_system.hour
            
            # Get base temperature from season
            base_temp = SEASONS[season]['base_temp']
            
            # Apply time of day variation (coolest at 3am, warmest at 3pm)
            time_offset = (hour - 3) % 24  # Hours since 3am
            time_factor = math.sin(time_offset * math.pi / 12)  # -1 to 1
            temp_range = 10  # ±10 degrees variation
            
            # Calculate final temperature with weather modifier
            weather_temp_mod = WEATHER_TYPES[self.current_weather]['temperature_mod']
            self.temperature = (base_temp + 
                              time_factor * temp_range + 
                              weather_temp_mod)
                              
            # Update world temperature
            self.world.temperature = self.temperature
            
        except Exception as e:
            print(f"Error updating temperature: {e}")
            traceback.print_exc()
            
    def _change_random_weather(self):
        """Change to a random weather based on season and time"""
        try:
            # Store previous weather for transition
            self.previous_weather = self.current_weather
            self.transition_progress = 0.0
            
            # Get current season
            season = SEASON_ORDER[self.world.time_system.season]
            
            # Get possible weather types for this season
            possible_weather = []
            for weather, data in WEATHER_TYPES.items():
                if season in data['possible_seasons']:
                    # Add weather multiple times based on its probability
                    probability = data['probability']
                    if season in data['season_probability_mod']:
                        probability *= data['season_probability_mod'][season]
                    possible_weather.extend([weather] * int(probability * 10))
                    
            # Select random weather from possibilities
            if possible_weather:
                self.current_weather = random.choice(possible_weather)
            else:
                self.current_weather = 'clear'  # Default to clear if no weather is possible
                
            # Set new duration
            self.weather_timer = 0
            self.weather_duration = random.randint(300, 900)  # 5-15 minutes
            
            # Update effects for new weather
            self._update_weather_effects()
            
            print(f"Weather changed to {self.current_weather}")
            
        except Exception as e:
            print(f"Error changing weather: {e}")
            traceback.print_exc()
            
    def _update_weather_effects(self):
        """Update weather effects based on current weather"""
        try:
            weather_data = WEATHER_TYPES[self.current_weather]
            
            # Update visual effects
            for effect in self.effects:
                self.effects[effect] = weather_data.get(effect, 0.0)
                
            # Update environmental conditions
            self.wind_speed = weather_data.get('wind_speed', 0.0)
            self.wind_direction = random.uniform(0, 2 * math.pi)
            self.humidity = weather_data.get('humidity', 0.5)
            
            # Initialize particles if needed
            if not self.particles:
                self._initialize_particles()
            
        except Exception as e:
            print(f"Error updating weather effects: {e}")
            traceback.print_exc()
            
    def _update_transition_effects(self):
        """Update effects during weather transition"""
        try:
            if not self.previous_weather or self.transition_progress >= 1.0:
                return
                
            # Get effect values for both weathers
            prev_effects = WEATHER_TYPES[self.previous_weather]
            curr_effects = WEATHER_TYPES[self.current_weather]
            
            # Interpolate between effects
            for effect in self.effects:
                prev_value = prev_effects.get(effect, 0.0)
                curr_value = curr_effects.get(effect, 0.0)
                self.effects[effect] = prev_value + (curr_value - prev_value) * self.transition_progress
                
        except Exception as e:
            print(f"Error updating transition effects: {e}")
            traceback.print_exc()
        
    def _update_particles(self, dt: float):
        """Update particle positions and lifecycle"""
        try:
            if not self.current_weather:
                return
                
            weather_data = WEATHER_TYPES[self.current_weather]
            
            # Update regular particles
            for particle in self.particles[:]:  # Copy list to allow removal
                # Update position based on wind and gravity
                particle['x'] += (self.wind_speed * math.cos(self.wind_direction) + 
                                weather_data['wind_speed']) * dt * 60
                particle['y'] += (self.wind_speed * math.sin(self.wind_direction) + 
                                weather_data['wind_speed']) * dt * 60
                
                # Reset particles that go off screen
                if (particle['x'] < 0 or particle['x'] > WINDOW_WIDTH or
                    particle['y'] < 0 or particle['y'] > WINDOW_HEIGHT):
                    particle['x'] = random.randint(0, WINDOW_WIDTH)
                    particle['y'] = 0
                    particle['alpha'] = random.randint(100, 255)
            
            # Update glow particles
            for particle in self.glow_particles[:]:  # Copy list to allow removal
                particle['alpha'] = max(0, particle['alpha'] - dt * 200)
                if particle['alpha'] <= 0:
                    self.glow_particles.remove(particle)
                    
            # Add new particles if needed
            while len(self.particles) < weather_data['particle_count']:
                self._add_particle()
                
        except Exception as e:
            print(f"Error updating particles: {e}")
            traceback.print_exc()
            
    def _add_particle(self):
        """Add a new weather particle"""
        try:
            if not self.current_weather:
                return
                
            particle = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.randint(2, 4),
                'alpha': random.randint(100, 255),
                'speed': random.uniform(2, 5)
            }
            self.particles.append(particle)
            
        except Exception as e:
            print(f"Error adding particle: {e}")
            traceback.print_exc()
            
    def _add_glow_particle(self):
        """Add a new glow particle for effects like lightning"""
        try:
            particle = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.randint(10, 20),
                'alpha': 255,
                'speed': random.uniform(1, 2)
            }
            self.glow_particles.append(particle)
            
        except Exception as e:
            print(f"Error adding glow particle: {e}")
            traceback.print_exc()
        
    def _update_wind(self, dt: float):
        """Update wind conditions"""
        # Get target wind speed based on weather
        target_speed = random.uniform(0, WEATHER_TYPES[self.current_weather]['max_wind'])
        
        # Smoothly interpolate current wind speed
        self.wind_speed += (target_speed - self.wind_speed) * dt
        
        # Update wind direction with smooth rotation
        self.wind_direction += random.uniform(-0.2, 0.2) * dt
        self.wind_direction = self.wind_direction % (2 * math.pi)
        
    def _update_visual_effects(self, dt: float):
        """Update visual weather effects"""
        # Update lightning flash
        if self.current_weather == 'storm' and random.random() < 0.01:
            self.lightning_flash = 1.0
        
        if self.lightning_flash > 0:
            self.lightning_flash = max(0, self.lightning_flash - dt * 5)
            
        # Update overlay alpha based on weather
        target_alpha = WEATHER_TYPES[self.current_weather].get('overlay_alpha', 0)
        self.overlay_alpha += (target_alpha - self.overlay_alpha) * dt * 2
        
    def _update_status_effects(self, world):
        """Update and apply weather status effects"""
        current_effects = set(WEATHER_TYPES[self.current_weather].get('status_effects', []))
        
        # Remove expired effects
        self.active_effects = self.active_effects.intersection(current_effects)
        
        # Add new effects
        self.active_effects.update(current_effects)
        
    def _initialize_particles(self):
        """Initialize weather particle systems"""
        self.particles = []
        self.glow_particles = []
        
    def _update_particle_systems(self, dt: float):
        """Update particle systems based on current weather"""
        try:
            weather_data = WEATHER_TYPES[self.current_weather]
            target_count = weather_data['particle_count']
            
            # Update regular particles
            while len(self.particles) < target_count:
                self._add_particle()
            while len(self.particles) > target_count:
                self.particles.pop()
            
            # Update glow particles for lightning
            if self.effects['lightning'] > 0:
                while len(self.glow_particles) < 5:
                    self._add_glow_particle()
            else:
                self.glow_particles.clear()
            
        except Exception as e:
            print(f"Error updating particle systems: {e}")
            traceback.print_exc()
        
    def draw(self, surface: pygame.Surface, camera: Dict):
        """Draw weather effects"""
        try:
            if not self.world:
                return
            
            # Apply darkness overlay
            if self.effects['darkness'] > 0:
                darkness = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                darkness.fill((0, 0, 0))
                darkness.set_alpha(int(self.effects['darkness'] * 128))
                surface.blit(darkness, (0, 0))
            
            # Draw regular particles
            for particle in self.particles:
                # Convert world coordinates to screen coordinates
                screen_x = int((particle['x'] - camera['x']) * camera['zoom'] + WINDOW_WIDTH/2)
                screen_y = int((particle['y'] - camera['y']) * camera['zoom'] + WINDOW_HEIGHT/2)
                
                # Skip particles outside screen
                if (screen_x < -10 or screen_x > WINDOW_WIDTH + 10 or
                    screen_y < -10 or screen_y > WINDOW_HEIGHT + 10):
                    continue
                
                # Draw particle
                size = int(particle['size'] * camera['zoom'])
                if size > 0:
                    if self.current_weather in ['rain', 'storm']:
                        # Draw rain drop as line
                        end_x = screen_x + int(self.wind_speed * math.cos(self.wind_direction) * 2)
                        end_y = screen_y + int(self.wind_speed * math.sin(self.wind_direction) * 2)
                        pygame.draw.line(surface, particle['color'], 
                                      (screen_x, screen_y), 
                                      (end_x, end_y), 
                                      max(1, size))
                    else:
                        # Draw circular particle
                        pygame.draw.circle(surface, particle['color'],
                                        (screen_x, screen_y), 
                                        max(1, size))
                                    
            # Draw glow particles
            for particle in self.glow_particles:
                screen_x = int((particle['x'] - camera['x']) * camera['zoom'] + WINDOW_WIDTH/2)
                screen_y = int((particle['y'] - camera['y']) * camera['zoom'] + WINDOW_HEIGHT/2)
                
                size = int(particle['size'] * camera['zoom'])
                if size > 0:
                    glow_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, particle['color'],
                                    (size, size), size)
                    surface.blit(glow_surf, 
                               (screen_x - size, screen_y - size),
                               special_flags=pygame.BLEND_ADD)
            
            # Draw fog overlay if needed
            if self.effects['fog'] > 0:
                fog = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                fog.fill((200, 200, 200))
                fog.set_alpha(int(self.effects['fog'] * 128))
                surface.blit(fog, (0, 0))
            
        except Exception as e:
            print(f"Error drawing weather effects: {e}")
            traceback.print_exc()
        
    def get_current_effects(self):
        """Get current weather effects"""
        try:
            if not self.world or not self.current_weather:
                return {}
                
            effects = {
                'temperature_change': WEATHER_TYPES[self.current_weather].get('temperature_mod', 0),
                'wind_speed': self.wind_speed,
                'wind_direction': self.wind_direction,
                'humidity': self.humidity,
                'visibility': WEATHER_TYPES[self.current_weather].get('visibility', 1.0),
                'movement_speed': WEATHER_TYPES[self.current_weather].get('movement_speed', 1.0)
            }
            
            # Add visual effects
            effects.update(self.effects)
            
            return effects
            
        except Exception as e:
            print(f"Error getting weather effects: {e}")
            traceback.print_exc()
            return {}
        
    def cleanup(self):
        """Clean up weather system resources"""
        self.particles.clear()
        self.active_effects.clear()

    def draw_effects(self, surface: pygame.Surface):
        """Draw weather effects on the surface"""
        try:
            if not self.current_weather:
                return
                
            weather_data = WEATHER_TYPES[self.current_weather]
            
            # Draw weather overlay
            if weather_data['overlay_alpha'] > 0:
                overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                overlay_color = (*weather_data['graphics']['sky_color'], 
                               int(weather_data['overlay_alpha'] * 255))
                overlay.fill(overlay_color)
                surface.blit(overlay, (0, 0))
            
            # Draw particles if enabled
            if weather_data['graphics']['particle_effects']:
                self._draw_particles(surface)
            
            # Draw lightning flash
            if self.lightning_flash > 0 and 'lightning' in weather_data['graphics']:
                flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                alpha = int(self.lightning_flash * 255)
                flash.fill((255, 255, 255, alpha))
                surface.blit(flash, (0, 0))
                
        except Exception as e:
            print(f"Error drawing weather effects: {e}")
            traceback.print_exc()
            
    def _draw_particles(self, surface: pygame.Surface):
        """Draw weather particles"""
        try:
            if not self.current_weather:
                return
                
            weather_data = WEATHER_TYPES[self.current_weather]
            
            # Draw regular particles (rain/snow)
            for particle in self.particles:
                color = weather_data['particle_color']
                if color:
                    pos = (int(particle['x']), int(particle['y']))
                    size = particle['size']
                    alpha = particle['alpha']
                    
                    particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    particle_color = (*color, alpha)
                    
                    if self.current_weather == 'snow':
                        # Draw snowflake
                        pygame.draw.circle(particle_surface, particle_color, 
                                        (size//2, size//2), size//2)
                    else:
                        # Draw raindrop
                        pygame.draw.line(particle_surface, particle_color,
                                      (0, 0), (size, size), 2)
                    
                    surface.blit(particle_surface, pos)
            
            # Draw glow particles for effects like lightning
            for particle in self.glow_particles:
                pos = (int(particle['x']), int(particle['y']))
                size = particle['size']
                alpha = particle['alpha']
                
                glow_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                for radius in range(size, 0, -2):
                    alpha_mod = int((radius/size) * alpha)
                    pygame.draw.circle(glow_surface, (255, 255, 255, alpha_mod),
                                    (size, size), radius)
                
                surface.blit(glow_surface, 
                           (pos[0] - size, pos[1] - size))
                
        except Exception as e:
            print(f"Error drawing particles: {e}")
            traceback.print_exc()
        
    def get_current_weather(self) -> Dict:
        """Get current weather data"""
        try:
            return {
                'condition': self.current_weather,
                'temperature': self.temperature,
                'humidity': self.humidity,
                'wind_speed': self.wind_speed,
                'wind_direction': self.wind_direction,
                'darkness': self.effects.get('darkness', 0.0),
                'fog': self.effects.get('fog', 0.0),
                'rain': self.effects.get('rain', 0.0),
                'snow': self.effects.get('snow', 0.0),
                'thunder': self.effects.get('thunder', 0.0),
                'cloud_cover': self.effects.get('cloud_cover', 0.0),
                'lightning': self.effects.get('lightning', 0.0)
            }
        except Exception as e:
            print(f"Error getting weather data: {e}")
            traceback.print_exc()
            return {
                'condition': 'clear',
                'temperature': 20.0,
                'humidity': 0.5,
                'wind_speed': 0.0,
                'wind_direction': 0.0,
                'darkness': 0.0,
                'fog': 0.0,
                'rain': 0.0,
                'snow': 0.0,
                'thunder': 0.0,
                'cloud_cover': 0.0,
                'lightning': 0.0
            } 