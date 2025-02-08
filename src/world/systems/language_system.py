import random
from collections import defaultdict
from typing import Dict, List, Optional

class LanguageSystem:
    def __init__(self):
        """Initialize language system"""
        self.world = None
        self.vocabulary = {
            'needs': ['hungry', 'thirsty', 'tired', 'lonely', 'uncomfortable'],
            'actions': ['eat', 'drink', 'rest', 'socialize', 'work', 'explore'],
            'emotions': ['happy', 'sad', 'angry', 'excited', 'worried', 'content'],
            'objects': ['food', 'water', 'bed', 'tool', 'resource', 'building'],
            'descriptors': ['good', 'bad', 'big', 'small', 'far', 'near'],
            'time': ['now', 'soon', 'later', 'morning', 'afternoon', 'night'],
            'weather': ['sunny', 'rainy', 'cloudy', 'stormy', 'cold', 'hot']
        }
        self.thought_templates = [
            "I feel {emotion}",
            "I need to {action}",
            "I should find {object}",
            "The weather is {weather}",
            "It's {time} now",
            "I am {need}",
            "{object} is {descriptor}"
        ]
        
    def initialize(self, world):
        """Initialize language system with world reference"""
        self.world = world
        
    def generate_thought(self, context: Dict) -> str:
        """Generate a thought based on context"""
        try:
            template = random.choice(self.thought_templates)
            
            # Fill in template based on context
            thought = template
            if '{emotion}' in thought:
                thought = thought.replace('{emotion}', self._get_emotion(context))
            if '{action}' in thought:
                thought = thought.replace('{action}', self._get_action(context))
            if '{object}' in thought:
                thought = thought.replace('{object}', self._get_object(context))
            if '{weather}' in thought:
                thought = thought.replace('{weather}', self._get_weather(context))
            if '{time}' in thought:
                thought = thought.replace('{time}', self._get_time(context))
            if '{need}' in thought:
                thought = thought.replace('{need}', self._get_need(context))
            if '{descriptor}' in thought:
                thought = thought.replace('{descriptor}', random.choice(self.vocabulary['descriptors']))
                
            return thought
            
        except Exception as e:
            print(f"Error generating thought: {e}")
            return "..."
            
    def _get_emotion(self, context: Dict) -> str:
        """Get appropriate emotion based on context"""
        if 'needs' in context:
            # Check critical needs
            for need, value in context['needs'].items():
                if value < 30:
                    return 'worried'
                elif value < 50:
                    return 'sad'
            return 'content'
        return random.choice(self.vocabulary['emotions'])
        
    def _get_action(self, context: Dict) -> str:
        """Get appropriate action based on context"""
        if 'needs' in context:
            # Check needs and return relevant action
            if context['needs'].get('hunger', 0) > 60:
                return 'eat'
            elif context['needs'].get('thirst', 0) > 60:
                return 'drink'
            elif context['needs'].get('energy', 0) < 40:
                return 'rest'
            elif context['needs'].get('social', 0) < 40:
                return 'socialize'
        return random.choice(self.vocabulary['actions'])
        
    def _get_object(self, context: Dict) -> str:
        """Get appropriate object based on context"""
        if 'needs' in context:
            # Return object based on most pressing need
            if context['needs'].get('hunger', 0) > 60:
                return 'food'
            elif context['needs'].get('thirst', 0) > 60:
                return 'water'
            elif context['needs'].get('energy', 0) < 40:
                return 'bed'
        return random.choice(self.vocabulary['objects'])
        
    def _get_weather(self, context: Dict) -> str:
        """Get weather description"""
        if 'weather' in context:
            return context['weather']
        return random.choice(self.vocabulary['weather'])
        
    def _get_time(self, context: Dict) -> str:
        """Get time description"""
        if 'time' in context:
            hour = context['time'].get('hour', 0)
            if 5 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 18:
                return 'afternoon'
            else:
                return 'night'
        return random.choice(self.vocabulary['time'])
        
    def _get_need(self, context: Dict) -> str:
        """Get most pressing need"""
        if 'needs' in context:
            max_need = max(context['needs'].items(), key=lambda x: x[1])
            if max_need[0] == 'hunger' and max_need[1] > 50:
                return 'hungry'
            elif max_need[0] == 'thirst' and max_need[1] > 50:
                return 'thirsty'
            elif max_need[0] == 'energy' and max_need[1] < 40:
                return 'tired'
            elif max_need[0] == 'social' and max_need[1] < 40:
                return 'lonely'
        return random.choice(self.vocabulary['needs'])
        
    def update(self, world, dt):
        """Update language system"""
        if not self.world:
            self.initialize(world)
            
        # Update conversations and language processing here
        pass
        
    def _initialize_vocabulary(self):
        """Initialize basic vocabulary with generated words"""
        # Add words for each category
        for category, words in self.word_categories.items():
            for word in words:
                self.vocabulary[word] = self._generate_word()
                
    def generate_word(self, meaning: str, category: Optional[str] = None) -> str:
        """Generate a new word based on meaning and category"""
        if meaning in self.evolved_words:
            return self.evolved_words[meaning]
            
        # Create word pattern based on category
        if category == 'actions':
            pattern = 'CVCV'  # Action words are typically two syllables
        elif category == 'objects':
            pattern = 'CVC'   # Object words are typically one syllable
        elif category == 'qualities':
            pattern = 'VCV'   # Quality words often start with a vowel
        elif category == 'emotions':
            pattern = 'CVCCV' # Emotion words are more complex
        else:
            pattern = random.choice(self.word_patterns)
            
        word = self._generate_word(pattern)
        self.evolved_words[meaning] = word
        return word
        
    def _generate_word(self, pattern: Optional[str] = None) -> str:
        """Generate a random word using phoneme patterns"""
        if pattern is None:
            pattern = random.choice(self.word_patterns)
            
        word = ''
        for char in pattern:
            if char == 'C':
                word += random.choice(self.phonemes['consonants'])
            elif char == 'V':
                word += random.choice(self.phonemes['vowels'])
            elif char == 'E':
                word += random.choice(self.phonemes['endings'])
                
        return word
        
    def _generate_affix(self) -> str:
        """Generate a short affix for grammatical markers"""
        pattern = random.choice(['CV', 'VC'])
        return self._generate_word(pattern)
        
    def learn_word(self, human1, human2, context: Dict):
        """Humans learn words from each other based on context"""
        if not hasattr(human1, 'known_words'):
            human1.known_words = {}
        if not hasattr(human2, 'known_words'):
            human2.known_words = {}
            
        # Generate or share words based on context
        relevant_words = self._get_relevant_words(context)
        for meaning in relevant_words:
            if meaning in human2.known_words:
                # Learn word from other human
                human1.known_words[meaning] = human2.known_words[meaning]
            elif meaning in human1.known_words:
                # Teach word to other human
                human2.known_words[meaning] = human1.known_words[meaning]
            else:
                # Create new word together
                new_word = self.generate_word(meaning)
                human1.known_words[meaning] = new_word
                human2.known_words[meaning] = new_word
                
        # Update word associations based on context
        self._update_associations(relevant_words, context)
        
    def _get_relevant_words(self, context: Dict) -> List[str]:
        """Get relevant words based on context"""
        relevant_words = []
        
        # Add words based on activity
        if context.get('activity'):
            if context['activity'] in self.word_categories['actions']:
                relevant_words.append(context['activity'])
                
        # Add words based on location
        if context.get('location'):
            if context['location'] in self.word_categories['nature']:
                relevant_words.append(context['location'])
                
        # Add words based on emotion
        if context.get('emotion'):
            if context['emotion'] in self.word_categories['emotions']:
                relevant_words.append(context['emotion'])
                
        # Add words based on objects
        if context.get('objects'):
            for obj in context['objects']:
                if obj in self.word_categories['objects']:
                    relevant_words.append(obj)
                    
        return relevant_words
        
    def _update_associations(self, words: List[str], context: Dict):
        """Update word associations based on context"""
        for word1 in words:
            self.word_usage[word1] += 1
            for word2 in words:
                if word1 != word2:
                    self.word_associations[word1][word2] += 1
                    
    def generate_name(self, human, world) -> str:
        """Generate a name based on environment and traits"""
        if hasattr(human, 'name') and human.name:
            return human.name
            
        # Get environmental influences
        biome = human._get_current_biome(world)
        nearby = human._get_nearby_objects(world)
        
        # Get personality influences
        traits = []
        if human.personality['bravery'] > 0.7:
            traits.append('strong')
        if human.personality['wisdom'] > 0.7:
            traits.append('wise')
        if human.personality['agility'] > 0.7:
            traits.append('swift')
        if human.personality['kindness'] > 0.7:
            traits.append('kind')
            
        # Generate name components
        components = []
        
        # Add environment-based component
        if biome and biome in self.name_patterns['nature']:
            components.append(random.choice(self.name_patterns['nature'][biome]))
            
        # Add trait-based component
        if traits:
            trait = random.choice(traits)
            components.append(random.choice(self.name_patterns['qualities'][trait]))
            
        # If no components yet, use default
        if not components:
            components = [random.choice(sum(self.name_patterns['nature'].values(), []))]
            
        # Add suffix
        suffix = random.choice(self.name_patterns['suffixes'])
        
        # Combine components
        base_name = random.choice(components)
        name = base_name.capitalize() + suffix
        
        return name
        
    def translate(self, text: str, to_native: bool = True) -> str:
        """Translate between native language and common language"""
        words = text.lower().split()
        translated = []
        
        for word in words:
            if to_native:
                # Translate to native language
                if word in self.vocabulary:
                    translated.append(self.vocabulary[word])
                else:
                    # Generate a new word if not in vocabulary
                    self.vocabulary[word] = self._generate_word()
                    translated.append(self.vocabulary[word])
            else:
                # Translate from native to common
                for common, native in self.vocabulary.items():
                    if native == word:
                        translated.append(common)
                        break
                else:
                    translated.append(word)  # Keep untranslatable words as is
                    
        return ' '.join(translated)
        
    def generate_sentence(self, subject: str, verb: str, object: Optional[str] = None, tense: str = 'present') -> str:
        """Generate a grammatically correct sentence"""
        # Add tense marker
        verb_with_tense = self.grammar['tense_markers'][tense] + verb
        
        # Build sentence
        if object:
            return f"{subject} {verb_with_tense} {object}"
        return f"{subject} {verb_with_tense}"
        
    def get_greeting(self) -> str:
        """Generate a culturally appropriate greeting"""
        greetings = [
            self.translate("hello"),
            self.translate("good day"),
            self.translate("peace")
        ]
        return random.choice(greetings)

    def generate_dialogue(self, speaker, listener, context: Dict) -> str:
        """Generate dialogue between two entities"""
        try:
            # Get relationship between entities
            relationship = None
            if hasattr(speaker, 'social') and hasattr(listener, 'id'):
                relationship = speaker.social['relationships'].get(listener.id, {})
                
            # Get interaction type
            interaction_type = context.get('interaction_type', 'chat')
            
            # Get dialogue templates based on interaction type and relationship
            templates = self._get_dialogue_templates(interaction_type, relationship)
            if not templates:
                return "..."
                
            # Select template and fill in context
            template = random.choice(templates)
            dialogue = self._fill_template(template, context)
            
            return dialogue
            
        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return "..."

    def _get_dialogue_templates(self, interaction_type: str, relationship: Optional[Dict]) -> List[str]:
        """Get appropriate dialogue templates"""
        try:
            # Base templates for different interaction types
            templates = {
                'greet': [
                    "Hello {target_name}!",
                    "Hi there!",
                    "Good {time_of_day}!"
                ],
                'chat': [
                    "How are you doing?",
                    "Nice {weather} today, isn't it?",
                    "What have you been up to?"
                ],
                'help': [
                    "Do you need any help?",
                    "I can help you with that!",
                    "Let me give you a hand."
                ],
                'trade': [
                    "Would you like to trade?",
                    "I have some items to trade.",
                    "What do you have to offer?"
                ],
                'farewell': [
                    "Goodbye!",
                    "See you later!",
                    "Take care!"
                ]
            }
            
            # Add relationship-specific templates
            if relationship:
                relationship_value = relationship.get('value', 0)
                if relationship_value > 70:  # Friends
                    templates['greet'].extend([
                        "Great to see you, {target_name}!",
                        "I was hoping to run into you!"
                    ])
                    templates['chat'].extend([
                        "Tell me about your day!",
                        "I've been thinking about our last conversation."
                    ])
                elif relationship_value < 30:  # Unfriendly
                    templates['greet'].extend([
                        "Oh... it's you.",
                        "*nods briefly*"
                    ])
                    templates['chat'].extend([
                        "What do you want?",
                        "I'm quite busy..."
                    ])
                    
            return templates.get(interaction_type, ["..."])
            
        except Exception as e:
            print(f"Error getting dialogue templates: {e}")
            return ["..."]

    def _fill_template(self, template: str, context: Dict) -> str:
        """Fill in template with context"""
        try:
            filled = template
            
            # Replace target name
            if '{target_name}' in filled and 'target' in context:
                target = context['target']
                if hasattr(target, 'name'):
                    filled = filled.replace('{target_name}', target.name)
                    
            # Replace time of day
            if '{time_of_day}' in filled and 'time_system' in context:
                time = context['time_system'].get('day_progress', 0)
                time_of_day = 'morning' if time < 0.3 else 'afternoon' if time < 0.7 else 'evening'
                filled = filled.replace('{time_of_day}', time_of_day)
                
            # Replace weather
            if '{weather}' in filled and 'weather' in context:
                weather = context['weather']
                filled = filled.replace('{weather}', weather)
                
            return filled
            
        except Exception as e:
            print(f"Error filling template: {e}")
            return template

    def generate_response(self, speaker, listener, previous_dialogue: str, context: Dict) -> str:
        """Generate a response to previous dialogue"""
        try:
            # Get relationship between entities
            relationship = None
            if hasattr(speaker, 'social') and hasattr(listener, 'id'):
                relationship = speaker.social['relationships'].get(listener.id, {})
                
            # Analyze previous dialogue to determine response type
            if any(word in previous_dialogue.lower() for word in ['hello', 'hi', 'hey']):
                return self._generate_greeting_response(relationship)
            elif '?' in previous_dialogue:
                return self._generate_question_response(previous_dialogue, context)
            elif any(word in previous_dialogue.lower() for word in ['goodbye', 'bye', 'later']):
                return self._generate_farewell_response(relationship)
            else:
                return self._generate_general_response(previous_dialogue, context)
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return "..."

    def _generate_greeting_response(self, relationship: Optional[Dict]) -> str:
        """Generate response to greeting"""
        try:
            if relationship:
                value = relationship.get('value', 0)
                if value > 70:
                    return random.choice([
                        "Great to see you too!",
                        "I was just thinking about you!",
                        "What a pleasant surprise!"
                    ])
                elif value < 30:
                    return random.choice([
                        "Hmm.",
                        "*nods*",
                        "Yes?"
                    ])
                    
            return random.choice([
                "Hello!",
                "Hi there!",
                "Good to see you!"
            ])
            
        except Exception as e:
            print(f"Error generating greeting response: {e}")
            return "Hello."

    def _generate_question_response(self, question: str, context: Dict) -> str:
        """Generate response to question"""
        try:
            # Check for common questions
            question = question.lower()
            
            if any(word in question for word in ['how', 'are', 'you']):
                return self._generate_status_response(context)
            elif any(word in question for word in ['what', 'doing']):
                return self._generate_activity_response(context)
            elif any(word in question for word in ['weather', 'rain', 'sun']):
                return self._generate_weather_response(context)
            else:
                return random.choice([
                    "Hmm, let me think about that.",
                    "That's an interesting question.",
                    "I'm not quite sure."
                ])
                
        except Exception as e:
            print(f"Error generating question response: {e}")
            return "I'm not sure."

    def _generate_status_response(self, context: Dict) -> str:
        """Generate response about current status"""
        try:
            if 'needs' in context:
                # Check critical needs
                for need, value in context['needs'].items():
                    if value > 70:
                        return f"Not great, I'm really {need}..."
                    elif value > 50:
                        return f"I could use some help with my {need}."
                        
                return "I'm doing well, thanks for asking!"
                
            return random.choice([
                "I'm fine, thank you.",
                "Pretty good!",
                "Can't complain."
            ])
            
        except Exception as e:
            print(f"Error generating status response: {e}")
            return "I'm fine."

    def _generate_activity_response(self, context: Dict) -> str:
        """Generate response about current activity"""
        try:
            if 'current_action' in context:
                action = context['current_action']
                return f"I'm {action['type']}ing right now."
                
            return random.choice([
                "Just looking around.",
                "Taking a break.",
                "Nothing much."
            ])
            
        except Exception as e:
            print(f"Error generating activity response: {e}")
            return "Nothing much."

    def _generate_weather_response(self, context: Dict) -> str:
        """Generate response about weather"""
        try:
            if 'weather' in context:
                weather = context['weather']
                return f"Yes, it's quite {weather} today."
                
            return random.choice([
                "The weather's been interesting lately.",
                "It's a nice day.",
                "Could be better, could be worse."
            ])
            
        except Exception as e:
            print(f"Error generating weather response: {e}")
            return "It's a nice day."

    def _generate_farewell_response(self, relationship: Optional[Dict]) -> str:
        """Generate response to farewell"""
        try:
            if relationship:
                value = relationship.get('value', 0)
                if value > 70:
                    return random.choice([
                        "Take care, friend!",
                        "Looking forward to our next chat!",
                        "See you soon, I hope!"
                    ])
                elif value < 30:
                    return random.choice([
                        "Bye.",
                        "*waves briefly*",
                        "Finally..."
                    ])
                    
            return random.choice([
                "Goodbye!",
                "See you later!",
                "Take care!"
            ])
            
        except Exception as e:
            print(f"Error generating farewell response: {e}")
            return "Goodbye."

    def _generate_general_response(self, previous_dialogue: str, context: Dict) -> str:
        """Generate general response to statement"""
        try:
            # Check for emotional content
            emotions = {
                'positive': ['happy', 'great', 'good', 'wonderful', 'excited'],
                'negative': ['sad', 'bad', 'terrible', 'worried', 'angry']
            }
            
            for emotion_type, words in emotions.items():
                if any(word in previous_dialogue.lower() for word in words):
                    if emotion_type == 'positive':
                        return random.choice([
                            "That's great to hear!",
                            "I'm glad!",
                            "Wonderful!"
                        ])
                    else:
                        return random.choice([
                            "I'm sorry to hear that.",
                            "That must be difficult.",
                            "I hope things get better."
                        ])
                        
            return random.choice([
                "I see.",
                "Interesting.",
                "Tell me more.",
                "Mhm."
            ])
            
        except Exception as e:
            print(f"Error generating general response: {e}")
            return "I see." 