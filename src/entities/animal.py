import pygame
import random
import traceback
import math
from typing import Dict, List, Optional, Tuple
from ..constants import (
    ENTITY_TYPES, TILE_SIZE, STATUS_EFFECTS,
    WEATHER_EFFECTS, BIOMES
)

class Animal:
    def __init__(self, world, pos: Tuple[float, float], animal_type: str):
        """Initialize animal entity with advanced features"""
        try:
            print(f"Creating {animal_type} at position {pos}")
            self.world = world
            self.x, self.y = pos
            self.type = animal_type
            self.id = f"animal_{id(self)}"  # Unique identifier
            
            # Get base properties from entity types
            self.properties = ENTITY_TYPES['animal'].copy()
            
            # Basic attributes
            self.speed = self.properties['speed']
            self.size = self.properties['size']
            self.vision_range = self.properties['specs']['vision_range']
            self.interaction_range = self.properties['specs']['interaction_range']
            
            # Core stats
            self.health = self.properties['specs']['max_health']
            self.max_health = self.properties['specs']['max_health']
            self.energy = self.properties['specs']['max_energy']
            self.max_energy = self.properties['specs']['max_energy']
            
            # Needs
            self.needs = {
                'hunger': 0,
                'thirst': 0,
                'rest': 0,
                'safety': 0
            }
            
            # Behavior
            self.state = 'idle'
            self.target_pos = None
            self.velocity = [0, 0]
            self.wander_timer = 0
            self.wander_interval = random.uniform(3.0, 8.0)
            self.behavior_cooldown = 0
            self.last_behavior_change = 0
            
            # Status effects
            self.status_effects: Dict[str, Dict] = {}
            
            # Characteristics
            self.is_predator = 'predator' in animal_type.lower()
            self.is_prey = not self.is_predator
            self.is_hostile = self.is_predator
            self.preferred_biomes = self._determine_preferred_biomes()
            self.preferred_time = random.choice(['day', 'night', 'any'])
            
            # Memory and awareness
            self.known_food_sources = []
            self.known_water_sources = []
            self.known_threats = []
            self.home_location = pos
            
            # Sprite/emoji
            self.sprite = self.properties['sprite']
            self.color = self.properties['color']
            
            print(f"{animal_type} created successfully with characteristics: predator={self.is_predator}, preferred_time={self.preferred_time}")
            
        except Exception as e:
            print(f"Error creating animal: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update animal state with enhanced features"""
        try:
            # Update needs
            self._update_needs(dt)
            
            # Update status effects
            self._update_status_effects(dt)
            
            # Update behavior and decision making
            self._update_behavior(dt)
            
            # Update movement and physics
            self._update_movement(dt)
            
            # Update memory and awareness
            self._update_awareness(dt)
            
        except Exception as e:
            print(f"Error updating animal: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], zoom: float, effects: Dict = None):
        """Draw animal entity with enhanced visuals"""
        try:
            # Calculate screen position
            screen_x = (self.x - camera_pos[0]) * zoom
            screen_y = (self.y - camera_pos[1]) * zoom
            
            # Apply visual effects based on status
            color = self._get_display_color(effects)
            
            # Draw animal sprite/emoji with effects
            if isinstance(self.sprite, str):  # Emoji fallback
                font = pygame.font.SysFont('segoe ui emoji', int(TILE_SIZE * zoom))
                text = font.render(self.sprite, True, color)
                surface.blit(text, (screen_x, screen_y))
            else:  # Image sprite
                scaled_size = (int(self.size * zoom), int(self.size * zoom))
                scaled_sprite = pygame.transform.scale(self.sprite, scaled_size)
                # Apply color tint
                tinted_sprite = self._apply_color_tint(scaled_sprite, color)
                surface.blit(tinted_sprite, (screen_x, screen_y))
                
            # Draw status indicators
            self._draw_status_indicators(surface, (screen_x, screen_y), zoom)
            
            # Draw health bar
            self._draw_health_bar(surface, (screen_x, screen_y), zoom)
            
        except Exception as e:
            print(f"Error drawing animal: {e}")
            traceback.print_exc()
            
    def _update_needs(self, dt: float):
        """Update animal needs"""
        try:
            # Increase needs over time
            self.needs['hunger'] = min(100, self.needs['hunger'] + dt * 2)
            self.needs['thirst'] = min(100, self.needs['thirst'] + dt * 3)
            self.needs['rest'] = min(100, self.needs['rest'] + dt * 1.5)
            
            # Safety need based on environment and threats
            threats = self._assess_threats()
            self.needs['safety'] = min(100, 20 * len(threats))
            
            # Apply need effects
            if self.needs['hunger'] > 80 or self.needs['thirst'] > 80:
                self.health = max(0, self.health - dt * 5)
                
            if self.needs['rest'] > 90:
                self.energy = max(0, self.energy - dt * 3)
                
        except Exception as e:
            print(f"Error updating animal needs: {e}")
            traceback.print_exc()
            
    def _update_behavior(self, dt: float):
        """Update animal behavior with enhanced decision making"""
        try:
            # Update timers
            self.wander_timer += dt
            self.behavior_cooldown = max(0, self.behavior_cooldown - dt)
            
            # Only change behavior if cooldown is done
            if self.behavior_cooldown > 0:
                return
                
            # Check if current behavior should change
            current_time = self.world.time
            if current_time - self.last_behavior_change > 5.0:  # Minimum 5 seconds between changes
                new_state = self._decide_behavior()
                if new_state != self.state:
                    self.state = new_state
                    self.last_behavior_change = current_time
                    self.behavior_cooldown = random.uniform(2.0, 5.0)
                    
            # Execute current behavior
            if self.state == 'idle':
                if self.wander_timer >= self.wander_interval:
                    self.wander_timer = 0
                    self._choose_random_target()
                    self.state = 'moving'
                    
            elif self.state == 'moving':
                if self.target_pos:
                    dx = self.target_pos[0] - self.x
                    dy = self.target_pos[1] - self.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    if dist < 5:  # Close enough to target
                        self.state = 'idle'
                        self.target_pos = None
                    else:
                        # Update velocity towards target
                        speed = self._get_current_speed()
                        self.velocity[0] = (dx / dist) * speed
                        self.velocity[1] = (dy / dist) * speed
                        
            elif self.state == 'hunting':
                self._execute_hunting_behavior()
                
            elif self.state == 'fleeing':
                self._execute_fleeing_behavior()
                
            elif self.state == 'resting':
                self._execute_resting_behavior(dt)
                
            elif self.state == 'drinking':
                self._execute_drinking_behavior(dt)
                
            elif self.state == 'returning_home':
                self._move_towards(self.home_location)
                
        except Exception as e:
            print(f"Error updating animal behavior: {e}")
            traceback.print_exc()
            
    def _decide_behavior(self) -> str:
        """Decide next behavior based on current state and needs"""
        try:
            # Check for immediate threats
            threats = self._assess_threats()
            if threats and self.needs['safety'] > 50:
                return 'fleeing'
                
            # Check if it's appropriate time of day
            is_day = 6 < self.world.day_time < 20
            if self.preferred_time != 'any':
                if (self.preferred_time == 'day' and not is_day) or \
                   (self.preferred_time == 'night' and is_day):
                    return 'resting'
                    
            # Check critical needs
            if self.needs['rest'] > 80 or self.energy < 20:
                return 'resting'
                
            if self.needs['thirst'] > 80:
                if self.known_water_sources:
                    return 'drinking'
                    
            if self.needs['hunger'] > 70:
                if self.is_predator:
                    nearby_prey = self._find_nearby_prey()
                    if nearby_prey:
                        return 'hunting'
                else:
                    if self.known_food_sources:
                        return 'moving'
                        
            # Return home if far away and getting dark
            if not is_day and self._distance_to(self.home_location) > self.vision_range * TILE_SIZE:
                return 'returning_home'
                
            # Default behaviors
            if random.random() < 0.3:
                return 'idle'
            return 'moving'
            
        except Exception as e:
            print(f"Error deciding behavior: {e}")
            traceback.print_exc()
            return 'idle'
            
    def _update_movement(self, dt: float):
        """Update animal position with enhanced movement"""
        try:
            # Get current terrain and weather effects
            current_tile = self._get_current_tile()
            weather_effects = WEATHER_EFFECTS.get(self.world.current_weather, {})
            
            # Apply movement modifiers
            speed_modifier = 1.0
            if current_tile:
                # Slow down in non-preferred biomes
                if current_tile['biome'] not in self.preferred_biomes:
                    speed_modifier *= 0.7
                # Apply terrain walkability
                if not current_tile.get('walkable', True):
                    speed_modifier *= 0.3
                    
            # Apply weather effects
            if 'movement_speed' in weather_effects:
                speed_modifier *= weather_effects['movement_speed']
                
            # Update position with modifiers
            self.x += self.velocity[0] * dt * speed_modifier
            self.y += self.velocity[1] * dt * speed_modifier
            
            # Keep within world bounds
            self.x = max(0, min(self.world.width, self.x))
            self.y = max(0, min(self.world.height, self.y))
            
            # Energy cost based on movement
            if self.velocity[0] != 0 or self.velocity[1] != 0:
                energy_cost = 0.5  # Base cost
                if self.state == 'fleeing':
                    energy_cost *= 2
                elif self.state == 'hunting':
                    energy_cost *= 1.5
                self.energy = max(0, self.energy - dt * energy_cost)
                
        except Exception as e:
            print(f"Error updating animal movement: {e}")
            traceback.print_exc()
            
    def _update_status_effects(self, dt: float):
        """Update active status effects"""
        try:
            # Update existing effects
            for effect_name in list(self.status_effects.keys()):
                effect_data = self.status_effects[effect_name]
                
                # Update duration
                if effect_data['duration'] > 0:
                    effect_data['duration'] -= dt
                    if effect_data['duration'] <= 0:
                        self._remove_status_effect(effect_name)
                        continue
                        
                # Apply effect
                self._apply_status_effect(effect_name, effect_data)
                
        except Exception as e:
            print(f"Error updating status effects: {e}")
            traceback.print_exc()
            
    def _update_awareness(self, dt: float):
        """Update animal's awareness of surroundings"""
        try:
            # Clear old information
            self.known_food_sources = [
                source for source in self.known_food_sources
                if self._distance_to(source) <= self.vision_range * TILE_SIZE
            ]
            self.known_water_sources = [
                source for source in self.known_water_sources
                if self._distance_to(source) <= self.vision_range * TILE_SIZE
            ]
            
            # Scan for new resources
            nearby_resources = self.world.get_resources_in_range(
                self.x, self.y, self.vision_range * TILE_SIZE
            )
            for resource in nearby_resources:
                if resource.type == 'water' and resource not in self.known_water_sources:
                    self.known_water_sources.append((resource.x, resource.y))
                elif resource.type == 'food' and resource not in self.known_food_sources:
                    self.known_food_sources.append((resource.x, resource.y))
                    
        except Exception as e:
            print(f"Error updating awareness: {e}")
            traceback.print_exc()
            
    def _get_display_color(self, effects: Dict = None) -> Tuple[int, int, int]:
        """Get the display color based on status"""
        try:
            base_color = self.color
            
            # Apply status effect colors
            if self.status_effects:
                if 'injured' in self.status_effects:
                    return (min(255, base_color[0] * 1.2),
                           max(0, base_color[1] * 0.8),
                           max(0, base_color[2] * 0.8))
                    
            # Apply environmental effects
            if effects and 'visibility' in effects:
                visibility = effects['visibility']
                return tuple(int(c * visibility) for c in base_color)
                
            return base_color
            
        except Exception as e:
            print(f"Error getting display color: {e}")
            traceback.print_exc()
            return (255, 255, 255)
            
    def _draw_status_indicators(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw status effect indicators"""
        try:
            y_offset = -20 * zoom
            for effect_name in self.status_effects:
                if effect_name in STATUS_EFFECTS:
                    # Draw effect icon or symbol
                    font = pygame.font.SysFont('segoe ui emoji', int(12 * zoom))
                    text = font.render('💢' if effect_name == 'injured' else '💫',
                                     True, (255, 255, 255))
                    surface.blit(text, (pos[0], pos[1] + y_offset))
                    y_offset -= 15 * zoom
                    
        except Exception as e:
            print(f"Error drawing status indicators: {e}")
            traceback.print_exc()
            
    def _draw_health_bar(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw health and energy bars"""
        try:
            bar_width = 30 * zoom
            bar_height = 4 * zoom
            y_offset = -10 * zoom
            
            # Health bar
            health_percent = self.health / self.max_health
            pygame.draw.rect(surface, (200, 0, 0),
                           (pos[0], pos[1] + y_offset, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 200, 0),
                           (pos[0], pos[1] + y_offset, bar_width * health_percent, bar_height))
                           
            # Energy bar
            energy_percent = self.energy / self.max_energy
            y_offset -= bar_height + 2
            pygame.draw.rect(surface, (100, 100, 100),
                           (pos[0], pos[1] + y_offset, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 100, 200),
                           (pos[0], pos[1] + y_offset, bar_width * energy_percent, bar_height))
                           
        except Exception as e:
            print(f"Error drawing health bar: {e}")
            traceback.print_exc()
            
    def _determine_preferred_biomes(self) -> List[str]:
        """Determine preferred biomes based on animal type"""
        try:
            if 'wolf' in self.type or 'fox' in self.type:
                return ['forest', 'plains']
            elif 'bear' in self.type:
                return ['forest', 'mountain']
            elif 'deer' in self.type or 'rabbit' in self.type:
                return ['forest', 'plains']
            elif 'fish' in self.type:
                return ['water']
            elif 'bird' in self.type:
                return ['forest', 'plains', 'mountain']
            else:
                return ['plains']  # Default
                
        except Exception as e:
            print(f"Error determining preferred biomes: {e}")
            traceback.print_exc()
            return ['plains']
            
    def _get_current_speed(self) -> float:
        """Get current movement speed based on state and conditions"""
        try:
            base_speed = self.speed
            
            # State modifiers
            if self.state == 'fleeing':
                base_speed *= 1.5
            elif self.state == 'hunting':
                base_speed *= 1.3
            elif self.state == 'resting':
                base_speed *= 0.5
                
            # Energy modifier
            if self.energy < 30:
                base_speed *= 0.7
                
            # Weather modifier
            weather_effects = WEATHER_EFFECTS.get(self.world.current_weather, {})
            if 'movement_speed' in weather_effects:
                base_speed *= weather_effects['movement_speed']
                
            return base_speed
            
        except Exception as e:
            print(f"Error getting current speed: {e}")
            traceback.print_exc()
            return self.speed
            
    def _get_current_tile(self) -> Optional[Dict]:
        """Get the tile at current position"""
        try:
            chunk_x = int(self.x // (TILE_SIZE * self.world.chunk_size))
            chunk_y = int(self.y // (TILE_SIZE * self.world.chunk_size))
            
            if (chunk_x, chunk_y) in self.world.chunks:
                chunk = self.world.chunks[(chunk_x, chunk_y)]
                tile_x = int((self.x % (TILE_SIZE * self.world.chunk_size)) // TILE_SIZE)
                tile_y = int((self.y % (TILE_SIZE * self.world.chunk_size)) // TILE_SIZE)
                return chunk.tiles[tile_y][tile_x]
                
            return None
            
        except Exception as e:
            print(f"Error getting current tile: {e}")
            traceback.print_exc()
            return None
            
    def _distance_to(self, pos: Tuple[float, float]) -> float:
        """Calculate distance to a position"""
        try:
            dx = pos[0] - self.x
            dy = pos[1] - self.y
            return math.sqrt(dx * dx + dy * dy)
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            traceback.print_exc()
            return float('inf')
            
    def _move_towards(self, target_pos: Tuple[float, float]):
        """Move towards a target position"""
        try:
            dx = target_pos[0] - self.x
            dy = target_pos[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 1:
                speed = self._get_current_speed()
                self.velocity[0] = (dx / dist) * speed
                self.velocity[1] = (dy / dist) * speed
            else:
                self.velocity = [0, 0]
                
        except Exception as e:
            print(f"Error moving towards target: {e}")
            traceback.print_exc()
            
    def _assess_threats(self) -> List[Dict]:
        """Assess nearby threats"""
        threats = []
        try:
            # Check for dangerous weather
            if self.world.current_weather in ['storm']:
                threats.append({
                    'type': 'weather',
                    'danger_level': 0.7
                })
                
            # Check for predators if prey
            if self.is_prey:
                nearby_entities = self.world.get_entities_in_range(
                    self.x, self.y, self.vision_range * TILE_SIZE
                )
                for entity in nearby_entities:
                    if isinstance(entity, Animal) and entity.is_predator:
                        threats.append({
                            'type': 'predator',
                            'source': entity,
                            'danger_level': 0.9
                        })
                        
            # Check for environmental hazards
            current_tile = self._get_current_tile()
            if current_tile:
                if not current_tile['walkable']:
                    threats.append({
                        'type': 'terrain',
                        'danger_level': 0.5
                    })
                    
        except Exception as e:
            print(f"Error assessing threats: {e}")
            traceback.print_exc()
            
        return threats
            
    def _find_nearby_prey(self) -> Optional['Animal']:
        """Find nearby prey for predators"""
        try:
            if not self.is_predator:
                return None
                
            nearby_entities = self.world.get_entities_in_range(
                self.x, self.y, self.vision_range * TILE_SIZE
            )
            
            prey = [
                entity for entity in nearby_entities
                if isinstance(entity, Animal) and entity.is_prey
            ]
            
            return random.choice(prey) if prey else None
            
        except Exception as e:
            print(f"Error finding nearby prey: {e}")
            traceback.print_exc()
            return None
            
    def _execute_hunting_behavior(self):
        """Execute hunting behavior for predators"""
        try:
            if not self.is_predator:
                self.state = 'idle'
                return
                
            target = self._find_nearby_prey()
            if target:
                self._move_towards((target.x, target.y))
                
                # Attack if close enough
                if self._distance_to((target.x, target.y)) < self.interaction_range:
                    self._attack(target)
            else:
                self.state = 'moving'
                
        except Exception as e:
            print(f"Error executing hunting behavior: {e}")
            traceback.print_exc()
            
    def _execute_fleeing_behavior(self):
        """Execute fleeing behavior"""
        try:
            threats = self._assess_threats()
            if not threats:
                self.state = 'moving'
                return
                
            # Find safest direction away from threats
            dx = dy = 0
            for threat in threats:
                if 'source' in threat:
                    threat_pos = (threat['source'].x, threat['source'].y)
                    dist = self._distance_to(threat_pos)
                    if dist > 0:
                        dx += (self.x - threat_pos[0]) / dist
                        dy += (self.y - threat_pos[1]) / dist
                        
            if dx != 0 or dy != 0:
                # Normalize direction
                mag = math.sqrt(dx * dx + dy * dy)
                dx /= mag
                dy /= mag
                
                # Set target position away from threats
                flee_distance = self.vision_range * TILE_SIZE
                self.target_pos = (
                    self.x + dx * flee_distance,
                    self.y + dy * flee_distance
                )
                
        except Exception as e:
            print(f"Error executing fleeing behavior: {e}")
            traceback.print_exc()
            
    def _execute_resting_behavior(self, dt: float):
        """Execute resting behavior"""
        try:
            # Regenerate energy while resting
            self.energy = min(self.max_energy,
                            self.energy + dt * 5)
            self.needs['rest'] = max(0,
                                   self.needs['rest'] - dt * 10)
                                   
            # Stop resting if energy is full or there are threats
            if (self.energy >= self.max_energy or
                self.needs['rest'] <= 20 or
                self._assess_threats()):
                self.state = 'idle'
                
        except Exception as e:
            print(f"Error executing resting behavior: {e}")
            traceback.print_exc()
            
    def _execute_drinking_behavior(self, dt: float):
        """Execute drinking behavior"""
        try:
            if not self.known_water_sources:
                self.state = 'moving'
                return
                
            # Move to nearest water source
            nearest_water = min(self.known_water_sources,
                              key=lambda pos: self._distance_to(pos))
            self._move_towards(nearest_water)
            
            # Drink if close enough
            if self._distance_to(nearest_water) < self.interaction_range:
                self.needs['thirst'] = max(0,
                                         self.needs['thirst'] - dt * 20)
                                         
                # Stop drinking if thirst is satisfied
                if self.needs['thirst'] <= 20:
                    self.state = 'idle'
                    
        except Exception as e:
            print(f"Error executing drinking behavior: {e}")
            traceback.print_exc()
            
    def _attack(self, target: 'Animal'):
        """Attack another animal"""
        try:
            # Calculate damage based on predator type
            base_damage = 20
            if 'wolf' in self.type:
                base_damage = 25
            elif 'bear' in self.type:
                base_damage = 30
                
            # Apply damage
            target.health = max(0, target.health - base_damage)
            
            # Add injured status effect to target
            target.status_effects['injured'] = {
                'duration': 10.0,
                'start_time': self.world.time
            }
            
            # Energy cost for attacking
            self.energy = max(0, self.energy - 10)
            
        except Exception as e:
            print(f"Error attacking target: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up animal resources"""
        try:
            print(f"Cleaning up animal {self.type}")
            # Clear references
            self.world = None
            self.target_pos = None
            self.velocity = [0, 0]
            self.known_food_sources.clear()
            self.known_water_sources.clear()
            self.known_threats.clear()
            self.status_effects.clear()
            
        except Exception as e:
            print(f"Error cleaning up animal: {e}")
            traceback.print_exc()