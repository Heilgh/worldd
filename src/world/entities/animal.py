import random
import math
import pygame
from .entity import Entity
from ...constants import ANIMAL_TYPES, ANIMAL_BEHAVIORS, TILE_SIZE
import traceback
from typing import Dict, List, Tuple, Optional

class Animal(Entity):
    def __init__(self, world, x: float, y: float, animal_type: str = 'wolf'):
        """Initialize an animal entity"""
        # Initialize type before super().__init__
        self.type = 'animal'
        self.subtype = animal_type
        
        # Get properties from ANIMAL_TYPES
        self.properties = ANIMAL_TYPES[animal_type].copy()
        
        # Set basic attributes
        self.sprite = self.properties.get('sprite', '🐾')  # Default animal footprint emoji
        self.speed = self.properties.get('speed', 100)
        self.size = self.properties.get('size', TILE_SIZE)
        self.behavior = self.properties.get('behavior', 'neutral')
        self.vision_range = self.properties.get('vision_range', 200)
        self.damage = self.properties.get('damage', 0)
        
        # Core stats
        self.health = self.properties.get('health', 100)
        self.max_health = self.health
        self.energy = self.properties.get('max_energy', 100)
        self.max_energy = self.energy
        
        # Initialize needs
        self.needs = {
            'hunger': 0,
            'thirst': 0,
            'energy': self.energy,
            'safety': 100
        }
        
        # State tracking
        self.state = 'idle'
        self.state_timer = 0
        self.target = None
        self.path = []
        
        # Behavior tracking
        self.last_behavior_time = 0
        self.behavior_cooldown = random.uniform(1.0, 3.0)
        self.wander_direction = random.uniform(0, 360)
        self.wander_timer = 0
        
        # Additional properties
        self.age = 0
        self.maturity = 0
        self.reproduction_cooldown = 0
        self.last_position = (x, y)
        
        # Set behavior-specific properties
        self.is_predator = self.behavior == 'predator'
        self.is_prey = self.behavior == 'prey'
        self.diet = self.properties.get('diet', ['grass'])
        self.pack_animal = self.properties.get('pack_animal', False)
        self.nocturnal = self.properties.get('nocturnal', False)
        
        # Call parent constructor
        super().__init__(world, x, y)
        
        # Initialize rect for UI and collision
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        print(f"Created animal of type {animal_type} at position ({x}, {y})")
        
    def update(self, world, dt):
        """Update animal state and behavior"""
        super().update(world, dt)
        
        # Update needs
        self._update_needs(dt)
        
        # Update behavior
        self._update_behavior(world, dt)
        
        # Update reproduction
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= dt
            
    def _update_needs(self, dt):
        """Update basic needs"""
        # Increase hunger and thirst over time
        self.needs['hunger'] = min(100, self.needs['hunger'] + 1.5 * dt)
        self.needs['thirst'] = min(100, self.needs['thirst'] + 2 * dt)
        
        # Decrease energy while active
        if self.state != 'resting':
            self.energy = max(0, self.energy - 0.5 * dt)
            
        # Health regeneration when resting and well-fed
        if self.state == 'resting' and self.needs['hunger'] < 50 and self.needs['thirst'] < 50:
            self.health = min(self.max_health, self.health + 2 * dt)
            
    def _update_behavior(self, world, dt):
        """Update animal behavior based on needs and surroundings"""
        # Reset state timer
        self.state_timer -= dt
        if self.state_timer <= 0:
            self._choose_new_state(world)
            
        # Act based on current state
        if self.state == 'hunting':
            self._handle_hunting(world, dt)
        elif self.state == 'fleeing':
            self._handle_fleeing(world, dt)
        elif self.state == 'resting':
            self._handle_resting(dt)
        elif self.state == 'wandering':
            self._handle_wandering(world, dt)
            
    def _choose_new_state(self, world):
        """Choose a new state based on current situation"""
        # Check for threats first
        if self.behavior == 'prey':
            threats = self._find_threats(world)
            if threats:
                self.state = 'fleeing'
                self.target = threats[0]
                self.state_timer = random.uniform(5, 10)
                return
                
        # Check needs
        if self.energy < 30:
            self.state = 'resting'
            self.state_timer = random.uniform(10, 20)
        elif self.needs['hunger'] > 70 and self.behavior == 'predator':
            self.state = 'hunting'
            self.state_timer = random.uniform(20, 30)
        else:
            self.state = 'wandering'
            self.state_timer = random.uniform(5, 15)
            
    def _find_threats(self, world):
        """Find nearby predators"""
        threats = []
        nearby = world.get_entities_in_range(self.x, self.y, self.vision_range * TILE_SIZE)
        
        for entity in nearby:
            if (isinstance(entity, Animal) and 
                entity.behavior == 'predator' and 
                entity != self):
                threats.append(entity)
                
        return threats
        
    def _handle_hunting(self, world, dt):
        """Handle hunting behavior"""
        if not self.target or not hasattr(self.target, 'x'):
            potential_prey = self._find_prey(world)
            if potential_prey:
                self.target = random.choice(potential_prey)
            else:
                self.state = 'wandering'
                return
                
        # Move towards target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.size:
            # Attack target
            if hasattr(self.target, 'health'):
                self.target.health -= self.damage * dt
            self.state = 'wandering'
        else:
            # Move towards target
            self.x += (dx/dist) * self.speed * dt
            self.y += (dy/dist) * self.speed * dt
            
    def _find_prey(self, world):
        """Find potential prey"""
        prey = []
        nearby = world.get_entities_in_range(self.x, self.y, self.vision_range)
        
        for entity in nearby:
            if (isinstance(entity, Animal) and 
                entity.behavior == 'prey' and 
                entity != self):
                prey.append(entity)
                
        return prey
        
    def _handle_fleeing(self, world, dt):
        """Handle fleeing behavior"""
        if not self.target or not hasattr(self.target, 'x'):
            self.state = 'wandering'
            return
            
        # Move away from threat
        dx = self.x - self.target.x
        dy = self.y - self.target.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > self.vision_range * TILE_SIZE:
            self.state = 'wandering'
        else:
            # Move away from target
            self.x += (dx/dist) * self.speed * dt
            self.y += (dy/dist) * self.speed * dt
            
    def _handle_resting(self, dt):
        """Handle resting behavior"""
        # Recover energy
        self.energy = min(self.max_energy, self.energy + 5 * dt)
        
        # End resting if energy is high enough
        if self.energy >= self.max_energy * 0.8:
            self.state = 'wandering'
            
    def _handle_wandering(self, world, dt):
        """Handle wandering behavior"""
        if not self.target or not hasattr(self.target, 'x'):
            # Choose random target point
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 200)
            target_x = self.x + math.cos(angle) * distance
            target_y = self.y + math.sin(angle) * distance
            
            # Keep within world bounds
            target_x = max(0, min(world.width, target_x))
            target_y = max(0, min(world.height, target_y))
            
            self.target = type('Target', (), {'x': target_x, 'y': target_y})()
            
        # Move towards target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.size:
            self.target = None
        else:
            # Move towards target
            self.x += (dx/dist) * self.speed * 0.5 * dt
            self.y += (dy/dist) * self.speed * 0.5 * dt
            
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw the animal with behavior indicators and status bars"""
        try:
            # Call parent draw method first
            super().draw(screen, camera_x, camera_y, zoom)
            
            # Calculate screen position
            screen_x = int((self.x - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Draw behavior emoji if available
            if self.state in ANIMAL_BEHAVIORS and 'emoji' in ANIMAL_BEHAVIORS[self.state]:
                try:
                    behavior_emoji = ANIMAL_BEHAVIORS[self.state]['emoji']
                    emoji_size = int(16 * zoom)
                    emoji_font = pygame.font.SysFont('segoe ui emoji', emoji_size)
                    emoji_surface = emoji_font.render(behavior_emoji, True, (0, 0, 0))
                    emoji_rect = emoji_surface.get_rect(
                        centerx=screen_x,
                        bottom=screen_y - int(self.size * zoom)
                    )
                    screen.blit(emoji_surface, emoji_rect)
                except Exception as e:
                    print(f"Error drawing behavior emoji: {e}")
                    
            # Draw additional status indicators
            if hasattr(self, 'is_predator') and self.is_predator:
                # Draw predator indicator
                indicator_size = int(8 * zoom)
                pygame.draw.circle(screen, (255, 0, 0),
                                (screen_x + int(self.size * zoom / 2),
                                 screen_y - int(self.size * zoom / 2)),
                                indicator_size)
                
        except Exception as e:
            print(f"Error drawing animal: {e}")
            traceback.print_exc()
            
    def _draw_status_bars(self, screen, camera):
        """Draw health and energy bars"""
        try:
            # Calculate screen position
            screen_x = int((self.x - camera['x']) * camera['zoom'])
            screen_y = int((self.y - camera['y']) * camera['zoom'])
            
            # Calculate bar dimensions
            bar_width = int(20 * camera['zoom'])
            bar_height = int(2 * camera['zoom'])
            bar_spacing = bar_height + 1
            
            # Draw health bar
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (100, 100, 100),
                           (screen_x - bar_width//2, screen_y - 15,
                            bar_width, bar_height))
            pygame.draw.rect(screen, (220, 50, 50),
                           (screen_x - bar_width//2, screen_y - 15,
                            health_width, bar_height))
                            
            # Draw energy bar
            energy_width = int(bar_width * (self.energy / self.max_energy))
            pygame.draw.rect(screen, (100, 100, 100),
                           (screen_x - bar_width//2, screen_y - 15 + bar_spacing,
                            bar_width, bar_height))
            pygame.draw.rect(screen, (50, 150, 220),
                           (screen_x - bar_width//2, screen_y - 15 + bar_spacing,
                            energy_width, bar_height))
                            
        except Exception as e:
            print(f"Error drawing status bars: {e}")
            
    def get_state(self):
        """Get current state for saving"""
        return {
            'type': self.type,
            'subtype': self.subtype,
            'x': self.x,
            'y': self.y,
            'health': self.health,
            'energy': self.energy,
            'hunger': self.needs['hunger'],
            'thirst': self.needs['thirst'],
            'state': self.state,
            'behavior': self.behavior
        } 