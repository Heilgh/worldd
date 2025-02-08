import random
import math
import pygame
import traceback
from typing import Dict, List, Optional, Tuple
from ...constants import (
    ENTITY_STATES,
    ENTITY_NEEDS,
    ENTITY_TYPES,
    RESOURCE_TYPES,
    TILE_SIZE,
    MOODS,
    PERSONALITY_TRAITS,
    INTERACTION_TYPES,
    HUMAN_TYPES,
    THOUGHT_TYPES,
    UI_COLORS
)
from .entity import Entity
from ..systems.thought_system import ThoughtSystem
from ..systems.action_system import ActionSystem
from ..systems.language_system import LanguageSystem

class Human(Entity):
    def __init__(self, world, x: float, y: float, human_type: str = 'villager'):
        """Initialize a human entity with thoughts and behaviors"""
        super().__init__(world, x, y)
        
        # Validate human type
        if human_type not in HUMAN_TYPES:
            print(f"Warning: Invalid human type '{human_type}', defaulting to 'villager'")
            human_type = 'villager'
            
        self.type = 'human'
        self.subtype = human_type
        
        # Get properties from HUMAN_TYPES
        self.properties = HUMAN_TYPES[human_type].copy()
        
        # Set basic attributes
        self.sprite = self.properties.get('sprite', '👤')  # Default sprite if not specified
        self.speed = self.properties.get('speed', 2.0)
        self.size = self.properties.get('size', TILE_SIZE)
        self.vision_range = self.properties.get('vision_range', 8)
        self.intelligence = self.properties.get('intelligence', 1.0)
        self.skills = self.properties.get('starting_skills', {}).copy()
        
        # Initialize stats
        self.health = 100
        self.energy = 100
        self.hunger = 0
        self.thirst = 0
        self.happiness = 100
        self.stress = 0
        
        # Initialize needs
        self.needs = {
            'hunger': 0,
            'thirst': 0,
            'energy': 100,
            'social': 50,
            'comfort': 50,
            'safety': 100
        }
        
        # State tracking
        self.state = {
            'current': 'idle',
            'timer': 0,
            'target': None,
            'path': [],
            'mood': 'content',
            'emotion': None
        }
        
        # Initialize thought system
        self.thought_system = None
        if hasattr(world, 'systems') and 'thought' in world.systems:
            self.thought_system = world.systems['thought']
            
        # Initialize relationships and memory
        self.relationships = {}
        self.memory = []
        self.current_thought = None
        
        # Initialize personality traits
        self.personality = {}
        for trait, limits in PERSONALITY_TRAITS.items():
            self.personality[trait] = random.uniform(0.2, 0.8)
            
        print(f"Created human of type {human_type} at position ({x}, {y})")
        
        # Initialize appearance
        self.colors = {
            'skin': self._generate_skin_color(),
            'hair': self._generate_hair_color(),
            'clothes': self._generate_clothes_colors()
        }
        
        # Initialize systems
        self.systems = {
            'thought': ThoughtSystem(self),
            'language': LanguageSystem()
        }
        
        # Initialize systems with world reference
        if world:
            self.systems['thought'].initialize(world)
            self.systems['language'].initialize(world)
        
        # Initialize inventory and equipment
        self.inventory = []
        self.equipment = {}
        
        # Initialize social attributes
        self.home_location = None
        self.current_task = None
        self.daily_schedule = self._create_daily_schedule()
        
        # Status effects
        self.status_effects = []
        
        # Generate name
        self.name = self._generate_name()
        
        # Initialize needs before super().__init__
        self.needs = {
            'hunger': 100.0,
            'thirst': 100.0,
            'energy': 100.0,
            'social': 100.0,
            'hygiene': 100.0,
            'entertainment': 100.0,
            'comfort': 100.0
        }
        
        # Call parent constructor
        super().__init__(world, x, y)
        
        # Basic attributes
        self.age = random.randint(18, 60)
        self.gender = random.choice(['male', 'female'])
        self.max_health = 100.0
        
        # Appearance
        self.sprite = '👨' if self.gender == 'male' else '👩'
        self.color = (255, 220, 180)  # Skin tone
        
        # Movement
        self.direction = random.uniform(0, 2 * math.pi)
        self.target_position = None
        
        # Initialize rect for UI
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)
        
        # Stats and skills
        self.stats = {
            'strength': random.uniform(0.5, 1.0),
            'intelligence': random.uniform(0.5, 1.0),
            'charisma': random.uniform(0.5, 1.0),
            'dexterity': random.uniform(0.5, 1.0)
        }
        
        # Initialize surface
        self._init_surface()
        
    def _generate_personality(self):
        """Generate random personality traits"""
        personality = {}
        for trait in PERSONALITY_TRAITS:
            personality[trait] = random.random()
        return personality
        
    def update(self, world, dt):
        """Update human state and behavior"""
        try:
            super().update(world, dt)
            
            # Update systems
            if 'thought' in self.systems:
                self.systems['thought'].update(dt)
            if 'language' in self.systems:
                self.systems['language'].update(world, dt)
            
            # Update needs
            self._update_needs(dt)
            
            # Update current task
            self._update_task(dt)
            
            # Check schedule
            self._check_schedule(world.time_system)
            
            # Handle interactions
            self._handle_interactions()
            
            # Update relationships
            self._update_relationships(world, dt)
            
            # Update visual effects
            self._update_visual_effects(dt)
            
            # Process status effects
            self._process_status_effects(dt)
            
            # Update state timers
            if self.state['timer'] > 0:
                self.state['timer'] -= dt
                if self.state['timer'] <= 0:
                    self._complete_current_state()
                    
            # Update rect position
            self.rect.x = self.x - 16
            self.rect.y = self.y - 16
            
        except Exception as e:
            print(f"Error updating human {self.name}: {e}")
            traceback.print_exc()
            
    def _update_needs(self, dt):
        """Update basic needs"""
        # Increase hunger and thirst over time
        self.hunger = min(100, self.hunger + 2 * dt)
        self.thirst = min(100, self.thirst + 3 * dt)
        
        # Decrease energy while awake
        if self.current_task != 'sleeping':
            self.energy = max(0, self.energy - 1 * dt)
            
        # Update happiness based on needs
        happiness_factors = [
            (100 - self.hunger) / 100,
            (100 - self.thirst) / 100,
            self.energy / 100
        ]
        self.happiness = sum(happiness_factors) / len(happiness_factors) * 100
        
    def _create_daily_schedule(self):
        """Create a daily schedule based on human type"""
        try:
            # Get daily routines from properties
            routines = self.properties.get('daily_routines', ['work', 'socialize', 'rest'])
            
            # Create schedule with time slots
            schedule = {
                'morning': {
                    'time': (6, 12),
                    'activities': ['wake_up', random.choice(routines)]
                },
                'afternoon': {
                    'time': (12, 18),
                    'activities': [random.choice(routines), 'eat']
                },
                'evening': {
                    'time': (18, 22),
                    'activities': ['socialize', random.choice(routines)]
                },
                'night': {
                    'time': (22, 6),
                    'activities': ['sleep']
                }
            }
            
            return schedule
            
        except Exception as e:
            print(f"Error creating daily schedule: {e}")
            traceback.print_exc()
            return {
                'morning': {'time': (6, 12), 'activities': ['rest']},
                'afternoon': {'time': (12, 18), 'activities': ['rest']},
                'evening': {'time': (18, 22), 'activities': ['rest']},
                'night': {'time': (22, 6), 'activities': ['sleep']}
            }
        
    def _check_schedule(self, time_system):
        """Check and follow daily schedule"""
        current_hour = time_system['hour']
        
        if current_hour in self.daily_schedule:
            new_task = self.daily_schedule[current_hour]
            if new_task != self.current_task:
                self.current_task = new_task
                
    def _handle_interactions(self):
        """Handle interactions with other entities"""
        if not self.world:
            return
            
        nearby = self.world.get_entities_in_range(self.x, self.y, 50)
        for entity in nearby:
            if entity != self:
                self._interact_with(entity)
                
    def _interact_with(self, entity):
        """Interact with another entity"""
        if isinstance(entity, Human):
            # Update relationship
            if entity not in self.relationships:
                self.relationships[entity] = {
                    'value': 0,
                    'type': 'neutral',
                    'last_interaction': 0
                }
            
            # Random chance to interact
            if random.random() < 0.1:
                relationship = self.relationships[entity]
                relationship['value'] += random.uniform(-0.1, 0.2)
                relationship['last_interaction'] = self.world.time if self.world else 0
                
                # Update relationship type based on value
                if relationship['value'] > 0.5:
                    relationship['type'] = 'friend'
                elif relationship['value'] < -0.5:
                    relationship['type'] = 'enemy'
                else:
                    relationship['type'] = 'neutral'
                    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw the human with thought bubbles and status indicators"""
        try:
            # Call parent draw method first
            super().draw(screen, camera_x, camera_y, zoom)
            
            # Calculate screen position
            screen_x = int((self.x - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Draw thought bubble if thinking
            if hasattr(self, 'current_thought') and self.current_thought:
                self._draw_thought_bubble(screen, screen_x, screen_y, zoom)
            
            # Draw mood indicator
            if hasattr(self, 'state') and 'mood' in self.state:
                mood_colors = {
                    'happy': (50, 220, 50),
                    'content': (220, 220, 50),
                    'neutral': (200, 200, 200),
                    'sad': (220, 50, 50),
                    'angry': (255, 0, 0)
                }
                mood_color = mood_colors.get(self.state['mood'], (200, 200, 200))
                mood_size = int(4 * zoom)
                mood_x = screen_x + int(self.size * zoom / 2) + mood_size
                mood_y = screen_y - int(self.size * zoom / 2)
                
                # Draw mood indicator with glow effect
                glow_surf = pygame.Surface((mood_size * 3, mood_size * 3), pygame.SRCALPHA)
                glow_color = (*mood_color, 100)  # Add alpha for glow
                pygame.draw.circle(glow_surf, glow_color,
                                (mood_size * 1.5, mood_size * 1.5),
                                mood_size * 1.5)
                screen.blit(glow_surf,
                           (mood_x - mood_size * 1.5,
                            mood_y - mood_size * 1.5))
                
                # Draw main mood indicator
                pygame.draw.circle(screen, mood_color,
                                (mood_x, mood_y), mood_size)
            
            # Draw current action/state indicator
            if hasattr(self, 'state') and 'current' in self.state:
                try:
                    state_emoji = {
                        'idle': '💭',
                        'moving': '🚶',
                        'working': '⚒️',
                        'resting': '😴',
                        'socializing': '👥',
                        'eating': '🍽️',
                        'sleeping': '💤'
                    }.get(self.state['current'], '❓')
                    
                    emoji_size = int(16 * zoom)
                    emoji_font = pygame.font.SysFont('segoe ui emoji', emoji_size)
                    emoji_surface = emoji_font.render(state_emoji, True, (0, 0, 0))
                    emoji_rect = emoji_surface.get_rect(
                        centerx=screen_x,
                        bottom=screen_y - int(self.size * zoom)
                    )
                    screen.blit(emoji_surface, emoji_rect)
                except Exception as e:
                    print(f"Error drawing state emoji: {e}")
                
        except Exception as e:
            print(f"Error drawing human: {e}")
            traceback.print_exc()

    def _draw_thought_bubble(self, screen, screen_x, screen_y, zoom):
        """Draw thought bubble above the human"""
        try:
            # Get current thought
            thought = self.current_thought
            if not thought:
                return
            
            # Calculate bubble dimensions
            bubble_width = int(200 * zoom)
            bubble_height = int(100 * zoom)
            padding = int(10 * zoom)
            
            # Create bubble surface
            bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
            
            # Draw bubble background
            pygame.draw.ellipse(bubble_surface, (255, 255, 255, 220),
                              (0, 0, bubble_width-padding*2, bubble_height-padding*2))
            
            # Draw bubble border
            pygame.draw.ellipse(bubble_surface, (100, 100, 100, 255),
                              (0, 0, bubble_width-padding*2, bubble_height-padding*2), 2)
            
            # Draw thought text
            font_size = int(24 * zoom)
            font = pygame.font.Font(None, font_size)
            
            # Word wrap text
            words = str(thought).split()
            lines = []
            current_line = words[0] if words else ''
            
            for word in words[1:]:
                test_line = current_line + ' ' + word
                if font.size(test_line)[0] <= bubble_width - padding*4:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            
            # Draw text lines
            y_offset = padding
            for line in lines:
                text_surface = font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(
                    centerx=bubble_width//2,
                    top=y_offset
                )
                bubble_surface.blit(text_surface, text_rect)
                y_offset += text_surface.get_height() + 2
            
            # Draw connecting circles
            circle_positions = [
                (bubble_width//4, bubble_height-padding),
                (bubble_width//4-5, bubble_height-padding+5),
                (bubble_width//4-10, bubble_height-padding+10)
            ]
            for pos in circle_positions:
                pygame.draw.circle(bubble_surface, (255, 255, 255, 220), pos, 5)
                pygame.draw.circle(bubble_surface, (100, 100, 100, 255), pos, 5, 1)
            
            # Draw final bubble
            screen.blit(bubble_surface,
                       (screen_x - bubble_width//2,
                        screen_y - bubble_height - int(self.size * zoom)))
                    
        except Exception as e:
            print(f"Error drawing thought bubble: {e}")
            traceback.print_exc()

    def add_memory(self, memory: Dict) -> None:
        """Add a new memory"""
        self.memory.append(memory)
        if len(self.memory) > 100:  # Keep last 100 memories
            self.memory.pop(0)
            
    def get_state(self) -> Dict:
        """Get current state for saving"""
        return {
            'type': self.type,
            'subtype': self.subtype,
            'x': self.x,
            'y': self.y,
            'health': self.health,
            'energy': self.energy,
            'hunger': self.hunger,
            'thirst': self.thirst,
            'happiness': self.happiness,
            'skills': self.skills,
            'personality': self.personality,
            'state': self.state,
            'current_task': self.current_task
        }

    def _generate_skin_color(self):
        """Generate a random skin color"""
        # Generate a natural skin tone
        base_colors = [
            (255, 224, 189),  # Light
            (241, 194, 125),  # Medium
            (224, 172, 105),  # Tan
            (198, 134, 66),   # Dark
            (141, 85, 36)     # Very Dark
        ]
        return random.choice(base_colors)
        
    def _generate_hair_color(self):
        """Generate a random hair color"""
        # Natural hair colors
        hair_colors = [
            (0, 0, 0),        # Black
            (89, 47, 42),     # Dark Brown
            (148, 93, 50),    # Brown
            (205, 155, 29),   # Blonde
            (165, 42, 42),    # Red
            (128, 128, 128)   # Gray
        ]
        return random.choice(hair_colors)
        
    def _generate_clothes_colors(self):
        """Generate random clothing colors"""
        # Basic clothing colors
        clothing_colors = [
            (65, 105, 225),   # Royal Blue
            (34, 139, 34),    # Forest Green
            (139, 69, 19),    # Saddle Brown
            (128, 0, 0),      # Maroon
            (75, 0, 130),     # Indigo
            (47, 79, 79),     # Dark Slate Gray
            (119, 136, 153)   # Light Slate Gray
        ]
        return {
            'top': random.choice(clothing_colors),
            'bottom': random.choice(clothing_colors)
        }
        
    def interact_with(self, other_human, world) -> None:
        """Interact with another human"""
        try:
            # Initialize relationship if not exists
            if other_human.id not in self.relationships:
                compatibility = self._calculate_compatibility(other_human)
                self.relationships[other_human.id] = {
                    'type': 'neutral',
                    'value': 0
                }
                self.relationships[other_human.id]['compatibility'] = compatibility
            
            # Generate interaction context
            context = {
                'activity': self.state['current'],
                'location': self._get_current_biome(world),
                'mood': self.state['mood'],
                'compatibility': self.relationships[other_human.id]['compatibility']
            }
            
            # Update relationship based on interaction
            rel_change = random.uniform(0, 10)  # Base change
            rel_change *= (1 + self.relationships[other_human.id]['compatibility'])  # Modify by compatibility
            
            # Apply relationship change
            self.relationships[other_human.id]['value'] = max(-100, min(100,
                self.relationships[other_human.id]['value'] + rel_change
            ))
            
            # Record interaction
            self.social['recent_interactions'].append({
                'human_id': other_human.id,
                'context': context,
                'time': world.time
            })
            
            # Update social need
            self.skills['social'] = min(100, self.skills['social'] + 20)
            
            # Generate thought about interaction
            self.state['thought'] = world.thought_system.generate_social_thought(self, other_human)
            
            # Share knowledge
            self._share_knowledge(other_human)
            
            # Show social emotion
            self.state['emotion'] = 'happy' if self.relationships[other_human.id]['type'] == 'friend' else 'thinking'
            
        except Exception as e:
            print(f"Error during human interaction: {e}")
            traceback.print_exc()

    def _calculate_compatibility(self, other_human):
        """Calculate personality compatibility with another human"""
        compatibility = 0
        for trait, value in self.personality.items():
            other_value = other_human.personality[trait]
            diff = abs(value - other_value)
            compatibility += 1 - diff  # Higher for similar values
        return compatibility / len(self.personality)  # Normalize to 0-1

    def _share_knowledge(self, other_human):
        """Share knowledge with another human"""
        # Share some known locations
        for loc_type in ['resources', 'dangers', 'social_spots']:
            if self.known_locations[loc_type]:
                shared_loc = random.choice(self.known_locations[loc_type])
                if shared_loc not in other_human.known_locations[loc_type]:
                    other_human.known_locations[loc_type].append(shared_loc)

        # Share some conversation topics
        if self.social['conversation_topics']:
            topic = random.choice(self.social['conversation_topics'])
            if topic not in other_human.social['conversation_topics']:
                other_human.social['conversation_topics'].append(topic)

    def _draw_fallback_graphics(self, surface, size):
        """Draw basic graphics when emoji rendering fails"""
        try:
            # Calculate center and sizes
            center_x = size // 2
            center_y = size // 2
            head_size = int(size * 0.3)
            body_height = int(size * 0.4)
            
            # Draw body
            body_rect = pygame.Rect(
                center_x - size//4,
                center_y - body_height//2,
                size//2,
                body_height
            )
            pygame.draw.rect(surface, self.colors['clothes']['top'], body_rect)
            
            # Draw head
            pygame.draw.circle(surface, self.colors['skin'],
                            (center_x, center_y - body_height//2),
                            head_size)
            
            # Draw face
            eye_size = max(2, size//25)
            eye_offset = head_size//2
            
            # Draw eyes
            for i in [-1, 1]:
                eye_x = center_x + i*eye_offset//2
                eye_y = center_y - body_height//2 - 2
                pygame.draw.circle(surface, (0, 0, 0), (eye_x, eye_y), eye_size)
            
            # Draw mouth based on mood
            mouth_y = center_y - body_height//2 + head_size//3
            if self.state['mood'] == 'happy':
                # Happy smile
                mouth_rect = pygame.Rect(
                    center_x - head_size//2,
                    mouth_y - head_size//4,
                    head_size,
                    head_size//2
                )
                pygame.draw.arc(surface, (139, 0, 0), mouth_rect, 0, math.pi, 2)
            else:
                # Neutral line
                pygame.draw.line(surface, (139, 0, 0),
                               (center_x - head_size//3, mouth_y),
                               (center_x + head_size//3, mouth_y),
                               2)
            
            return surface
            
        except Exception as e:
            print(f"Error drawing fallback graphics: {e}")
            return surface

    def _update_visual_effects(self, dt):
        """Update visual effects for thoughts and emotions"""
        super()._update_visual_effects(dt)  # Call parent class method
        
        current_time = pygame.time.get_ticks() / 1000
        
        # Update thought bubble
        if self.state.get('thought'):
            if current_time - self.state.get('last_thought_time', 0) >= 1.0:
                # Generate both native and English thoughts
                native_thought = self._generate_native_thought(
                    self.state.get('thought_type', 'observation'),
                    self.state.get('thought_context')
                )
                
                # Format thought text
                thought_text = f"{native_thought}\n{self.state['thought']}"
                
                # Create thought bubble effect
                self.add_visual_effect(
                    'text',
                    text=thought_text,
                    lifetime=2.0,
                    font_size=14,
                    text_color=(0, 0, 0),
                    background_color=(255, 255, 255, 200),
                    padding=5
                )
                
                self.state['last_thought_time'] = current_time
        
        # Update emotion icon
        if self.state.get('emotion'):
            if current_time - self.state.get('last_emotion_time', 0) >= 1.0:
                emotion_icon = self.emotion_icons.get(self.state['emotion'], '🤔')
                self.add_visual_effect(
                    'text',
                    text=emotion_icon,
                    lifetime=1.5,
                    font_size=20,
                    text_color=(0, 0, 0)
                )
                self.state['last_emotion_time'] = current_time 

    def _update_relationships(self, world, dt):
        """Update relationships with other humans"""
        try:
            # Decay relationship values slightly over time
            for entity_id in self.relationships:
                rel = self.relationships[entity_id]
                if abs(rel['value']) > 0:
                    decay = math.copysign(dt * 0.1, -rel['value'])  # Decay towards neutral
                    rel['value'] = max(-100, min(100, rel['value'] + decay))
            
            # Update relationship types based on values
            for entity_id, rel in self.relationships.items():
                if rel['value'] >= 30:
                    rel['type'] = 'friend'
                    if entity_id not in self.social['friends']:
                        self.social['friends'].append(entity_id)
                elif rel['value'] <= -30:
                    rel['type'] = 'dislike'
                    if entity_id in self.social['friends']:
                        self.social['friends'].remove(entity_id)
                else:
                    rel['type'] = 'neutral'
                    if entity_id in self.social['friends']:
                        self.social['friends'].remove(entity_id)
                        
            # Clean up old interactions
            self.social['recent_interactions'] = [
                interact for interact in self.social['recent_interactions']
                if world.time - interact['time'] < 24  # Keep last 24 hours
            ]
            
        except Exception as e:
            print(f"Error updating relationships for {self.name}: {e}")

    def _generate_native_thought(self, thought_type, context=None):
        """Generate a thought in the constructed language"""
        if not hasattr(self, 'language') or not self.language:
            return ""
            
        try:
            # Basic thought templates
            templates = {
                'observation': ['look', 'see'],
                'need': ['want', 'need'],
                'emotion': ['feel', 'think'],
                'action': ['do', 'make']
            }
            
            # Get root words for the thought
            roots = self.language.get('word_roots', {})
            suffixes = self.language.get('suffixes', {})
            
            # Select template words
            template_words = templates.get(thought_type, ['think'])
            base_word = random.choice(template_words)
            
            # Construct basic thought
            if base_word in roots:
                thought = roots[base_word]
                if context and context in roots:
                    thought += roots[context]
                if thought_type in suffixes:
                    thought += suffixes[thought_type]
                return thought.capitalize()
            
            return ""  # Return empty string if construction fails
            
        except Exception as e:
            print(f"Error generating native thought: {e}")
            return ""

    def _update_task(self, dt):
        """Update current task"""
        if self.current_task:
            if self.current_task == 'wake_up':
                self.state['current'] = 'idle'
                self.state['timer'] = 60  # Wake up takes 1 minute
            elif self.current_task == 'gather_food':
                self.state['current'] = 'idle'
                self.state['timer'] = 60  # Gather food takes 1 minute
            elif self.current_task == 'eat':
                self.state['current'] = 'idle'
                self.state['timer'] = 60  # Eat takes 1 minute
            elif self.current_task == 'work':
                self.state['current'] = 'idle'
                self.state['timer'] = 60  # Work takes 1 minute
            elif self.current_task == 'socialize':
                self.state['current'] = 'idle'
                self.state['timer'] = 60  # Socialize takes 1 minute
            elif self.current_task == 'sleep':
                self.state['current'] = 'sleeping'
                self.state['timer'] = 60 * 8  # Sleep takes 8 minutes
            else:
                self.state['current'] = 'idle'
                self.state['timer'] = 0
        else:
            self.state['current'] = 'idle'
            self.state['timer'] = 0

    def _process_status_effects(self, dt):
        """Process status effects"""
        for effect in self.status_effects:
            if effect['type'] == 'healing':
                self.health = min(100, self.health + effect['amount'] * dt)
            elif effect['type'] == 'energy':
                self.energy = min(100, self.energy + effect['amount'] * dt)
            elif effect['type'] == 'hunger':
                self.hunger = max(0, self.hunger - effect['amount'] * dt)
            elif effect['type'] == 'thirst':
                self.thirst = max(0, self.thirst - effect['amount'] * dt)
            elif effect['type'] == 'happiness':
                self.happiness = min(100, self.happiness + effect['amount'] * dt)
            elif effect['type'] == 'stress':
                self.stress = max(0, self.stress - effect['amount'] * dt)
            elif effect['type'] == 'mood':
                self.state['mood'] = effect['mood']
            elif effect['type'] == 'emotion':
                self.state['emotion'] = effect['emotion']
            elif effect['type'] == 'thought':
                self.state['thought'] = effect['text']
                self.state['thought_type'] = effect['type']
                self.state['thought_context'] = effect['context']
            elif effect['type'] == 'visual_effect':
                self.add_visual_effect(**effect['params'])

    def _complete_current_state(self):
        """Complete the current state"""
        self.state['current'] = 'idle'
        self.state['timer'] = 0
        self.state['target'] = None
        self.state['path'] = []
        self.state['mood'] = 'content'
        self.state['emotion'] = None
        self.state['thought'] = None
        self.state['last_thought_time'] = 0
        self.state['last_emotion_time'] = 0
        self.state['current_activity'] = None

    def _generate_name(self) -> str:
        """Generate a random name"""
        syllables = ['ka', 'ri', 'ta', 'mo', 'lu', 'sa', 'ni', 'po']
        return ''.join(random.choice(syllables) for _ in range(random.randint(2, 3))).capitalize()

    def process_thought(self, dt):
        """Process thoughts and generate actions"""
        try:
            if 'thought' not in self.systems:
                return
                
            context = self._get_current_context()
            thought = self.systems['thought'].generate_thought(context)
            if not thought:
                return
            
            # Store thought in memory
            self.memory.append({
                'type': 'thought',
                'content': thought,
                'time': self.world.time_system['time'],
                'context': context
            })
            
            # Convert thought to action
            action = self._thought_to_action(thought, context)
            if action:
                self.action_system.queue_action(action)
            
        except Exception as e:
            print(f"Error processing thought for {self.name}: {e}")
            traceback.print_exc()

    def _get_current_context(self) -> Dict:
        """Get current context for thought generation"""
        try:
            if not self.world:
                return {}
            
            # Get current tile and chunk
            current_chunk = self.world.get_chunk_at(self.x, self.y)
            current_tile = self.world.get_tile_at(self.x, self.y)
            
            # Get nearby entities
            nearby_entities = self.world.get_entities_in_range(
                self.x, self.y, self.vision_range * TILE_SIZE
            )
            
            # Get current needs status
            needs_status = {
                'health': self.health,
                'energy': self.energy,
                'hunger': self.hunger,
                'thirst': self.thirst,
                'happiness': self.happiness,
                'stress': self.stress
            }
            
            # Get environmental factors
            env_factors = {
                'biome': current_tile.get('biome', 'unknown') if current_tile else 'unknown',
                'temperature': self.world.time_system.get('temperature', 20),
                'weather': self.world.time_system.get('weather', 'clear'),
                'time_of_day': self.world.time_system.get('day_progress', 0.0),
                'season': self.world.time_system.get('season', 'spring')
            }
            
            # Get social context
            social_context = {
                'nearby_humans': [e for e in nearby_entities if isinstance(e, Human)],
                'relationships': self.relationships,
                'recent_interactions': self.social['recent_interactions'][-5:],
                'reputation': self.social['reputation']
            }
            
            # Get inventory and resources context
            resource_context = {
                'inventory': self.inventory,
                'equipment': self.equipment,
                'known_resources': self.known_locations['resources'],
                'nearby_resources': [
                    r for r in current_tile.get('resources', [])
                    if r['type'] in RESOURCE_TYPES
                ] if current_tile else []
            }
            
            return {
                'entity': self,
                'needs': needs_status,
                'environment': env_factors,
                'social': social_context,
                'resources': resource_context,
                'personality': self.personality,
                'current_state': self.state,
                'memory': self.memory[-10:],  # Last 10 memories
                'skills': self.skills
            }
            
        except Exception as e:
            print(f"Error getting context for {self.name}: {e}")
            traceback.print_exc()
            return {}

    def _thought_to_action(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Convert a thought into an actionable task"""
        try:
            if not thought or 'type' not in thought:
                return None
            
            action = None
            
            # Handle different thought types
            if thought['type'] == 'need':
                action = self._handle_need_thought(thought, context)
            elif thought['type'] == 'social':
                action = self._handle_social_thought(thought, context)
            elif thought['type'] == 'explore':
                action = self._handle_explore_thought(thought, context)
            elif thought['type'] == 'work':
                action = self._handle_work_thought(thought, context)
            elif thought['type'] == 'rest':
                action = self._handle_rest_thought(thought, context)
            
            if action:
                action.update({
                    'priority': thought.get('priority', 1.0),
                    'source_thought': thought,
                    'context': context
                })
            
            return action
            
        except Exception as e:
            print(f"Error converting thought to action for {self.name}: {e}")
            traceback.print_exc()
            return None

    def _handle_need_thought(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Handle thoughts related to basic needs"""
        try:
            need_type = thought.get('need')
            if not need_type:
                return None
            
            if need_type == 'hunger':
                # Find food source
                food_sources = self._find_resources(['fruit', 'berry', 'mushroom'])
                if food_sources:
                    return {
                        'type': 'gather',
                        'target': food_sources[0],
                        'reason': 'hungry'
                    }
                
            elif need_type == 'thirst':
                # Find water source
                water_tiles = self._find_water_source()
                if water_tiles:
                    return {
                        'type': 'move',
                        'target': water_tiles[0],
                        'reason': 'thirsty',
                        'next_action': {
                            'type': 'drink',
                            'duration': 5
                        }
                    }
                
            elif need_type == 'rest':
                # Find safe place to rest
                rest_spot = self._find_rest_spot()
                if rest_spot:
                    return {
                        'type': 'move',
                        'target': rest_spot,
                        'reason': 'tired',
                        'next_action': {
                            'type': 'rest',
                            'duration': 30
                        }
                    }
                
            return None
            
        except Exception as e:
            print(f"Error handling need thought for {self.name}: {e}")
            traceback.print_exc()
            return None

    def _handle_social_thought(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Handle thoughts related to social interaction"""
        try:
            social_type = thought.get('social_type')
            if not social_type:
                return None
            
            nearby_humans = context['social']['nearby_humans']
            
            if social_type == 'chat':
                # Find someone to talk to
                potential_friends = [
                    h for h in nearby_humans
                    if h.id in self.relationships and
                    self.relationships[h.id]['value'] > 0
                ]
                
                if potential_friends:
                    target = random.choice(potential_friends)
                    return {
                        'type': 'interact',
                        'target': target,
                        'interaction': 'chat',
                        'duration': random.uniform(5, 15)
                    }
                
            elif social_type == 'help':
                # Find someone who needs help
                for human in nearby_humans:
                    if human.needs_help():
                        return {
                            'type': 'interact',
                            'target': human,
                            'interaction': 'help',
                            'duration': random.uniform(10, 20)
                        }
                
            return None
            
        except Exception as e:
            print(f"Error handling social thought for {self.name}: {e}")
            traceback.print_exc()
            return None

    def _handle_explore_thought(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Handle thoughts related to exploration"""
        try:
            explore_type = thought.get('explore_type')
            if not explore_type:
                return None
            
            if explore_type == 'new_area':
                # Find unexplored area
                target = self._find_unexplored_area()
                if target:
                    return {
                        'type': 'move',
                        'target': target,
                        'reason': 'explore',
                        'next_action': {
                            'type': 'explore',
                            'duration': random.uniform(10, 30)
                        }
                    }
                
            elif explore_type == 'resource':
                # Find new resources
                resource_types = thought.get('resource_types', ['wood', 'stone', 'herb'])
                target = self._find_resources(resource_types)
                if target:
                    return {
                        'type': 'move',
                        'target': target,
                        'reason': 'gather_resource',
                        'next_action': {
                            'type': 'gather',
                            'resource_type': target['type']
                        }
                    }
                
            return None
            
        except Exception as e:
            print(f"Error handling explore thought for {self.name}: {e}")
            traceback.print_exc()
            return None

    def _handle_work_thought(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Handle thoughts related to work and tasks"""
        try:
            work_type = thought.get('work_type')
            if not work_type:
                return None
            
            if work_type == 'gather':
                # Find resources to gather
                resources = self._find_resources(thought.get('resource_types', ['wood', 'stone']))
                if resources:
                    return {
                        'type': 'gather',
                        'target': resources[0],
                        'reason': 'work'
                    }
                
            elif work_type == 'craft':
                # Check if we have materials to craft
                recipe = thought.get('recipe')
                if recipe and self._can_craft(recipe):
                    return {
                        'type': 'craft',
                        'recipe': recipe,
                        'duration': random.uniform(10, 30)
                    }
                
            return None
            
        except Exception as e:
            print(f"Error handling work thought for {self.name}: {e}")
            traceback.print_exc()
            return None

    def _handle_rest_thought(self, thought: Dict, context: Dict) -> Optional[Dict]:
        """Handle thoughts related to resting and recovery"""
        try:
            rest_type = thought.get('rest_type')
            if not rest_type:
                return None
            
            if rest_type == 'sleep':
                # Find safe place to sleep
                bed = self._find_bed()
                if bed:
                    return {
                        'type': 'move',
                        'target': bed,
                        'reason': 'sleep',
                        'next_action': {
                            'type': 'sleep',
                            'duration': random.uniform(240, 480)
                        }
                    }
                else:
                    # Sleep where we are if safe
                    if self._is_location_safe(self.x, self.y):
                        return {
                            'type': 'sleep',
                            'duration': random.uniform(240, 480)
                        }
                
            elif rest_type == 'break':
                # Take a short break
                if self._is_location_safe(self.x, self.y):
                    return {
                        'type': 'rest',
                        'duration': random.uniform(10, 30)
                    }
                
            return None
            
        except Exception as e:
            print(f"Error handling rest thought for {self.name}: {e}")
            traceback.print_exc()
            return None

    def cleanup(self):
        """Clean up human resources"""
        try:
            # Clean up systems
            for system in self.systems.values():
                if hasattr(system, 'cleanup'):
                    system.cleanup()
            self.systems.clear()
            
            super().cleanup()
            
        except Exception as e:
            print(f"Error cleaning up human: {e}")
            traceback.print_exc() 