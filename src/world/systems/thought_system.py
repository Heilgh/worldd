import random
import time
import pygame
import traceback
from typing import Dict, List, Optional
from collections import defaultdict
from ...constants import (MOODS, PERSONALITY_TRAITS, THOUGHT_INTERVAL,
                        THOUGHT_COMPLEXITY_LEVELS, INTERACTION_TYPES, UI_COLORS, THOUGHT_TYPES,
                        TILE_SIZE, ENTITY_STATES, ENTITY_NEEDS, ENTITY_TYPES, RESOURCE_TYPES, WEATHER_TYPES, TIME_SPEEDS,
                        THOUGHT_CATEGORIES)

class ThoughtSystem:
    def __init__(self, entity):
        """Initialize thought system for an entity"""
        self.entity = entity
        self.thoughts = []
        self.thought_history = []
        self.max_history = 10
        self.current_mood = 'content'
        self.emotion_state = 'neutral'
        self.thought_timer = 0
        self.thought_interval = 2.0  # Generate new thought every 2 seconds
        self.max_thoughts = 10
        
        # Personality and emotional state
        self.personality = {}
        self.emotions = {}
        self.goals = []
        self.relationships = {}
        self.memories = {}
        
        # Visual effects
        self.thought_alpha = 0
        self.target_alpha = 255
        self.fade_speed = 300  # Alpha per second
        self.glow_intensity = 0
        self.glow_direction = 1
        
        # Initialize subsystems
        self._initialize_personality()
        self._initialize_emotions()
        self._initialize_goals()
        
    def _initialize_personality(self):
        """Initialize personality traits"""
        self.personality = {
            'openness': random.uniform(0.3, 0.7),
            'conscientiousness': random.uniform(0.3, 0.7),
            'extraversion': random.uniform(0.3, 0.7),
            'agreeableness': random.uniform(0.3, 0.7),
            'neuroticism': random.uniform(0.3, 0.7)
        }
        
    def _initialize_emotions(self):
        """Initialize emotional state"""
        self.emotions = {
            'happiness': 0.5,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'surprise': 0.0
        }
        
    def _initialize_goals(self):
        """Initialize goals and desires"""
        self.goals = [
            {'type': 'survival', 'priority': 1.0, 'progress': 0.0},
            {'type': 'social', 'priority': 0.8, 'progress': 0.0},
            {'type': 'achievement', 'priority': 0.6, 'progress': 0.0},
            {'type': 'exploration', 'priority': 0.4, 'progress': 0.0},
            {'type': 'learning', 'priority': 0.5, 'progress': 0.0}
        ]
        
    def initialize(self, world):
        """Initialize thought system with world reference"""
        try:
            self.world = world
            # Initialize subsystems
            self._initialize_personality()
            self._initialize_emotions()
            self._initialize_goals()
            print("Thought system initialized successfully")
        except Exception as e:
            print(f"Error initializing thought system: {e}")
            traceback.print_exc()
        
    def update(self, dt: float):
        """Update thought system"""
        try:
            # Update thought timer
            self.thought_timer += dt
            if self.thought_timer >= self.thought_interval:
                self.thought_timer = 0
                self._generate_thought()
                
            # Update mood based on needs and environment
            self._update_mood()
            
            # Update emotions
            self._update_emotions(dt)
            
            # Update goals
            self._update_goals(dt)
            
            # Process memories
            self._process_memories(dt)
            
            # Update relationships
            self._update_relationships(dt)
            
            # Update visual effects
            if self.thought_alpha < self.target_alpha:
                self.thought_alpha = min(self.target_alpha, 
                                      self.thought_alpha + self.fade_speed * dt)
            
            # Update glow effect
            self.glow_intensity += self.glow_direction * dt
            if self.glow_intensity > 1:
                self.glow_intensity = 1
                self.glow_direction = -1
            elif self.glow_intensity < 0:
                self.glow_intensity = 0
                self.glow_direction = 1
                
            # Clean up old thoughts
            self.thoughts = [t for t in self.thoughts if t['timer'] > 0]
            for thought in self.thoughts:
                thought['timer'] -= dt
                
        except Exception as e:
            print(f"Error updating thought system: {e}")
            traceback.print_exc()
            
    def generate_thought(self, context: Dict) -> Optional[Dict]:
        """Generate a thought based on context"""
        try:
            thought_type = context.get('type', 'random')
            
            if thought_type == 'need':
                return self._generate_need_thought()
            elif thought_type == 'social':
                return self._generate_social_thought()
            elif thought_type == 'selected':
                return self._generate_selected_thought(context)
            else:
                return self._generate_random_thought()
                
        except Exception as e:
            print(f"Error generating thought: {e}")
            traceback.print_exc()
            return None
            
    def _generate_need_thought(self) -> Dict:
        """Generate thought based on entity needs"""
        try:
            # Find most pressing need
            critical_needs = []
            for need, value in self.entity.needs.items():
                if need in ENTITY_NEEDS:
                    threshold = ENTITY_NEEDS[need]['critical_threshold']
                    if value <= threshold:
                        critical_needs.append(need)
                        
            if critical_needs:
                need = random.choice(critical_needs)
                thoughts = {
                    'hunger': ["I'm so hungry...", "Need food soon!", "Must find something to eat"],
                    'thirst': ["So thirsty...", "Need water!", "Must find water"],
                    'energy': ["I'm exhausted...", "Need rest...", "Should take a break"],
                    'social': ["Feeling lonely...", "Need company", "Should talk to someone"]
                }
                return {
                    'text': random.choice(thoughts.get(need, ["I need something..."])),
                    'type': 'need',
                    'priority': 3,
                    'timer': 5.0
                }
                
            return self._generate_random_thought()
            
        except Exception as e:
            print(f"Error generating need thought: {e}")
            traceback.print_exc()
            return self._generate_random_thought()
            
    def _generate_social_thought(self) -> Dict:
        """Generate thought about social interaction"""
        social_thoughts = [
            "Wonder what others are doing?",
            "Would be nice to chat with someone",
            "Should meet new people",
            "Hope to make friends today",
            "Looking for interesting conversations"
        ]
        return {
            'text': random.choice(social_thoughts),
            'type': 'social',
            'priority': 2,
            'timer': 8.0
        }
        
    def _generate_selected_thought(self, context: Dict) -> Dict:
        """Generate thought when entity is selected"""
        selected_thoughts = [
            "Oh, hello there!",
            "Nice to meet you!",
            "Can I help you?",
            "What a pleasant surprise!",
            "Always happy to interact!"
        ]
        return {
            'text': random.choice(selected_thoughts),
            'type': 'social',
            'priority': 2,
            'timer': 5.0
        }
        
    def _generate_random_thought(self):
        """Generate a random thought based on current state"""
        try:
            if not self.entity:
                return None
                
            # Check needs
            needs = getattr(self.entity, 'needs', {})
            if needs and any(v <= 50 for v in needs.values()):
                # Generate need-based thought
                low_needs = [need for need, value in needs.items() if value <= 50]
                need = random.choice(low_needs)
                return {
                    'type': 'need',
                    'text': f"I need {need}...",
                    'emotion': 'concern',
                    'urgency': max(0, 50 - needs[need]) / 50,
                    'significance': 0.7
                }
                
            # Random thought types
            thought_types = [
                self._generate_observation_thought,
                self._generate_goal_thought,
                self._generate_emotional_thought,
                self._generate_memory_thought
            ]
            
            # Generate random thought
            thought_generator = random.choice(thought_types)
            return thought_generator()
            
        except Exception as e:
            print(f"Error generating random thought: {e}")
            traceback.print_exc()
            return None
            
    def _update_mood(self):
        """Update entity's mood based on needs and environment"""
        try:
            # Calculate overall well-being
            need_values = list(self.entity.needs.values())
            avg_needs = sum(need_values) / len(need_values)
            
            # Determine mood based on needs
            if avg_needs >= 80:
                self.current_mood = 'joyful'
            elif avg_needs >= 60:
                self.current_mood = 'content'
            elif avg_needs >= 40:
                self.current_mood = 'neutral'
            elif avg_needs >= 20:
                self.current_mood = 'sad'
            else:
                self.current_mood = 'tired'
                
            # Update emotion state
            if 'energy' in self.entity.needs and self.entity.needs['energy'] < 30:
                self.emotion_state = 'tired'
            elif avg_needs < 30:
                self.emotion_state = 'sad'
            elif avg_needs > 80:
                self.emotion_state = 'happy'
            else:
                self.emotion_state = 'neutral'
                
        except Exception as e:
            print(f"Error updating mood: {e}")
            traceback.print_exc()
            
    def _update_emotions(self, dt: float):
        """Update emotional state based on context"""
        try:
            # Update based on needs
            if hasattr(self.entity, 'needs'):
                for need, value in self.entity.needs.items():
                    if value < 30:  # Critical need
                        self.emotions['happiness'] = max(0, self.emotions['happiness'] - 0.1 * dt)
                        self.emotions['anger'] = min(1, self.emotions['anger'] + 0.05 * dt)
                        self.emotions['fear'] = min(1, self.emotions['fear'] + 0.05 * dt)
                    elif value > 80:  # Well satisfied need
                        self.emotions['happiness'] = min(1, self.emotions['happiness'] + 0.05 * dt)
                        self.emotions['contentment'] = min(1, self.emotions['contentment'] + 0.05 * dt)
                        
            # Decay emotions over time
            for emotion in self.emotions:
                if emotion != 'happiness':  # Happiness decays slower
                    self.emotions[emotion] = max(0, self.emotions[emotion] - 0.02 * dt)
                    
        except Exception as e:
            print(f"Error updating emotions: {e}")
            traceback.print_exc()
            
    def _update_goals(self, dt: float):
        """Update goals and their priorities"""
        try:
            for goal in self.goals:
                # Update priority based on personality and needs
                if goal['type'] == 'survival':
                    if any(v < 30 for v in self.entity.needs.values()):
                        goal['priority'] = 1.0
                    else:
                        goal['priority'] = 0.6
                elif goal['type'] == 'social':
                    goal['priority'] = 0.4 + self.personality['extraversion'] * 0.4
                elif goal['type'] == 'exploration':
                    goal['priority'] = 0.3 + self.personality['curiosity'] * 0.4
                    
                # Decay progress over time
                goal['progress'] = max(0, goal['progress'] - 0.1 * dt)
                
        except Exception as e:
            print(f"Error updating goals: {e}")
            traceback.print_exc()
            
    def _process_memories(self, dt: float):
        """Process and update memories"""
        try:
            # Remove old memories
            current_time = time.time()
            self.memories = {entity_id: [m for m in memories if current_time - m['time'] < m['duration']] for entity_id, memories in self.memories.items()}
            
            # Process memory effects
            for entity_id, memories in self.memories.items():
                for memory in memories:
                    if memory['type'] == 'emotional':
                        intensity = memory['intensity'] * (1 - (current_time - memory['time']) / memory['duration'])
                        self.emotions[memory['emotion']] = min(1, self.emotions[memory['emotion']] + intensity * dt)
                        
        except Exception as e:
            print(f"Error processing memories: {e}")
            traceback.print_exc()
            
    def _update_relationships(self, dt: float):
        """Update relationships with other entities"""
        try:
            current_time = time.time()
            for entity_id, relationship in self.relationships.items():
                # Decay relationship value over time
                if 'last_interaction' in relationship:
                    time_since_interaction = current_time - relationship['last_interaction']
                    if time_since_interaction > 300:  # 5 minutes
                        relationship['value'] = max(0, relationship['value'] - 0.1 * dt)
                        
                # Update relationship type based on value
                if relationship['value'] > 0.8:
                    relationship['type'] = 'friend'
                elif relationship['value'] > 0.5:
                    relationship['type'] = 'acquaintance'
                else:
                    relationship['type'] = 'stranger'
                    
        except Exception as e:
            print(f"Error updating relationships: {e}")
            traceback.print_exc()
            
    def _generate_thought(self):
        """Generate a new thought based on current state"""
        try:
            # Get possible thought categories
            categories = []
            
            # Add need-based categories
            if hasattr(self.entity, 'needs'):
                for need, value in self.entity.needs.items():
                    if value < 30:
                        categories.extend(['needs'] * 3)  # Higher priority
                    elif value < 50:
                        categories.append('needs')
                        
            # Add emotion-based categories
            for emotion, value in self.emotions.items():
                if value > 0.7:
                    categories.append('emotional')
                    
            # Add goal-based categories
            for goal in sorted(self.goals, key=lambda g: g['priority'], reverse=True):
                if goal['priority'] > 0.7:
                    categories.extend([goal['type']] * 2)
                elif goal['priority'] > 0.4:
                    categories.append(goal['type'])
                    
            # Add personality-influenced categories
            if self.personality['curiosity'] > 0.6:
                categories.append('exploration')
            if self.personality['extraversion'] > 0.6:
                categories.append('social')
                
            # Select category and generate thought
            if categories:
                category = random.choice(categories)
                thought = self._generate_specific_thought(category)
                if thought:
                    self.thoughts.append(thought)
                    self.thought_history.append(thought)
                    if len(self.thought_history) > self.max_history:
                        self.thought_history.pop(0)
                    return thought
                    
        except Exception as e:
            print(f"Error generating thought: {e}")
            traceback.print_exc()
            return None
            
    def _generate_specific_thought(self, category: str) -> Optional[Dict]:
        """Generate a specific type of thought"""
        try:
            if category == 'needs':
                return self._generate_need_thought()
            elif category == 'emotional':
                return self._generate_emotional_thought()
            elif category == 'social':
                return self._generate_social_thought()
            elif category == 'exploration':
                return self._generate_explore_thought()
            elif category == 'survival':
                return self._generate_survival_thought()
            else:
                return self._generate_random_thought()
                
        except Exception as e:
            print(f"Error generating specific thought: {e}")
            traceback.print_exc()
            return None
            
    def draw(self, screen, camera):
        """Draw thought bubble and effects"""
        try:
            if not self.thoughts:
                return
                
            # Calculate screen position
            x = self.entity.x - camera['x']
            y = self.entity.y - camera['y']
            
            # Draw thought bubble
            thought = self.thoughts[-1]
            text = thought.get('text', '')
            emotion = thought.get('emotion', 'neutral')
            
            # Create thought bubble surface
            bubble_surface = pygame.Surface((200, 100), pygame.SRCALPHA)
            
            # Draw glow effect
            glow_color = (*UI_COLORS['thought_glow'][:3], int(50 * self.glow_intensity))
            pygame.draw.ellipse(bubble_surface, glow_color, bubble_surface.get_rect().inflate(20, 20))
            
            # Draw bubble background
            bg_color = UI_COLORS['thought_bubble_bg']
            pygame.draw.ellipse(bubble_surface, bg_color, bubble_surface.get_rect())
            
            # Draw border with emotional color
            emotion_color = UI_COLORS.get(f'emotion_{emotion}', UI_COLORS['thought_bubble_border'])
            pygame.draw.ellipse(bubble_surface, emotion_color, bubble_surface.get_rect(), 2)
            
            # Draw text
            font = pygame.font.Font(None, 20)
            words = text.split()
            lines = []
            current_line = words[0] if words else ""
            
            for word in words[1:]:
                test_line = current_line + " " + word
                if font.size(test_line)[0] <= 180:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            
            # Draw text with emotional color
            y_offset = 20
            for line in lines:
                text_surface = font.render(line, True, UI_COLORS['thought_bubble_text'])
                text_rect = text_surface.get_rect(centerx=100, top=y_offset)
                bubble_surface.blit(text_surface, text_rect)
                y_offset += text_surface.get_height() + 5
                
            # Draw connecting circles with emotional color
            circle_positions = [(20, 80), (15, 70), (10, 60)]
            for pos in circle_positions:
                pygame.draw.circle(bubble_surface, bg_color, pos, 5)
                pygame.draw.circle(bubble_surface, emotion_color, pos, 5, 1)
                
            # Draw emoji if present
            if 'emoji' in thought:
                emoji_font = pygame.font.SysFont('segoe ui emoji', 24)
                emoji_surface = emoji_font.render(thought['emoji'], True, UI_COLORS['thought_bubble_text'])
                emoji_rect = emoji_surface.get_rect(right=180, bottom=80)
                bubble_surface.blit(emoji_surface, emoji_rect)
            
            # Apply fade effect
            if self.thought_alpha < 255:
                bubble_surface.set_alpha(self.thought_alpha)
            
            # Draw final surface
            screen.blit(bubble_surface, (x - 100, y - 120))
            
        except Exception as e:
            print(f"Error drawing thought bubble: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up thought system resources"""
        try:
            self.thoughts.clear()
            self.thought_history.clear()
            self.memories.clear()
            self.relationships.clear()
            self.entity = None
        except Exception as e:
            print(f"Error cleaning up thought system: {e}")
            traceback.print_exc()

    def get_current_thought(self):
        """Get the current thought if it exists"""
        return self.thoughts[-1] if self.thoughts else None
        
    def get_thought_history(self):
        """Get the thought history"""
        return self.thought_history
        
    def get_emotional_state(self):
        """Get the current emotional state"""
        return self.emotions
        
    def get_personality(self):
        """Get the personality traits"""
        return self.personality
        
    def get_goals(self):
        """Get the current goals"""
        return self.goals

    def process(self, context: Dict) -> Optional[Dict]:
        """Process thoughts and generate actions"""
        try:
            # Generate new thought based on context
            thought = self.generate_thought(context)
            
            if not thought:
                return None
                
            # Update emotional state based on thought
            self._update_emotions(0.1)  # Small time step for emotion updates
            
            # Update goals based on thought
            self._update_goals(0.1)
            
            # Process memories
            self._process_memories(0.1)
            
            # Update relationships based on thought
            self._update_relationships(0.1)
            
            # Store thought in history
            if len(self.thought_history) >= 10:
                self.thought_history.pop(0)
            self.thought_history.append(thought)
            
            # Set as current thought
            self.current_thought = thought.get('text', '')
            
            return thought
            
        except Exception as e:
            print(f"Error processing thought: {e}")
            traceback.print_exc()
            return None

    def add_thought(self, entity_id: int, thought: Dict):
        """Add a new thought to the system"""
        try:
            if not thought:
                return
                
            # Add timestamp and entity ID
            thought['timestamp'] = time.time()
            thought['entity_id'] = entity_id
            
            # Add to thoughts list
            self.thoughts.append(thought)
            
            # Keep only last 10 thoughts
            if len(self.thoughts) > 10:
                self.thoughts.pop(0)
                
            # Update current thought
            self.current_thought = thought
            
            # Add to history
            self.thought_history.append(thought)
            if len(self.thought_history) > 100:
                self.thought_history.pop(0)
                
            # Process emotional impact
            self._process_emotional_impact(thought)
            
            # Update goals based on thought
            self._update_goals_from_thought(thought)
            
            # Create memory if significant
            if thought.get('significance', 0) > 0.5:
                self._create_memory(thought)
                
        except Exception as e:
            print(f"Error adding thought: {e}")
            traceback.print_exc()
            
    def _generate_observation_thought(self) -> Dict:
        """Generate an observation thought"""
        # Implementation of _generate_observation_thought method
        pass

    def _generate_goal_thought(self) -> Dict:
        """Generate a goal thought"""
        # Implementation of _generate_goal_thought method
        pass

    def _generate_emotional_thought(self) -> Dict:
        """Generate an emotional thought"""
        # Implementation of _generate_emotional_thought method
        pass

    def _generate_memory_thought(self) -> Dict:
        """Generate a memory thought"""
        # Implementation of _generate_memory_thought method
        pass

    def _process_emotional_impact(self, thought: Dict):
        """Process the emotional impact of a thought"""
        # Implementation of _process_emotional_impact method
        pass

    def _update_goals_from_thought(self, thought: Dict):
        """Update goals based on a new thought"""
        # Implementation of _update_goals_from_thought method
        pass

    def _create_memory(self, thought: Dict):
        """Create a new memory based on a thought"""
        # Implementation of _create_memory method
        pass 