import pygame
import random
import math
import traceback
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Local imports
from .generation.world_generator import WorldGenerator
from .generation.terrain_generator import TerrainGenerator
from .entities.human import Human
from .entities.animal import Animal
from .entities.plant import Plant
from .chunk import Chunk
from ..constants import (
    WORLD_WIDTH, WORLD_HEIGHT, CHUNK_SIZE, TILE_SIZE,
    ENTITY_TYPES, WEATHER_TYPES, SEASONS, SEASON_ORDER,
    DAY_LENGTH, SEASON_LENGTH, TIME_SCALE,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BIOMES, UI_COLORS, TIME_SPEEDS,
    CAMERA_SETTINGS, RESOURCE_TYPES
)
from .systems.thought_system import ThoughtSystem
from .systems.weather_system import WeatherSystem
from .systems.language_system import LanguageSystem
from .systems.time_system import TimeSystem
from .entities.resource import Resource

class World:
    def __init__(self, width=WORLD_WIDTH, height=WORLD_HEIGHT):
        """Initialize the world"""
        try:
            # Core properties
            self.width = width
            self.height = height
            self.seed = random.randint(0, 999999)  # Initialize random seed
            self.entities = []
            self.active_entities = set()  # Changed from list to set
            self.chunks = {}
            self.active_chunks = {}  # Initialize active_chunks dictionary
            self.visible_chunks = set()
            self.needs_update = True
            self.initialized = False
            self.entity_id_counter = 0
            self.entity_types = {}
            self._pending_additions = []
            self._pending_removals = []
            self.selected_entity = None  # Initialize selected entity
            
            # Time and weather
            self.time_system = TimeSystem()
            self.current_season = 'spring'  # Initialize current season
            self.last_season_update = 0
            self.season_effects = {}
            
            # Camera and bounds
            self.camera = {
                'x': self.width / 2,
                'y': self.height / 2,
                'target_x': self.width / 2,
                'target_y': self.height / 2,
                'zoom': 1.0,
                'target_zoom': 1.0,
                'min_zoom': 0.5,
                'max_zoom': 4.0,
                'move_speed': 500,
                'zoom_speed': 2.0,
                'smooth_follow': True,  # Add smooth follow setting
                'follow_target': None,
                'shake_amount': 0,
                'shake_duration': 0,
                'viewport_width': WINDOW_WIDTH,
                'viewport_height': WINDOW_HEIGHT,
                'view_distance': 3,
                'bounds': {  # Add camera bounds
                    'min_x': 0,
                    'min_y': 0,
                    'max_x': self.width * TILE_SIZE,
                    'max_y': self.height * TILE_SIZE
                }
            }
            
            # Systems initialization
            self._init_systems()
            self._init_spatial_grid()
            self._init_render_surfaces()
            self._init_camera()
            
            print("World initialized successfully")
            
        except Exception as e:
            print(f"Error initializing world: {e}")
            traceback.print_exc()

    def _init_systems(self):
        """Initialize world systems"""
        try:
            print("Initializing world systems...")
            
            # Core systems
            self.systems = {
                'time': TimeSystem(),
                'weather': WeatherSystem(),
                'thought': ThoughtSystem(self),
                'language': LanguageSystem()
            }
            
            # Initialize each system
            for system_name, system in self.systems.items():
                if hasattr(system, 'initialize'):
                    system.initialize(self)
                print(f"Initialized {system_name} system")
                
            # Set up system references
            self.time_system = self.systems['time']
            self.weather_system = self.systems['weather']
            self.thought_system = self.systems['thought']
            self.language_system = self.systems['language']
            
            # Initialize spatial grid for entity tracking
            self._init_spatial_grid()
            
            # Initialize render surfaces
            self._init_render_surfaces()
            
            # Initialize camera
            self._init_camera()
            
            # Set initial season
            self.current_season = self.time_system.get_current_season()
            
            print("World systems initialized successfully")
            
        except Exception as e:
            print(f"Error initializing world systems: {e}")
            traceback.print_exc()

    def initialize_world(self, progress_callback=None):
        """Initialize the world"""
        try:
            print("Starting world initialization...")
            
            # Generate initial chunks around origin
            self._generate_initial_chunks(progress_callback)
            
            # Generate initial entities
            self._generate_initial_entities()
            
            # Update active chunks and entities
            self._update_active_chunks()
            self._update_active_entities()
            
            # Mark as initialized
            self.initialized = True
            print("World initialization complete")
            
        except Exception as e:
            print(f"Error initializing world: {e}")
            traceback.print_exc()
            
    def _generate_initial_chunks(self, progress_callback=None):
        """Generate initial chunks around origin"""
        try:
            print("Generating initial chunks...")
            
            # Generate chunks in a 5x5 area around origin
            total_chunks = 25
            chunks_generated = 0
            
            for x in range(-2, 3):
                for y in range(-2, 3):
                    chunk = self._generate_chunk(x, y)
                    if chunk:
                        self.chunks[(x, y)] = chunk
                        chunks_generated += 1
                        
                        # Update progress
                        if progress_callback:
                            progress = chunks_generated / total_chunks
                            progress_callback(progress, f"Generating chunk {chunks_generated}/{total_chunks}")
                            
            print(f"Generated {chunks_generated} initial chunks")
            
        except Exception as e:
            print(f"Error generating initial chunks: {e}")
            traceback.print_exc()

    def _generate_initial_entities(self):
        """Generate initial entities in the world"""
        try:
            print("Generating initial entities...")
            
            # Generate humans
            num_humans = 10
            for _ in range(num_humans):
                spawn_pos = self._find_valid_spawn_position(['plains', 'forest'])
                if spawn_pos:
                    human = Human(self, spawn_pos)
                    self.add_entity(human)
            
            # Generate animals
            num_animals = 20
            for _ in range(num_animals):
                spawn_pos = self._find_valid_spawn_position(['plains', 'forest', 'savanna'])
                if spawn_pos:
                    animal = Animal(self, spawn_pos)
                    self.add_entity(animal)
            
            # Generate plants
            num_plants = 50
            for _ in range(num_plants):
                spawn_pos = self._find_valid_spawn_position(['plains', 'forest', 'savanna'])
                if spawn_pos:
                    plant = Plant(self, spawn_pos)
                    self.add_entity(plant)
            
            print(f"Generated {len(self.entities)} initial entities")
            
        except Exception as e:
            print(f"Error generating initial entities: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up world resources"""
        try:
            print("Cleaning up...")
            
            # Clean up chunks
            for chunk in list(self.chunks.values()):
                if chunk:
                    chunk.cleanup()
            self.chunks.clear()
            self.active_chunks.clear()
            self.visible_chunks.clear()
            
            # Clean up entities
            for entity in self.entities:
                if entity:
                    entity.cleanup()
            self.entities.clear()
            self.active_entities.clear()
            self._pending_additions.clear()
            self._pending_removals.clear()
            
            # Clean up systems
            for system in self.systems.values():
                if system and hasattr(system, 'cleanup'):
                    system.cleanup()
            self.systems.clear()
            
            # Clear surfaces
            if hasattr(self, 'render_surface'):
                self.render_surface = None
            if hasattr(self, 'background_surface'):
                self.background_surface = None
                
            # Clear spatial grid
            if hasattr(self, 'spatial_grid'):
                for cell in self.spatial_grid.values():
                    cell.clear()
                self.spatial_grid.clear()
                
            # Clear other references
            self.generator = None
            self.camera = None
            self.ui_manager = None
            self.terrain_generator = None
            self.initialized = False
            
            # Force garbage collection
            import gc
            gc.collect()
            
            print("World cleanup complete")
            
        except Exception as e:
            print(f"Error during world cleanup: {e}")
            traceback.print_exc()

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except Exception as e:
            print(f"Error in world destructor: {e}")

    def update(self, dt: float, input_state: Optional[Dict] = None):
        """Update world state"""
        try:
            # Update time systems
            self._update_time(dt)
            self._update_weather(dt)
            self._update_season()
            
            # Update camera if input state is provided
            if input_state:
                self.update_camera(dt, input_state)
            
            # Update entities
            self._update_entities(dt)
            
            # Process thoughts and effects
            self._process_thoughts()
            self._apply_effects()
            
            # Update active chunks
            self._update_active_chunks()
            
        except Exception as e:
            print(f"Error updating world: {e}")
            traceback.print_exc()
            
    def _update_time(self, dt: float):
        """Update time system"""
        try:
            if not self.time_system:
                return
                
            # Update time system
            self.time_system.update(dt)
            
            # Update day/night cycle
            self.light_level = self.time_system.get_light_level()
            
            # Update season if needed
            self._update_season()
            
        except Exception as e:
            print(f"Error updating time: {e}")
            traceback.print_exc()
            
    def _update_season(self):
        """Update current season based on time system"""
        try:
            if not hasattr(self.time_system, 'get_current_season'):
                return
                
            current_season = self.time_system.get_current_season()
            if current_season != self.current_season:
                # Season has changed
                self.current_season = current_season
                print(f"Season changed to {self.current_season}")
                
                # Update season effects
                self.season_effects = SEASONS.get(self.current_season, {})
                
                # Notify entities of season change
                for entity in self.entities:
                    if hasattr(entity, '_handle_seasonal_effects'):
                        entity._handle_seasonal_effects(self, self.current_season)
                        
        except Exception as e:
            print(f"Error updating season: {e}")
            traceback.print_exc()
            
    def _update_weather(self, dt: float):
        """Update weather conditions"""
        try:
            if 'weather' not in self.systems or not self.systems['weather']:
                return
            
            # Update weather system
            self.systems['weather'].update(dt)
            
            # Get current weather data
            weather_data = self.systems['weather'].get_current_weather()
            
            # Update environmental conditions
            if weather_data:
                self.temperature = weather_data['temperature']
                self.humidity = weather_data['humidity']
                self.wind_speed = weather_data['wind_speed']
                self.wind_direction = weather_data['wind_direction']
                
                # Update visual effects
                self.darkness_level = weather_data.get('darkness', 0.0)
                
        except Exception as e:
            print(f"Error updating weather: {e}")
            traceback.print_exc()
            
    def _process_thoughts(self):
        """Process thoughts for all active entities"""
        try:
            for entity in self.active_entities:
                if hasattr(entity, 'thought_system') and entity.thought_system:
                    # Generate context for entity
                    context = self._generate_entity_context(entity)
                    
                    # Process thoughts
                    thought = entity.thought_system.process(context)
                    
                    if thought:
                        # Update entity's current thought
                        entity.current_thought = thought
                        entity.thought_timer = 3.0  # Display thought for 3 seconds
                        
                        # Process any actions from the thought
                        self._process_entity_action(entity, thought)
                        
        except Exception as e:
            print(f"Error processing thoughts: {e}")
            traceback.print_exc()
            
    def _generate_entity_context(self, entity):
        """Generate context information for entity thought processing"""
        try:
            context = {
                'time': {
                    'hour': self.time_system.hour,
                    'day': self.time_system.day,
                    'season': self.current_season,
                    'weather': self.weather_system.current_weather
                },
                'location': {
                    'x': entity.x,
                    'y': entity.y,
                    'chunk': (entity.x // CHUNK_SIZE, entity.y // CHUNK_SIZE)
                },
                'nearby_entities': self.get_entities_in_range(entity.x, entity.y, entity.vision_range),
                'current_tile': self.get_tile(entity.x, entity.y),
                'needs': entity.needs if hasattr(entity, 'needs') else {},
                'memories': entity.memories if hasattr(entity, 'memories') else [],
                'relationships': entity.relationships if hasattr(entity, 'relationships') else {},
                'personality': entity.personality if hasattr(entity, 'personality') else {}
            }
            
            return context
            
        except Exception as e:
            print(f"Error generating entity context: {e}")
            traceback.print_exc()
            return {}
            
    def _process_entity_action(self, entity, thought):
        """Process actions based on entity thoughts"""
        try:
            if not thought or 'action' not in thought:
                return
                
            action = thought['action']
            target = thought.get('target')
            
            if action == 'move':
                if target and isinstance(target, tuple):
                    target_x, target_y = target
                    dx = target_x - entity.x
                    dy = target_y - entity.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        entity.velocity_x = dx/dist * entity.speed
                        entity.velocity_y = dy/dist * entity.speed
                        
            elif action == 'interact':
                if target and hasattr(target, 'interact_with'):
                    target.interact_with(entity, self)
                    
            elif action == 'gather':
                if target and hasattr(target, 'gather'):
                    target.gather(entity)
                    
            elif action == 'rest':
                entity.state = 'resting'
                entity.velocity_x = 0
                entity.velocity_y = 0
                
            elif action == 'flee':
                if target:
                    dx = entity.x - target.x
                    dy = entity.y - target.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        entity.velocity_x = dx/dist * entity.speed * 1.5
                        entity.velocity_y = dy/dist * entity.speed * 1.5
                        
            # Add visual feedback for the action
            self._add_action_feedback(entity, action)
            
        except Exception as e:
            print(f"Error processing entity action: {e}")
            traceback.print_exc()
            
    def _add_action_feedback(self, entity, action):
        """Add visual feedback for entity actions"""
        try:
            if action == 'move':
                entity.add_visual_effect({
                    'type': 'particles',
                    'color': (200, 200, 200),
                    'duration': 0.5
                })
            elif action == 'interact':
                entity.add_visual_effect({
                    'type': 'glow',
                    'color': (255, 255, 150),
                    'duration': 0.3
                })
            elif action == 'gather':
                entity.add_visual_effect({
                    'type': 'sparkle',
                    'color': (150, 255, 150),
                    'duration': 0.5
                })
            elif action == 'rest':
                entity.add_visual_effect({
                    'type': 'zzz',
                    'color': (150, 150, 255),
                    'duration': 1.0
                })
            elif action == 'flee':
                entity.add_visual_effect({
                    'type': 'speed_lines',
                    'color': (255, 150, 150),
                    'duration': 0.5
                })
                
        except Exception as e:
            print(f"Error adding action feedback: {e}")
            traceback.print_exc()

    def _apply_effects(self):
        """Apply weather and time effects to entities"""
        try:
            if 'weather' not in self.systems or not self.systems['weather']:
                return
            
            # Get current weather effects
            weather_effects = self.systems['weather'].get_current_effects()
            
            # Apply effects to each entity
            for entity in self.entities:
                try:
                    # Check if entity is exposed to weather
                    if self._is_entity_exposed(entity):
                        # Apply weather effects
                        if hasattr(entity, 'apply_weather_effects'):
                            entity.apply_weather_effects(weather_effects)
                            
                        # Apply temperature effects
                        if hasattr(entity, 'apply_temperature_effects'):
                            entity.apply_temperature_effects(self.temperature)
                            
                except Exception as e:
                    print(f"Error applying effects to entity: {e}")
                    continue
                
        except Exception as e:
            print(f"Error applying effects: {e}")
            traceback.print_exc()
            
    def _is_entity_exposed(self, entity) -> bool:
        """Check if entity is exposed to weather"""
        try:
            # Get chunk and tile at entity position
            chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
            chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
            chunk = self.active_chunks.get((chunk_x, chunk_y))
            
            if chunk:
                local_x = int((entity.x % (CHUNK_SIZE * TILE_SIZE)) / TILE_SIZE)
                local_y = int((entity.y % (CHUNK_SIZE * TILE_SIZE)) / TILE_SIZE)
                tile = chunk.get_tile(local_x, local_y)
                
                if tile:
                    # Check if tile has shelter (trees, structures, etc.)
                    return not any(feature.get('provides_shelter', False) 
                                 for feature in tile.get('features', []))
                    
            return True
            
        except Exception as e:
            print(f"Error checking entity exposure: {e}")
            traceback.print_exc()
            return True
            
    def _update_entities(self, dt: float):
        """Update all active entities"""
        try:
            # Update active entities
            for entity in list(self.active_entities):
                if entity and hasattr(entity, 'update'):
                    try:
                        # Update entity
                        entity.update(self, dt)
                        
                        # Check if entity moved to a new chunk
                        new_chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
                        new_chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
                        new_chunk_pos = (new_chunk_x, new_chunk_y)
                        
                        old_chunk_x = int(entity.last_x / (CHUNK_SIZE * TILE_SIZE))
                        old_chunk_y = int(entity.last_y / (CHUNK_SIZE * TILE_SIZE))
                        old_chunk_pos = (old_chunk_x, old_chunk_y)
                        
                        if new_chunk_pos != old_chunk_pos:
                            # Remove from old chunk
                            old_chunk = self.chunks.get(old_chunk_pos)
                            if old_chunk:
                                old_chunk.remove_entity(entity)
                                
                            # Add to new chunk
                            new_chunk = self.chunks.get(new_chunk_pos)
                            if new_chunk:
                                new_chunk.add_entity(entity)
                                
                            # Update entity's last position
                            entity.last_x = entity.x
                            entity.last_y = entity.y
                            
                    except Exception as e:
                        print(f"Error updating entity {entity}: {e}")
                        continue
                        
            # Process any pending entity additions or removals
            self._process_entity_changes()
            
        except Exception as e:
            print(f"Error updating entities: {e}")
            traceback.print_exc()
            
    def _process_entity_changes(self):
        """Process pending entity additions and removals"""
        try:
            # Process additions
            while self._pending_additions:
                entity = self._pending_additions.pop()
                if entity:
                    chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
                    chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
                    chunk_pos = (chunk_x, chunk_y)
                    
                    # Add to appropriate chunk
                    chunk = self.chunks.get(chunk_pos)
                    if chunk:
                        chunk.add_entity(entity)
                        if chunk_pos in self.active_chunks:
                            self.active_entities.add(entity)
                            
            # Process removals
            while self._pending_removals:
                entity = self._pending_removals.pop()
                if entity:
                    # Remove from chunk
                    chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
                    chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
                    chunk = self.chunks.get((chunk_x, chunk_y))
                    if chunk:
                        chunk.remove_entity(entity)
                        
                    # Remove from active entities
                    self.active_entities.discard(entity)
                    
        except Exception as e:
            print(f"Error processing entity changes: {e}")
            traceback.print_exc()

    def _update_active_entities(self):
        """Update which entities are active based on camera position"""
        try:
            view_distance = 2000  # Increased view distance for entities
            camera_x = self.camera['x']
            camera_y = self.camera['y']
            
            # Calculate view bounds with padding
            min_x = camera_x - view_distance
            max_x = camera_x + view_distance
            min_y = camera_y - view_distance
            max_y = camera_y + view_distance
            
            active_count = 0
            for entity in self.entities:
                # Check if entity is within view bounds
                if hasattr(entity, 'x') and hasattr(entity, 'y'):
                    was_active = getattr(entity, 'active', False)
                    entity.active = (
                        min_x <= entity.x <= max_x and
                        min_y <= entity.y <= max_y
                    )
                    if entity.active:
                        active_count += 1
                        # Initialize entity if newly activated
                        if not was_active and hasattr(entity, 'initialize'):
                            entity.initialize()
                        
            print(f"Updated active entities: {active_count} entities in view")
            
        except Exception as e:
            print(f"Error updating active entities: {e}")
            traceback.print_exc()

    def _update_active_chunks(self):
        """Update which chunks are active based on camera position"""
        try:
            # Calculate chunk coordinates from camera position
            camera_chunk_x = int(self.camera['x'] / (CHUNK_SIZE * TILE_SIZE))
            camera_chunk_y = int(self.camera['y'] / (CHUNK_SIZE * TILE_SIZE))
            
            # Set view distance in chunks (increased)
            view_distance_x = 4
            view_distance_y = 3
            
            # Calculate visible chunk range
            min_chunk_x = camera_chunk_x - view_distance_x
            max_chunk_x = camera_chunk_x + view_distance_x
            min_chunk_y = camera_chunk_y - view_distance_y
            max_chunk_y = camera_chunk_y + view_distance_y
            
            print(f"Calculating visible chunks around ({camera_chunk_x}, {camera_chunk_y}) with view distance ({view_distance_x}, {view_distance_y})")
            
            # Track which chunks should be active
            visible_chunks = set()
            for x in range(min_chunk_x, max_chunk_x + 1):
                for y in range(min_chunk_y, max_chunk_y + 1):
                    chunk_pos = (x, y)
                    visible_chunks.add(chunk_pos)
                    
                    # Create chunk if it doesn't exist
                    if chunk_pos not in self.chunks:
                        chunk = self._generate_chunk(x, y)
                        if chunk:
                            self.chunks[chunk_pos] = chunk
                            chunk.active = True
                    
                    # Activate existing chunk
                    elif chunk_pos in self.chunks:
                        chunk = self.chunks[chunk_pos]
                        if chunk:
                            chunk.active = True
                            chunk.needs_update = True
            
            # Deactivate chunks outside view distance
            for pos, chunk in self.chunks.items():
                if pos not in visible_chunks:
                    chunk.active = False
            
            # Update active chunks set
            self.active_chunks = {pos: chunk for pos, chunk in self.chunks.items() if chunk and chunk.active}
            
            print(f"Visible chunks: {len(visible_chunks)}, Active chunks: {len(self.active_chunks)}")
            
        except Exception as e:
            print(f"Error updating active chunks: {e}")
            traceback.print_exc()

    def draw(self, screen: pygame.Surface):
        """Draw the world and all its entities"""
        try:
            # Clear screen with sky color
            screen.fill(self._get_sky_color())
            
            # Calculate screen center offset
            screen_center_x = WINDOW_WIDTH / 2
            screen_center_y = WINDOW_HEIGHT / 2
            
            # Draw terrain first
            for chunk_pos in self.visible_chunks:
                chunk = self.chunks.get(chunk_pos)
                if chunk:
                    # Calculate chunk screen position
                    chunk_world_x = chunk_pos[0] * CHUNK_SIZE * TILE_SIZE
                    chunk_world_y = chunk_pos[1] * CHUNK_SIZE * TILE_SIZE
                    
                    # Convert to screen coordinates
                    chunk_screen_x = (chunk_world_x - self.camera['x']) * self.camera['zoom'] + screen_center_x
                    chunk_screen_y = (chunk_world_y - self.camera['y']) * self.camera['zoom'] + screen_center_y
                    
                    # Draw only terrain from chunk
                    chunk.draw_terrain(screen, self.camera['x'], self.camera['y'], self.camera['zoom'])
            
            # Draw all active entities sorted by Y position
            sorted_entities = sorted(
                list(self.active_entities),
                key=lambda e: getattr(e, 'y', 0)
            )
            
            for entity in sorted_entities:
                if entity and hasattr(entity, 'draw'):
                    try:
                        # Calculate entity screen position
                        entity_screen_x = (entity.x - self.camera['x']) * self.camera['zoom'] + screen_center_x
                        entity_screen_y = (entity.y - self.camera['y']) * self.camera['zoom'] + screen_center_y
                        
                        # Only draw if entity is on screen
                        if (-100 <= entity_screen_x <= WINDOW_WIDTH + 100 and 
                            -100 <= entity_screen_y <= WINDOW_HEIGHT + 100):
                            entity.draw(screen, self.camera['x'], self.camera['y'], self.camera['zoom'])
                    except Exception as e:
                        print(f"Error drawing entity {entity}: {e}")
                        continue
            
            # Draw UI elements
            self._draw_ui(screen)
            
            # Apply visual effects
            self._apply_visual_effects(screen)
            
            # Debug: draw entity count
            font = pygame.font.Font(None, 24)
            debug_text = f"Active Entities: {len(self.active_entities)}"
            text_surface = font.render(debug_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, WINDOW_HEIGHT - 30))
            
        except Exception as e:
            print(f"Error drawing world: {e}")
            traceback.print_exc()

    def _draw_ui(self, screen: pygame.Surface):
        """Draw UI elements"""
        try:
            # Get font and colors
            font = pygame.font.Font(None, 24)
            text_color = (255, 255, 255)
            shadow_color = (0, 0, 0)
            
            # Draw time panel
            time_text = f"Day {self.time_system.day} - {self.time_system.hour:02d}:{self.time_system.minute:02d}"
            season_text = f"Season: {self.time_system.get_current_season()}"
            
            # Draw with shadow effect
            def draw_text_with_shadow(text, pos):
                # Draw shadow
                shadow_surface = font.render(text, True, shadow_color)
                screen.blit(shadow_surface, (pos[0] + 2, pos[1] + 2))
                # Draw text
                text_surface = font.render(text, True, text_color)
                screen.blit(text_surface, pos)
            
            # Draw time and season info
            draw_text_with_shadow(time_text, (10, 10))
            draw_text_with_shadow(season_text, (10, 35))
            
            # Draw weather info
            if hasattr(self, 'weather_system'):
                weather_text = f"Weather: {self.weather_system.current_weather.capitalize()}"
                temp_text = f"Temperature: {getattr(self, 'temperature', 20):.1f}°C"
                
                draw_text_with_shadow(weather_text, (10, 60))
                draw_text_with_shadow(temp_text, (10, 85))
            
            # Draw selected entity info
            if self.selected_entity:
                entity_info = []
                entity_info.append(f"Selected: {getattr(self.selected_entity, 'type', 'Unknown')}")
                
                if hasattr(self.selected_entity, 'name'):
                    entity_info.append(f"Name: {self.selected_entity.name}")
                    
                if hasattr(self.selected_entity, 'health'):
                    entity_info.append(f"Health: {self.selected_entity.health}")
                    
                if hasattr(self.selected_entity, 'current_thought'):
                    entity_info.append(f"Thinking: {self.selected_entity.current_thought}")
                
                # Draw entity info at bottom left
                y_pos = WINDOW_HEIGHT - 20 * (len(entity_info) + 1)
                for info in entity_info:
                    draw_text_with_shadow(info, (10, y_pos))
                    y_pos += 20
                    
        except Exception as e:
            print(f"Error drawing UI: {e}")
            traceback.print_exc()

    def _apply_visual_effects(self, screen: pygame.Surface):
        """Apply time of day and weather visual effects"""
        try:
            # Apply time of day lighting
            day_progress = self.time_system.day_progress
            
            # Calculate lighting based on time of day
            if 0.25 <= day_progress < 0.75:  # Daytime
                light_level = 1.0
            else:  # Night
                # Smoother transition between day and night
                if day_progress < 0.25:  # Dawn
                    light_level = 0.3 + (day_progress / 0.25) * 0.7
                else:  # Dusk
                    light_level = 0.3 + ((1.0 - day_progress) / 0.25) * 0.7
            
            # Apply darkness overlay
            if light_level < 1.0:
                darkness = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                darkness.fill((0, 0, 0))
                darkness.set_alpha(int((1.0 - light_level) * 192))
                screen.blit(darkness, (0, 0))
            
            # Apply weather effects
            if self.weather_system.current_weather != 'clear':
                weather_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                
                if self.weather_system.current_weather == 'rain':
                    # Add rain effect
                    for _ in range(100):
                        x = random.randint(0, WINDOW_WIDTH)
                        y = random.randint(0, WINDOW_HEIGHT)
                        pygame.draw.line(weather_overlay, (200, 200, 255, 100),
                                      (x, y), (x - 5, y + 10), 2)
                                      
                elif self.weather_system.current_weather == 'snow':
                    # Add snow effect
                    for _ in range(50):
                        x = random.randint(0, WINDOW_WIDTH)
                        y = random.randint(0, WINDOW_HEIGHT)
                        pygame.draw.circle(weather_overlay, (255, 255, 255, 150),
                                        (x, y), 2)
                                        
                elif self.weather_system.current_weather == 'storm':
                    # Add storm effect
                    for _ in range(200):
                        x = random.randint(0, WINDOW_WIDTH)
                        y = random.randint(0, WINDOW_HEIGHT)
                        pygame.draw.line(weather_overlay, (200, 200, 255, 150),
                                      (x, y), (x - 10, y + 20), 3)
                                      
                screen.blit(weather_overlay, (0, 0))
                
        except Exception as e:
            print(f"Error applying visual effects: {e}")
            traceback.print_exc()
            
    def add_entity(self, entity):
        """Add an entity to the world"""
        try:
            # Assign ID if needed
            if not hasattr(entity, 'id'):
                entity.id = f"entity_{self.entity_id_counter}"
                self.entity_id_counter += 1
                
            # Add to main entity list if not already present
            if entity not in self.entities:
                self.entities.append(entity)
                
            # Calculate chunk coordinates
            chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
            chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
            chunk_pos = (chunk_x, chunk_y)
            
            # Create chunk if it doesn't exist
            if chunk_pos not in self.chunks:
                chunk_data = self.terrain_generator.generate_chunk(chunk_x, chunk_y)
                if chunk_data:
                    new_chunk = Chunk(self, chunk_pos)
                    new_chunk.initialize(chunk_data['heightmap'], chunk_data['biome_map'])
                    self.chunks[chunk_pos] = new_chunk
                    
            # Add to chunk
            chunk = self.chunks.get(chunk_pos)
            if chunk:
                chunk.add_entity(entity)
                
                # Add to active entities if chunk is active
                if chunk_pos in self.active_chunks:
                    self.active_entities.add(entity)
                    
            # Store initial position for chunk tracking
            entity.last_x = entity.x
            entity.last_y = entity.y
                    
            print(f"Added entity {entity.id} at position ({entity.x}, {entity.y})")
            return True
            
        except Exception as e:
            print(f"Error adding entity: {e}")
            traceback.print_exc()
            return False

    def _add_to_grid(self, entity):
        """Add entity to spatial grid"""
        try:
            grid_x = int(entity.x // self.grid_cell_size)
            grid_y = int(entity.y // self.grid_cell_size)
            grid_key = (grid_x, grid_y)
            
            if grid_key not in self.spatial_grid:
                self.spatial_grid[grid_key] = set()
            self.spatial_grid[grid_key].add(entity)
            
        except Exception as e:
            print(f"Error adding entity to grid: {e}")
            
    def _init_spatial_grid(self):
        """Initialize the spatial grid"""
        self.spatial_grid = {}
        self.grid_cell_size = 64
        
        # Add all existing entities to grid
        for entity in self.entities:
            self._add_to_grid(entity)
            
    def _init_render_surfaces(self):
        """Initialize surfaces for rendering"""
        try:
            # Create main surface for world rendering
            self.main_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            
            # Create overlay surface for effects
            self.overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            
            # Create surfaces for each chunk
            for chunk in self.chunks.values():
                if not hasattr(chunk, 'surface') or chunk.surface is None:
                    chunk_surface = pygame.Surface(
                        (CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE),
                        pygame.SRCALPHA
                    )
                    chunk.surface = chunk_surface
                    chunk.needs_update = True
            
            print("Render surfaces initialized successfully")
            
        except Exception as e:
            print(f"Error initializing render surfaces: {e}")
            traceback.print_exc()
            
    def remove_entity(self, entity):
        """Remove an entity from the world"""
        try:
            if entity in self.entities:
                self.entities.remove(entity)
                
            # Remove from chunk
            chunk_x = int(entity.x / (CHUNK_SIZE * TILE_SIZE))
            chunk_y = int(entity.y / (CHUNK_SIZE * TILE_SIZE))
            chunk = self.active_chunks.get((chunk_x, chunk_y))
            
            if chunk and hasattr(chunk, 'entities'):
                chunk.entities.discard(entity)
                
            # Remove from active entities
            self.active_chunks.pop((chunk_x, chunk_y))
            
            # Clean up thought history
            if 'thought' in self.systems and entity.id in self.systems['thought'].thought_history:
                del self.systems['thought'].thought_history[entity.id]
                
            # Clean up status effects
            if 'weather' in self.systems and entity.id in self.systems['weather'].status_effects:
                del self.systems['weather'].status_effects[entity.id]
                
        except Exception as e:
            print(f"Error removing entity: {e}")
            traceback.print_exc()
            
    def get_entities_in_range(self, x: float, y: float, radius: float) -> List:
        """Get all entities within a radius of a point"""
        try:
            nearby = []
            
            # Get chunks that could contain entities within radius
            chunk_radius = int(radius / (CHUNK_SIZE * TILE_SIZE)) + 1
            center_chunk_x = int(x / (CHUNK_SIZE * TILE_SIZE))
            center_chunk_y = int(y / (CHUNK_SIZE * TILE_SIZE))
            
            for dy in range(-chunk_radius, chunk_radius + 1):
                for dx in range(-chunk_radius, chunk_radius + 1):
                    chunk = self.active_chunks.get((center_chunk_x + dx, center_chunk_y + dy))
                    if chunk and hasattr(chunk, 'entities'):
                        # Check each entity in chunk
                        for entity in chunk.entities:
                            dist = math.sqrt((entity.x - x)**2 + (entity.y - y)**2)
                            if dist <= radius:
                                nearby.append(entity)
                                
            return nearby
            
        except Exception as e:
            print(f"Error getting entities in range: {e}")
            traceback.print_exc()
            return []
            
    def get_tile(self, x: float, y: float) -> Optional[Dict]:
        """Get tile data at world coordinates"""
        try:
            # Convert world coordinates to chunk coordinates
            chunk_x = int(x // (CHUNK_SIZE * TILE_SIZE))
            chunk_y = int(y // (CHUNK_SIZE * TILE_SIZE))
            
            # Get chunk
            chunk = self.chunks.get((chunk_x, chunk_y))
            if not chunk:
                return None
            
            # Convert world coordinates to local chunk coordinates
            local_x = int((x // TILE_SIZE) % CHUNK_SIZE)
            local_y = int((y // TILE_SIZE) % CHUNK_SIZE)
            
            # Get tile from chunk
            return chunk.get_tile(local_x, local_y)
            
        except Exception as e:
            print(f"Error getting tile at ({x}, {y}): {e}")
            traceback.print_exc()
            return None

    def _init_camera(self):
        """Initialize camera settings"""
        try:
            self.camera = {
                'x': self.width / 2,
                'y': self.height / 2,
                'target_x': self.width / 2,
                'target_y': self.height / 2,
                'zoom': 1.0,
                'target_zoom': 1.0,
                'min_zoom': 0.5,
                'max_zoom': 4.0,
                'move_speed': 500,
                'zoom_speed': 2.0,
                'smooth_follow': True,  # Add smooth follow setting
                'follow_target': None,
                'shake_amount': 0,
                'shake_duration': 0,
                'viewport_width': WINDOW_WIDTH,
                'viewport_height': WINDOW_HEIGHT,
                'view_distance': 3,
                'bounds': {  # Add camera bounds
                    'min_x': 0,
                    'min_y': 0,
                    'max_x': self.width * TILE_SIZE,
                    'max_y': self.height * TILE_SIZE
                }
            }
            print("Camera initialized successfully")
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            traceback.print_exc()

    def update_camera(self, dt: float, input_state: Dict):
        """Update camera position and zoom"""
        try:
            # Get keyboard state
            keys = pygame.key.get_pressed()
            
            # Calculate movement based on arrow keys/WASD
            move_x = 0
            move_y = 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move_y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move_y += 1
                
            # Normalize diagonal movement
            if move_x != 0 and move_y != 0:
                move_x *= 0.707  # 1/sqrt(2)
                move_y *= 0.707
            
            # Update camera position
            if self.camera.get('smooth_follow', False) and self.camera.get('follow_target'):
                target = self.camera['follow_target']
                if hasattr(target, 'x') and hasattr(target, 'y'):
                    self.camera['target_x'] = target.x
                    self.camera['target_y'] = target.y
            else:
                # Manual camera movement
                move_speed = self.camera['move_speed']
                self.camera['target_x'] += move_x * move_speed * dt / self.camera['zoom']
                self.camera['target_y'] += move_y * move_speed * dt / self.camera['zoom']
            
            # Update zoom
            zoom_delta = 0
            if 'camera_zoom' in input_state:
                zoom_delta = input_state['camera_zoom']
            
            if zoom_delta != 0:
                self.camera['target_zoom'] = max(
                    self.camera['min_zoom'],
                    min(self.camera['max_zoom'],
                        self.camera['target_zoom'] * (1 + zoom_delta * self.camera['zoom_speed'] * dt))
                )
            
            # Smooth camera movement
            lerp_factor = min(1.0, dt * 5)
            self.camera['x'] += (self.camera['target_x'] - self.camera['x']) * lerp_factor
            self.camera['y'] += (self.camera['target_y'] - self.camera['y']) * lerp_factor
            self.camera['zoom'] += (self.camera['target_zoom'] - self.camera['zoom']) * lerp_factor
            
            # Apply camera constraints
            self._constrain_camera()
            
            # Update screen shake
            if self.camera['shake_duration'] > 0:
                self.camera['shake_duration'] -= dt
                if self.camera['shake_duration'] <= 0:
                    self.camera['shake_amount'] = 0
                else:
                    shake_x = random.uniform(-1, 1) * self.camera['shake_amount']
                    shake_y = random.uniform(-1, 1) * self.camera['shake_amount']
                    self.camera['x'] += shake_x
                    self.camera['y'] += shake_y
            
            # Update visible chunks based on new camera position
            self._update_active_chunks()
            
        except Exception as e:
            print(f"Error updating camera: {e}")
            traceback.print_exc()

    def _constrain_camera(self):
        """Keep camera within world bounds"""
        try:
            if 'bounds' not in self.camera:
                self.camera['bounds'] = {
                    'min_x': 0,
                    'min_y': 0,
                    'max_x': self.width * TILE_SIZE,
                    'max_y': self.height * TILE_SIZE
                }
                
            # Calculate viewport dimensions in world space
            viewport_world_width = self.camera['viewport_width'] / max(0.1, self.camera['zoom'])
            viewport_world_height = self.camera['viewport_height'] / max(0.1, self.camera['zoom'])
            
            # Calculate bounds with margin
            margin = CAMERA_SETTINGS.get('bounds_margin', 100)  # Default margin if not set
            min_x = self.camera['bounds']['min_x'] - margin
            min_y = self.camera['bounds']['min_y'] - margin
            max_x = self.camera['bounds']['max_x'] + margin - viewport_world_width
            max_y = self.camera['bounds']['max_y'] + margin - viewport_world_height
            
            # Constrain camera position
            self.camera['x'] = max(min_x, min(max_x, self.camera['x']))
            self.camera['y'] = max(min_y, min(max_y, self.camera['y']))
            
            # Constrain target position as well
            if 'target_x' in self.camera and 'target_y' in self.camera:
                self.camera['target_x'] = max(min_x, min(max_x, self.camera['target_x']))
                self.camera['target_y'] = max(min_y, min(max_y, self.camera['target_y']))
                
        except Exception as e:
            print(f"Error constraining camera: {e}")
            traceback.print_exc()

    def add_screen_shake(self, amount: float):
        """Add screen shake effect"""
        try:
            self.camera['shake_amount'] = min(
                self.camera['shake_amount'] + amount,
                CAMERA_SETTINGS['max_shake']
            )
        except Exception as e:
            print(f"Error adding screen shake: {e}")
            traceback.print_exc()

    def focus_on_entity(self, entity, instant: bool = False):
        """Focus camera on an entity"""
        try:
            if hasattr(entity, 'x') and hasattr(entity, 'y'):
                if instant:
                    self.camera['x'] = self.camera['target_x'] = entity.x
                    self.camera['y'] = self.camera['target_y'] = entity.y
                else:
                    self.camera['target_x'] = entity.x
                    self.camera['target_y'] = entity.y
        except Exception as e:
            print(f"Error focusing on entity: {e}")
            traceback.print_exc()

    def _get_sky_color(self):
        """Get the sky color based on the time of day"""
        try:
            light_level = self.time_system.get_light_level()
            return (
                int(135 * light_level),  # R
                int(206 * light_level),  # G
                int(235 * light_level)   # B
            )
        except Exception as e:
            print(f"Error getting sky color: {e}")
            traceback.print_exc()
            return (255, 255, 255)  # Default to white

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        try:
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Get world coordinates of click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x = self.camera['x'] + (mouse_x - WINDOW_WIDTH/2) / self.camera['zoom']
                    world_y = self.camera['y'] + (mouse_y - WINDOW_HEIGHT/2) / self.camera['zoom']
                    
                    # Check for entity selection
                    clicked_entity = None
                    for entity in self.active_entities:
                        if hasattr(entity, 'size'):
                            # Calculate distance to entity
                            dx = entity.x - world_x
                            dy = entity.y - world_y
                            distance = math.sqrt(dx*dx + dy*dy)
                            if distance <= entity.size:
                                clicked_entity = entity
                                break
                    
                    self.selected_entity = clicked_entity
                    
                elif event.button == 4:  # Mouse wheel up
                    self.camera['target_zoom'] = min(
                        self.camera['max_zoom'],
                        self.camera['zoom'] * (1 + CAMERA_SETTINGS['zoom_speed'])
                    )
                    
                elif event.button == 5:  # Mouse wheel down
                    self.camera['target_zoom'] = max(
                        self.camera['min_zoom'],
                        self.camera['zoom'] * (1 - CAMERA_SETTINGS['zoom_speed'])
                    )
            
            # Handle keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.selected_entity:
                        self.focus_on_entity(self.selected_entity)
                elif event.key == pygame.K_ESCAPE:
                    self.selected_entity = None
                    
        except Exception as e:
            print(f"Error handling event: {e}")
            traceback.print_exc()

    def _generate_chunk(self, x: int, y: int) -> Optional[Chunk]:
        """Generate a new chunk at the given coordinates"""
        try:
            # Generate terrain data using the terrain generator
            if not hasattr(self, 'terrain_generator'):
                self.terrain_generator = TerrainGenerator(seed=self.seed)
            
            # Generate chunk data
            chunk_data = self.terrain_generator.generate_chunk(x, y)
            if not chunk_data:
                return None
                
            # Create and initialize chunk
            chunk = Chunk(self, (x, y))
            chunk.initialize(chunk_data['heightmap'], chunk_data['biome_map'])
            
            # Generate initial resources and features
            self._generate_chunk_resources(chunk)
            
            return chunk
            
        except Exception as e:
            print(f"Error generating chunk at ({x}, {y}): {e}")
            traceback.print_exc()
            return None
            
    def _generate_chunk_resources(self, chunk: Chunk):
        """Generate initial resources for a chunk"""
        try:
            # Get chunk position
            chunk_x, chunk_y = chunk.pos
            
            # Calculate world position of chunk
            world_x = chunk_x * CHUNK_SIZE * TILE_SIZE
            world_y = chunk_y * CHUNK_SIZE * TILE_SIZE
            
            # Generate resources based on biome
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile = chunk.get_tile(x, y)
                    if not tile:
                        continue
                        
                    biome = tile['biome']
                    if biome not in BIOMES:
                        continue
                        
                    # Get resource types for this biome
                    biome_data = BIOMES[biome]
                    resource_types = biome_data.get('resources', [])
                    
                    # Random chance to spawn resource
                    if resource_types and random.random() < 0.1:  # 10% chance per tile
                        resource_type = random.choice(resource_types)
                        
                        # Calculate world position for resource
                        resource_x = world_x + x * TILE_SIZE
                        resource_y = world_y + y * TILE_SIZE
                        
                        # Create resource
                        resource = Resource(self, (resource_x, resource_y), resource_type)
                        self.add_entity(resource)
                        
        except Exception as e:
            print(f"Error generating chunk resources: {e}")
            traceback.print_exc() 