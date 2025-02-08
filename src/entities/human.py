import pygame
import random
import traceback
import math
from typing import Dict, List, Optional, Tuple
from ..constants import (
    ENTITY_TYPES, THOUGHT_TYPES, THOUGHT_INTERVAL,
    THOUGHT_COMPLEXITY_LEVELS, TILE_SIZE, PERSONALITY_TRAITS,
    STATUS_EFFECTS, WEATHER_EFFECTS
)

class Human:
    def __init__(self, world, pos: Tuple[float, float], human_type: str = 'villager'):
        """Initialize human entity with advanced features"""
        try:
            print(f"Creating {human_type} at position {pos}")
            self.world = world
            self.x, self.y = pos
            self.type = human_type
            self.id = f"human_{id(self)}"  # Unique identifier
            
            # Get base properties from entity types
            self.properties = ENTITY_TYPES['human'].copy()
            
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
            self.happiness = 100
            self.stress = 0
            
            # Skills and experience
            self.skills = {
                'farming': 0,
                'mining': 0,
                'crafting': 0,
                'social': 0,
                'combat': 0
            }
            self.experience = 0
            self.level = 1
            
            # Personality traits (randomized)
            self.personality = {}
            for trait, limits in PERSONALITY_TRAITS.items():
                self.personality[trait] = random.uniform(limits['min'], limits['max'])
            
            # Movement and pathfinding
            self.velocity = [0, 0]
            self.target_pos = None
            self.path = []
            self.movement_state = 'idle'  # idle, walking, running
            
            # Thought processing
            self.thoughts: List[Dict] = []
            self.last_thought_time = 0
            self.current_action = None
            self.memory: List[Dict] = []
            self.relationships: Dict[str, float] = {}  # Using entity IDs as keys
            self.mood = 'neutral'
            
            # Status effects
            self.status_effects: Dict[str, Dict] = {}
            
            # Needs
            self.needs = {
                'hunger': 0,
                'thirst': 0,
                'rest': 0,
                'social': 0,
                'safety': 0
            }
            
            # Inventory and equipment
            self.inventory = []
            self.equipped_items = {}
            self.carrying_capacity = 100
            
            print(f"{human_type} created successfully with personality: {self.personality}")
            
        except Exception as e:
            print(f"Error creating human: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update human state with enhanced features"""
        try:
            # Update needs
            self._update_needs(dt)
            
            # Process thoughts and make decisions
            self._process_thoughts(dt)
            
            # Update movement and physics
            self._update_movement(dt)
            
            # Update stats and status effects
            self._update_stats(dt)
            self._update_status_effects(dt)
            
            # Update current action
            if self.current_action:
                action_complete = self.current_action.update(dt)
                if action_complete:
                    self._complete_action()
                    
            # Update relationships
            self._update_relationships(dt)
            
            # Experience and leveling
            self._check_level_up()
            
        except Exception as e:
            print(f"Error updating human: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], zoom: float, effects: Dict = None):
        """Draw human entity with enhanced visuals"""
        try:
            # Calculate screen position
            screen_x = (self.x - camera_pos[0]) * zoom
            screen_y = (self.y - camera_pos[1]) * zoom
            
            # Apply visual effects based on status
            color = self._get_display_color(effects)
            
            # Draw human sprite/emoji with effects
            sprite = self.properties['sprite']
            if isinstance(sprite, str):  # Emoji fallback
                font = pygame.font.SysFont('segoe ui emoji', int(TILE_SIZE * zoom))
                text = font.render(sprite, True, color)
                surface.blit(text, (screen_x, screen_y))
            else:  # Image sprite
                scaled_size = (int(self.size * zoom), int(self.size * zoom))
                scaled_sprite = pygame.transform.scale(sprite, scaled_size)
                # Apply color tint
                tinted_sprite = self._apply_color_tint(scaled_sprite, color)
                surface.blit(tinted_sprite, (screen_x, screen_y))
                
            # Draw status indicators
            self._draw_status_indicators(surface, (screen_x, screen_y), zoom)
            
            # Draw thought bubble if thinking
            if self.thoughts:
                self._draw_thought_bubble(surface, (screen_x, screen_y), zoom)
                
            # Draw health bar
            self._draw_health_bar(surface, (screen_x, screen_y), zoom)
            
        except Exception as e:
            print(f"Error drawing human: {e}")
            traceback.print_exc()
            
    def _process_thoughts(self, dt: float):
        """Process thoughts and make decisions with enhanced features"""
        try:
            current_time = pygame.time.get_ticks() / 1000
            
            # Generate new thought if enough time has passed
            if current_time - self.last_thought_time >= THOUGHT_INTERVAL:
                self.last_thought_time = current_time
                
                # Generate thoughts based on current state and surroundings
                new_thoughts = self._generate_thoughts()
                
                # Filter and prioritize thoughts based on personality
                prioritized_thoughts = self._prioritize_thoughts(new_thoughts)
                
                # Add most important thoughts
                for thought in prioritized_thoughts[:3]:  # Keep top 3 thoughts
                    self.thoughts.append(thought)
                    # Act on highest priority thought
                    if thought == prioritized_thoughts[0]:
                        self._act_on_thought(thought)
                    
                # Update memory with new thoughts
                self._update_memory(prioritized_thoughts)
                
                # Limit thought history
                if len(self.thoughts) > 10:
                    self.thoughts = self.thoughts[-10:]
                    
        except Exception as e:
            print(f"Error processing thoughts: {e}")
            traceback.print_exc()
            
    def _generate_thoughts(self) -> List[Dict]:
        """Generate thoughts based on current state and surroundings"""
        thoughts = []
        try:
            # Need-based thoughts
            for need, value in self.needs.items():
                if value > 70:
                    thoughts.append({
                        'type': 'need',
                        'category': need,
                        'content': f"I really need to address my {need}",
                        'urgency': value / 100,
                        'complexity': THOUGHT_COMPLEXITY_LEVELS['basic']
                    })
                    
            # Environmental thoughts
            weather = self.world.current_weather
            if weather in ['rain', 'storm']:
                thoughts.append({
                    'type': 'environment',
                    'category': 'weather',
                    'content': f"I should find shelter from this {weather}",
                    'urgency': 0.7 if weather == 'storm' else 0.5,
                    'complexity': THOUGHT_COMPLEXITY_LEVELS['simple']
                })
                
            # Time-based thoughts
            if self.world.day_time < 6 or self.world.day_time > 20:
                thoughts.append({
                    'type': 'environment',
                    'category': 'time',
                    'content': "It's dark, I should be careful",
                    'urgency': 0.6,
                    'complexity': THOUGHT_COMPLEXITY_LEVELS['simple']
                })
                
            # Social thoughts
            nearby_humans = self._get_nearby_humans()
            if nearby_humans:
                social_need = self.needs['social']
                if social_need > 50:
                    thoughts.append({
                        'type': 'social',
                        'category': 'interaction',
                        'content': "I should talk to someone",
                        'target': random.choice(nearby_humans),
                        'urgency': social_need / 100,
                        'complexity': THOUGHT_COMPLEXITY_LEVELS['normal']
                    })
                    
            # Work and resource thoughts
            if self.energy > 50:
                nearby_resources = self.world.get_resources_in_range(
                    self.x, self.y, self.vision_range * TILE_SIZE
                )
                if nearby_resources:
                    thoughts.append({
                        'type': 'work',
                        'category': 'gather',
                        'content': f"I could gather those {nearby_resources[0].type}",
                        'target': nearby_resources[0],
                        'urgency': 0.4,
                        'complexity': THOUGHT_COMPLEXITY_LEVELS['normal']
                    })
                    
            # Personality-influenced thoughts
            if self.personality['openness'] > 0.7 and random.random() < 0.3:
                thoughts.append({
                    'type': 'explore',
                    'category': 'curiosity',
                    'content': "I wonder what's beyond those hills",
                    'urgency': 0.3,
                    'complexity': THOUGHT_COMPLEXITY_LEVELS['complex']
                })
                
            if self.personality['conscientiousness'] > 0.7 and random.random() < 0.3:
                thoughts.append({
                    'type': 'work',
                    'category': 'planning',
                    'content': "I should plan for the future",
                    'urgency': 0.4,
                    'complexity': THOUGHT_COMPLEXITY_LEVELS['complex']
                })
                
        except Exception as e:
            print(f"Error generating thoughts: {e}")
            traceback.print_exc()
            
        return thoughts
        
    def _prioritize_thoughts(self, thoughts: List[Dict]) -> List[Dict]:
        """Prioritize thoughts based on personality and current state"""
        try:
            # Calculate priority scores
            for thought in thoughts:
                base_priority = thought['urgency']
                
                # Personality influence
                if thought['type'] == 'explore':
                    base_priority *= (0.5 + self.personality['openness'])
                elif thought['type'] == 'social':
                    base_priority *= (0.5 + self.personality['extraversion'])
                elif thought['type'] == 'work':
                    base_priority *= (0.5 + self.personality['conscientiousness'])
                    
                # Need influence
                if thought['type'] == 'need':
                    base_priority *= 1.5  # Basic needs take priority
                    
                # Stress influence
                if self.stress > 50:
                    if thought['complexity'] > THOUGHT_COMPLEXITY_LEVELS['simple']:
                        base_priority *= 0.5  # Stress reduces complex thought priority
                        
                thought['priority'] = base_priority
                
            # Sort by priority
            return sorted(thoughts, key=lambda x: x['priority'], reverse=True)
            
        except Exception as e:
            print(f"Error prioritizing thoughts: {e}")
            traceback.print_exc()
            return thoughts
            
    def _act_on_thought(self, thought: Dict):
        """Take action based on a thought"""
        try:
            if thought['type'] == 'need':
                if thought['category'] == 'hunger':
                    self._seek_food()
                elif thought['category'] == 'thirst':
                    self._seek_water()
                elif thought['category'] == 'rest':
                    self._find_rest_spot()
                    
            elif thought['type'] == 'social':
                if 'target' in thought:
                    self._approach_target(thought['target'])
                    
            elif thought['type'] == 'work':
                if thought['category'] == 'gather' and 'target' in thought:
                    self._gather_resource(thought['target'])
                else:
                    self._find_work()
                    
            elif thought['type'] == 'explore':
                self._explore_surroundings()
                
            elif thought['type'] == 'environment':
                if thought['category'] == 'weather':
                    self._seek_shelter()
                    
        except Exception as e:
            print(f"Error acting on thought: {e}")
            traceback.print_exc()
            
    def _update_needs(self, dt: float):
        """Update basic needs"""
        try:
            # Increase needs over time
            self.needs['hunger'] = min(100, self.needs['hunger'] + dt * 2)
            self.needs['thirst'] = min(100, self.needs['thirst'] + dt * 3)
            self.needs['rest'] = min(100, self.needs['rest'] + dt * 1.5)
            
            # Social need changes based on nearby humans
            nearby_humans = self._get_nearby_humans()
            if nearby_humans:
                self.needs['social'] = max(0, self.needs['social'] - dt * 5)
            else:
                self.needs['social'] = min(100, self.needs['social'] + dt)
                
            # Safety need based on environment
            threats = self._assess_threats()
            self.needs['safety'] = min(100, 20 * len(threats))
            
        except Exception as e:
            print(f"Error updating needs: {e}")
            traceback.print_exc()
            
    def _update_stats(self, dt: float):
        """Update human stats"""
        try:
            # Energy consumption
            energy_cost = 0.5  # Base cost
            if self.movement_state == 'walking':
                energy_cost *= 1.5
            elif self.movement_state == 'running':
                energy_cost *= 3.0
                
            self.energy = max(0, self.energy - dt * energy_cost)
            
            # Health regeneration when resting
            if self.movement_state == 'idle' and self.energy > 20:
                self.health = min(self.max_health, self.health + dt * 0.5)
                
            # Happiness and stress updates
            self._update_happiness()
            self._update_stress(dt)
            
            # Apply weather effects
            weather_effects = WEATHER_EFFECTS.get(self.world.current_weather, {})
            if 'movement_speed' in weather_effects:
                self.speed = self.properties['speed'] * weather_effects['movement_speed']
                
        except Exception as e:
            print(f"Error updating stats: {e}")
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
            
    def _apply_status_effect(self, effect_name: str, effect_data: Dict):
        """Apply a status effect's modifications"""
        try:
            effect_props = STATUS_EFFECTS[effect_name]
            
            # Apply stat modifications
            if 'energy_regen' in effect_props:
                self.energy = min(self.max_energy,
                                self.energy + effect_props['energy_regen'])
                                
            if 'energy_drain' in effect_props:
                self.energy = max(0, self.energy - effect_props['energy_drain'])
                
            if 'health_drain' in effect_props:
                self.health = max(0, self.health - effect_props['health_drain'])
                
            if 'mood_boost' in effect_props:
                self.happiness = min(100, self.happiness + effect_props['mood_boost'])
                
            if 'mood_penalty' in effect_props:
                self.happiness = max(0, self.happiness - effect_props['mood_penalty'])
                
        except Exception as e:
            print(f"Error applying status effect: {e}")
            traceback.print_exc()
            
    def _remove_status_effect(self, effect_name: str):
        """Remove a status effect"""
        try:
            if effect_name in self.status_effects:
                del self.status_effects[effect_name]
                
        except Exception as e:
            print(f"Error removing status effect: {e}")
            traceback.print_exc()
            
    def _get_display_color(self, effects: Dict = None) -> Tuple[int, int, int]:
        """Get the display color based on status"""
        try:
            base_color = self.properties['color']
            
            # Apply status effect colors
            if self.status_effects:
                # Example: Tint red when injured
                if 'sick' in self.status_effects:
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
                    text = font.render('⚡' if effect_name == 'energized' else '💫',
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
            
    def _draw_thought_bubble(self, surface: pygame.Surface, pos: Tuple[float, float], zoom: float):
        """Draw thought bubble with current thoughts"""
        try:
            if not self.thoughts:
                return
                
            # Draw the most recent thought
            thought = self.thoughts[-1]
            font = pygame.font.SysFont('arial', int(12 * zoom))
            text = font.render(thought['content'], True, (0, 0, 0))
            
            # Draw bubble background
            padding = 5 * zoom
            bubble_rect = pygame.Rect(
                pos[0] - padding,
                pos[1] - 40 * zoom,
                text.get_width() + padding * 2,
                text.get_height() + padding * 2
            )
            
            pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=int(5 * zoom))
            pygame.draw.rect(surface, (0, 0, 0), bubble_rect, width=1, border_radius=int(5 * zoom))
            
            # Draw thought text
            surface.blit(text, (pos[0], pos[1] - 40 * zoom))
            
        except Exception as e:
            print(f"Error drawing thought bubble: {e}")
            traceback.print_exc()
            
    def _get_nearby_humans(self) -> List['Human']:
        """Get nearby human entities"""
        try:
            nearby = self.world.get_entities_in_range(
                self.x, self.y, self.vision_range * TILE_SIZE
            )
            return [e for e in nearby if isinstance(e, Human) and e != self]
            
        except Exception as e:
            print(f"Error getting nearby humans: {e}")
            traceback.print_exc()
            return []
            
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
                
            # Check for dangerous entities
            nearby_entities = self.world.get_entities_in_range(
                self.x, self.y, self.vision_range * TILE_SIZE
            )
            for entity in nearby_entities:
                if hasattr(entity, 'is_hostile') and entity.is_hostile:
                    threats.append({
                        'type': 'entity',
                        'source': entity,
                        'danger_level': 0.8
                    })
                    
            # Check for environmental hazards
            if self.world.current_season == 'Winter' and self.world.day_time < 6:
                threats.append({
                    'type': 'environment',
                    'danger_level': 0.5
                })
                
        except Exception as e:
            print(f"Error assessing threats: {e}")
            traceback.print_exc()
            
        return threats
            
    def _update_happiness(self):
        """Update happiness based on various factors"""
        try:
            # Base happiness decay
            self.happiness = max(0, self.happiness - 0.1)
            
            # Needs impact
            for need, value in self.needs.items():
                if value > 80:
                    self.happiness = max(0, self.happiness - 0.2)
                elif value < 20:
                    self.happiness = min(100, self.happiness + 0.1)
                    
            # Social impact
            if self._get_nearby_humans():
                if self.personality['extraversion'] > 0.5:
                    self.happiness = min(100, self.happiness + 0.2)
                    
            # Weather impact
            if self.world.current_weather == 'clear':
                self.happiness = min(100, self.happiness + 0.1)
            elif self.world.current_weather == 'storm':
                self.happiness = max(0, self.happiness - 0.2)
                
        except Exception as e:
            print(f"Error updating happiness: {e}")
            traceback.print_exc()
            
    def _update_stress(self, dt: float):
        """Update stress levels"""
        try:
            # Base stress decay
            self.stress = max(0, self.stress - dt)
            
            # Increase stress based on various factors
            if self.health < 50:
                self.stress = min(100, self.stress + dt * 2)
                
            if self.energy < 30:
                self.stress = min(100, self.stress + dt)
                
            if self._assess_threats():
                self.stress = min(100, self.stress + dt * 3)
                
            # Personality influence
            if self.personality['neuroticism'] > 0.7:
                self.stress = min(100, self.stress + dt * 0.5)
                
        except Exception as e:
            print(f"Error updating stress: {e}")
            traceback.print_exc()
            
    def _update_relationships(self, dt: float):
        """Update relationships with other humans"""
        try:
            nearby_humans = self._get_nearby_humans()
            for human in nearby_humans:
                if human.id not in self.relationships:
                    # Initialize new relationship with random starting value
                    self.relationships[human.id] = random.uniform(0, 0.3)
                    
                # Update relationship based on personality compatibility
                compatibility = self._calculate_compatibility(human)
                current_value = self.relationships[human.id]
                
                if compatibility > 0.7:
                    self.relationships[human.id] = min(1.0, current_value + dt * 0.1)
                elif compatibility < 0.3:
                    self.relationships[human.id] = max(0.0, current_value - dt * 0.05)
                    
        except Exception as e:
            print(f"Error updating relationships: {e}")
            traceback.print_exc()
            
    def _calculate_compatibility(self, other: 'Human') -> float:
        """Calculate compatibility with another human"""
        try:
            compatibility = 0.5  # Base compatibility
            
            # Compare personality traits
            for trait in PERSONALITY_TRAITS:
                diff = abs(self.personality[trait] - other.personality[trait])
                if trait in ['openness', 'agreeableness']:
                    # Some traits work better with similarity
                    compatibility += (1 - diff) * 0.1
                else:
                    # Some traits work better with complementary values
                    compatibility += (0.5 - abs(0.5 - diff)) * 0.1
                    
            return max(0, min(1, compatibility))
            
        except Exception as e:
            print(f"Error calculating compatibility: {e}")
            traceback.print_exc()
            return 0.5
            
    def _check_level_up(self):
        """Check for level up and apply rewards"""
        try:
            exp_needed = self.level * 100
            if self.experience >= exp_needed:
                self.level += 1
                self.experience -= exp_needed
                
                # Increase stats
                self.max_health += 10
                self.max_energy += 5
                self.health = self.max_health
                self.energy = self.max_energy
                
                # Add status effect for level up
                self.status_effects['inspired'] = {
                    'duration': 300,  # 5 minutes
                    'start_time': self.world.time
                }
                
                print(f"Level up! {self.type} is now level {self.level}")
                
        except Exception as e:
            print(f"Error checking level up: {e}")
            traceback.print_exc()