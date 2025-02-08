import random
import noise
import pygame
import threading
import traceback
from queue import Queue
from typing import Dict, List, Tuple, Optional

from ..entities.human import Human
from ..entities.animal import Animal
from ..entities.plant import Plant
from ..chunk import Chunk
from .terrain_generator import TerrainGenerator
from ...constants import (
    WORLD_WIDTH, WORLD_HEIGHT, CHUNK_SIZE, ENTITY_TYPES,
    WORLD_CHUNKS_X, WORLD_CHUNKS_Y, TILE_SIZE,
    BIOMES, RESOURCE_TYPES, SEASONS, SEASON_ORDER,
    WEATHER_TYPES, TIME_SPEEDS
)

class WorldGenerator:
    def __init__(self, world, options=None):
        """Initialize world generator"""
        try:
            print("Initializing world generator...")
            self.world = world
            self.options = options or {}
            self.seed = random.randint(0, 999999)
            random.seed(self.seed)
            
            # Initialize settings with defaults
            self.settings = {
                'human_count': 10,  # Start with 10 humans
                'animal_count': 20,  # Start with 20 animals
                'plant_density': 0.3,  # 30% chance for plants per suitable tile
                'resource_density': 0.2,  # 20% chance for resources per suitable tile
                'structure_density': 0.1  # 10% chance for structures per suitable area
            }
            
            # Override defaults with provided options
            if options:
                self.settings.update(options)
                
            # Initialize generators
            self.terrain_generator = TerrainGenerator(seed=self.seed)
            
            # Generation state
            self.generation_progress = 0.0
            self.generation_status = ""
            self.is_generating = False
            self.generation_complete = False
            
            print(f"World generator initialized with seed {self.seed}")
            
        except Exception as e:
            print(f"Error initializing world generator: {e}")
            traceback.print_exc()
            raise

    def generate_world(self, progress_callback=None):
        """Generate the complete world"""
        try:
            total_steps = 5
            current_step = 0
            
            print("Starting world generation...")
            
            # Step 1: Generate initial terrain
            if progress_callback:
                progress_callback(current_step / total_steps, "Generating terrain...")
            if not self._generate_terrain(progress_callback, current_step, total_steps):
                raise Exception("Failed to generate terrain")
            current_step += 1
            
            # Step 2: Initialize world systems
            if progress_callback:
                progress_callback(current_step / total_steps, "Initializing systems...")
            if not self._initialize_systems(progress_callback, current_step, total_steps):
                raise Exception("Failed to initialize systems")
            current_step += 1
            
            # Step 3: Generate initial entities
            if progress_callback:
                progress_callback(current_step / total_steps, "Spawning entities...")
            if not self._generate_initial_entities(progress_callback, current_step, total_steps):
                raise Exception("Failed to generate entities")
            current_step += 1
            
            # Step 4: Generate structures
            if progress_callback:
                progress_callback(current_step / total_steps, "Generating structures...")
            if not self._generate_structures(progress_callback, current_step, total_steps):
                raise Exception("Failed to generate structures")
            current_step += 1
            
            # Step 5: Finalize world
            if progress_callback:
                progress_callback(current_step / total_steps, "Finalizing world...")
            if not self._finalize_world(progress_callback, current_step, total_steps):
                raise Exception("Failed to finalize world")
            
            # Final progress update
            if progress_callback:
                progress_callback(1.0, "World generation complete!")
            
            self.generation_complete = True
            print("World generation completed successfully")
            return True
            
        except Exception as e:
            self.error = str(e)
            print(f"Error generating world: {e}")
            traceback.print_exc()
            return False

    def _generate_terrain(self, progress_callback, step, total_steps):
        """Generate initial terrain chunks"""
        try:
            print("Generating initial terrain...")
            
            # Generate chunks in a spiral pattern from center
            center_x = WORLD_CHUNKS_X // 2
            center_y = WORLD_CHUNKS_Y // 2
            
            chunks_generated = 0
            total_initial_chunks = 25  # 5x5 grid
            
            # Generate initial 5x5 grid of chunks
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    chunk_x = center_x + dx
                    chunk_y = center_y + dy
                    
                    if 0 <= chunk_x < WORLD_CHUNKS_X and 0 <= chunk_y < WORLD_CHUNKS_Y:
                        try:
                            print(f"Generating chunk at ({chunk_x}, {chunk_y})")
                            chunk_data = self.terrain_generator.generate_chunk(chunk_x, chunk_y)
                            
                            if chunk_data and 'heightmap' in chunk_data and 'biome_map' in chunk_data:
                                chunk = self.world.chunks.get((chunk_x, chunk_y))
                                if chunk is None:
                                    chunk = self.world._create_chunk((chunk_x, chunk_y))
                                    self.world.chunks[(chunk_x, chunk_y)] = chunk
                                
                                chunk.initialize(chunk_data['heightmap'], chunk_data['biome_map'])
                                chunk.active = True
                                chunk.needs_update = True
                                
                                chunks_generated += 1
                                if progress_callback:
                                    sub_progress = chunks_generated / total_initial_chunks
                                    total_progress = (step + sub_progress) / total_steps
                                    progress_callback(total_progress, f"Generated chunk {chunks_generated}/{total_initial_chunks}")
                            else:
                                print(f"Failed to generate chunk data at ({chunk_x}, {chunk_y})")
                                
                        except Exception as e:
                            print(f"Error generating chunk at ({chunk_x}, {chunk_y}): {e}")
                            traceback.print_exc()
                            continue
            
            print(f"Generated {chunks_generated} initial chunks")
            return chunks_generated > 0
            
        except Exception as e:
            print(f"Error in terrain generation: {e}")
            traceback.print_exc()
            return False

    def _generate_initial_entities(self, progress_callback, step, total_steps):
        """Generate initial entities in the world"""
        try:
            print("Generating initial entities...")
            entities_generated = 0
            total_entities = (self.settings['human_count'] + 
                            self.settings['animal_count'])
            
            # Generate humans in suitable biomes
            human_biomes = ['plains', 'forest', 'savanna', 'beach']
            for i in range(self.settings['human_count']):
                x, y = self._find_spawn_position(human_biomes)
                if x is not None and y is not None:
                    try:
                        # Create human with random type
                        human_type = random.choice(list(ENTITY_TYPES.keys()))
                        human = Human(self.world, x, y, human_type)
                        self.world.add_entity(human)
                        entities_generated += 1
                        
                        if progress_callback:
                            sub_progress = entities_generated / total_entities
                            total_progress = (step + sub_progress) / total_steps
                            progress_callback(total_progress, f"Generated human {i+1}/{self.settings['human_count']}")
                    except Exception as e:
                        print(f"Error generating human: {e}")
                        traceback.print_exc()
                        continue
                    
            # Generate animals based on biome
            animal_types = {
                'plains': ['deer', 'rabbit', 'fox'],
                'forest': ['wolf', 'bear', 'deer'],
                'savanna': ['lion', 'zebra', 'gazelle'],
                'tundra': ['wolf', 'fox', 'rabbit'],
                'desert': ['snake', 'lizard', 'scorpion']
            }
            
            for biome, animals in animal_types.items():
                count = int(self.settings['animal_count'] / len(animal_types))
                for i in range(count):
                    x, y = self._find_spawn_position([biome])
                    if x is not None and y is not None:
                        try:
                            animal_type = random.choice(animals)
                            animal = Animal(self.world, x, y, animal_type)
                            self.world.add_entity(animal)
                            entities_generated += 1
                            
                            if progress_callback:
                                sub_progress = entities_generated / total_entities
                                total_progress = (step + sub_progress) / total_steps
                                progress_callback(total_progress, f"Generated {animal_type} {i+1}/{count}")
                        except Exception as e:
                            print(f"Error generating animal: {e}")
                            traceback.print_exc()
                            continue
                        
            # Generate plants
            plants_generated = self._spawn_initial_plants()
            if not plants_generated:
                print("Warning: Failed to generate some plants")
                
            print(f"Generated {entities_generated} entities")
            return entities_generated > 0
            
        except Exception as e:
            print(f"Error generating initial entities: {e}")
            traceback.print_exc()
            return False
            
    def _spawn_initial_plants(self):
        """Spawn initial plants in the world"""
        try:
            plants_generated = 0
            
            # Get all chunks
            for chunk_pos, chunk in self.world.chunks.items():
                # Skip if chunk is not initialized
                if not chunk or not hasattr(chunk, 'get_tile'):
                    continue
                    
                # Process each tile in chunk
                for local_y in range(CHUNK_SIZE):
                    for local_x in range(CHUNK_SIZE):
                        tile = chunk.get_tile(local_x, local_y)
                        if not tile:
                            continue
                            
                        biome = tile.get('biome')
                        if not biome or biome in ['ocean', 'frozen_ocean']:
                            continue
                            
                        # Get valid plant types for this biome
                        valid_plants = [
                            plant_type for plant_type, props in BIOMES.items()
                            if biome in props.get('biomes', [])
                        ]
                        
                        if not valid_plants:
                            continue
                            
                        # Check plant density
                        if random.random() < self.settings['plant_density']:
                            try:
                                # Calculate world coordinates
                                world_x = (chunk_pos[0] * CHUNK_SIZE + local_x) * TILE_SIZE
                                world_y = (chunk_pos[1] * CHUNK_SIZE + local_y) * TILE_SIZE
                                
                                # Add random offset within tile
                                world_x += random.uniform(0, TILE_SIZE)
                                world_y += random.uniform(0, TILE_SIZE)
                                
                                # Create and add plant
                                plant_type = random.choice(valid_plants)
                                plant = Plant(self.world, world_x, world_y, plant_type)
                                self.world.add_entity(plant)
                                plants_generated += 1
                                
                            except Exception as e:
                                print(f"Error generating plant: {e}")
                                traceback.print_exc()
                                continue
                                
            print(f"Generated {plants_generated} plants")
            return plants_generated > 0
            
        except Exception as e:
            print(f"Error spawning plants: {e}")
            traceback.print_exc()
            return False

    def _generate_structures(self, progress_callback, step, total_steps):
        """Generate initial structures in the world"""
        try:
            print("Generating world structures...")
            structures_generated = 0
            
            # Calculate number of structures based on world size and density
            total_structures = int(WORLD_WIDTH * WORLD_HEIGHT * self.settings['structure_density'])
            
            # Structure types and their biome preferences
            structure_types = {
                'village': {
                    'biomes': ['plains', 'forest', 'savanna'],
                    'min_spacing': 50,
                    'size_range': (5, 10),
                    'weight': 0.4
                },
                'camp': {
                    'biomes': ['plains', 'forest', 'desert', 'tundra'],
                    'min_spacing': 30,
                    'size_range': (3, 6),
                    'weight': 0.3
                },
                'ruins': {
                    'biomes': ['plains', 'forest', 'desert', 'mountains'],
                    'min_spacing': 40,
                    'size_range': (4, 8),
                    'weight': 0.2
                },
                'cave': {
                    'biomes': ['mountains', 'hills', 'forest'],
                    'min_spacing': 25,
                    'size_range': (2, 5),
                    'weight': 0.1
                }
            }
            
            # Keep track of structure positions to maintain minimum spacing
            structure_positions = []
            
            for i in range(total_structures):
                try:
                    # Select structure type based on weights
                    weights = [info['weight'] for info in structure_types.values()]
                    structure_type = random.choices(list(structure_types.keys()), weights=weights)[0]
                    structure_info = structure_types[structure_type]
                    
                    # Find valid position for structure
                    for attempt in range(50):  # Maximum attempts per structure
                        pos = self._find_spawn_position(structure_info['biomes'])
                        if not pos:
                            continue
                            
                        # Check minimum spacing from other structures
                        too_close = False
                        for other_pos in structure_positions:
                            dist = ((pos[0] - other_pos[0])**2 + (pos[1] - other_pos[1])**2)**0.5
                            if dist < structure_info['min_spacing']:
                                too_close = True
                                break
                                
                        if not too_close:
                            # Generate structure
                            size = random.randint(*structure_info['size_range'])
                            structure_data = self._generate_structure(
                                structure_type,
                                pos[0],
                                pos[1],
                                size
                            )
                            
                            if structure_data:
                                # Add structure to world
                                chunk_x = int(pos[0] / (CHUNK_SIZE * TILE_SIZE))
                                chunk_y = int(pos[1] / (CHUNK_SIZE * TILE_SIZE))
                                chunk = self.world.chunks.get((chunk_x, chunk_y))
                                
                                if chunk:
                                    if not hasattr(chunk, 'structures'):
                                        chunk.structures = []
                                    chunk.structures.append(structure_data)
                                    structure_positions.append(pos)
                                    structures_generated += 1
                                    
                                    # Update progress
                                    if progress_callback:
                                        sub_progress = structures_generated / total_structures
                                        total_progress = (step + sub_progress) / total_steps
                                        progress_callback(total_progress, 
                                                        f"Generated {structure_type} {structures_generated}/{total_structures}")
                                    break
                                    
                except Exception as e:
                    print(f"Error generating structure: {e}")
                    traceback.print_exc()
                    continue
                    
            print(f"Generated {structures_generated} structures")
            return structures_generated > 0
            
        except Exception as e:
            print(f"Error generating structures: {e}")
            traceback.print_exc()
            return False
            
    def _generate_structure(self, structure_type: str, x: float, y: float, size: int) -> Optional[Dict]:
        """Generate a single structure"""
        try:
            structure = {
                'type': structure_type,
                'x': x,
                'y': y,
                'size': size,
                'features': [],
                'resources': [],
                'npcs': []
            }
            
            # Add structure-specific features
            if structure_type == 'village':
                # Add buildings
                for _ in range(size):
                    structure['features'].append({
                        'type': 'building',
                        'subtype': random.choice(['house', 'shop', 'workshop']),
                        'offset_x': random.uniform(-size, size),
                        'offset_y': random.uniform(-size, size)
                    })
                    
                # Add resources
                for _ in range(size // 2):
                    structure['resources'].append({
                        'type': random.choice(['food', 'water', 'wood', 'stone']),
                        'amount': random.uniform(10, 20)
                    })
                    
            elif structure_type == 'camp':
                # Add tents and campfire
                structure['features'].append({
                    'type': 'campfire',
                    'offset_x': 0,
                    'offset_y': 0
                })
                
                for _ in range(size - 1):
                    structure['features'].append({
                        'type': 'tent',
                        'offset_x': random.uniform(-size/2, size/2),
                        'offset_y': random.uniform(-size/2, size/2)
                    })
                    
            elif structure_type == 'ruins':
                # Add ruined buildings and debris
                for _ in range(size):
                    structure['features'].append({
                        'type': 'ruins',
                        'subtype': random.choice(['wall', 'pillar', 'foundation']),
                        'offset_x': random.uniform(-size, size),
                        'offset_y': random.uniform(-size, size)
                    })
                    
            elif structure_type == 'cave':
                # Add cave entrance and interior features
                structure['features'].append({
                    'type': 'cave_entrance',
                    'offset_x': 0,
                    'offset_y': 0
                })
                
                for _ in range(size - 1):
                    structure['features'].append({
                        'type': 'cave_feature',
                        'subtype': random.choice(['stalactite', 'stalagmite', 'crystal']),
                        'offset_x': random.uniform(-size/2, size/2),
                        'offset_y': random.uniform(-size/2, size/2)
                    })
                    
            return structure
            
        except Exception as e:
            print(f"Error generating structure: {e}")
            traceback.print_exc()
            return None
            
    def _finalize_world(self, progress_callback, step, total_steps):
        """Finalize world generation"""
        try:
            print("Finalizing world generation...")
            
            # Ensure all chunks are properly initialized
            for chunk in self.world.chunks.values():
                if not chunk.surface or chunk.needs_update:
                    chunk._update_surface()
                    
            # Initialize pathfinding grid
            if hasattr(self.world, '_init_pathfinding'):
                print("Initializing pathfinding grid...")
                self.world._init_pathfinding()
                
            # Connect structures with paths
            print("Generating paths between structures...")
            self._generate_paths()
            
            # Update all entity states
            print("Updating entity states...")
            for entity in self.world.entities:
                if hasattr(entity, 'update_state'):
                    entity.update_state()
                    
            # Final world state validation
            if not self._validate_world_state():
                print("Warning: World state validation failed")
                
            print("World finalization complete")
            return True
            
        except Exception as e:
            print(f"Error finalizing world: {e}")
            traceback.print_exc()
            return False
            
    def _validate_world_state(self) -> bool:
        """Validate the final world state"""
        try:
            # Check for required systems
            required_systems = ['thought', 'weather', 'language']
            for system in required_systems:
                if system not in self.world.systems:
                    print(f"Warning: Missing required system: {system}")
                    return False
                    
            # Check for minimum required entities
            if len(self.world.entities) < (self.settings['human_count'] + self.settings['animal_count']) / 2:
                print("Warning: Insufficient number of entities generated")
                return False
                
            # Check for active chunks
            if not self.world.active_chunks:
                print("Warning: No active chunks found")
                return False
                
            # Validate time system
            if not hasattr(self.world, 'time_system'):
                print("Warning: Time system not initialized")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error validating world state: {e}")
            traceback.print_exc()
            return False

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a single chunk"""
        try:
            return self.terrain_generator.generate_chunk(chunk_x, chunk_y)
        except Exception as e:
            print(f"Error generating chunk at ({chunk_x}, {chunk_y}): {e}")
            traceback.print_exc()
            return None

    def get_generation_result(self):
        """Get the generated world data or None if not complete"""
        if not self.generation_thread or not self.generation_complete:
            return None
            
        if self.error:
            raise Exception(self.error)
            
        return {
            'chunks': self.world.chunks,
            'entities': self.world.entities,
            'seed': self.world.seed
        }

    def is_generation_complete(self):
        """Check if world generation is complete"""
        return self.generation_complete and not (self.generation_thread and self.generation_thread.is_alive())

    def get_progress(self):
        """Get current generation progress"""
        return self.generation_progress, self.generation_step

    def _spawn_entities_in_batches(self, progress_callback=None):
        """Spawn entities in smaller batches to manage memory"""
        try:
            # Calculate entity counts with reasonable limits
            world_size = (self.world.width * self.world.height) / (1000 * 1000)
            size_factor = min(world_size, 2.0)  # Cap at 2x default
            
            num_humans = max(1, min(int(10 * size_factor), 50))
            num_animals = max(1, min(int(20 * size_factor), 100))
            num_plants = max(1, min(int(100 * size_factor), 500))
            
            # Spawn humans
            for i in range(num_humans):
                x, y, biome = self._find_spawn_position(['grass', 'forest'])
                if x is not None and y is not None:
                    human = Human(self.world, float(x), float(y))
                    self.world.add_entity(human)
                self.generation_progress = 40 + (i / num_humans) * 20
                if progress_callback:
                    progress_callback(self.generation_progress, "Spawning humans...")
            
            # Spawn animals
            for i in range(num_animals):
                x, y, biome = self._find_spawn_position(['grass', 'forest', 'savanna'])
                if x is not None and y is not None:
                    animal_type = random.choice(list(ENTITY_TYPES.keys()))
                    animal = Animal(self.world, float(x), float(y), animal_type)
                    self.world.add_entity(animal)
                self.generation_progress = 60 + (i / num_animals) * 20
                if progress_callback:
                    progress_callback(self.generation_progress, "Spawning animals...")
            
            # Spawn plants
            for i in range(num_plants):
                x, y, biome = self._find_spawn_position(['grass', 'forest', 'jungle'])
                if x is not None and y is not None:
                    valid_plants = BIOMES.get(biome, [])
                    if valid_plants:
                        plant_type = random.choice([p for p in valid_plants if p in ENTITY_TYPES])
                        plant = Plant(self.world, float(x), float(y), plant_type)
                        self.world.add_entity(plant)
                self.generation_progress = 80 + (i / num_plants) * 20
                if progress_callback:
                    progress_callback(self.generation_progress, "Spawning plants...")
                    
        except Exception as e:
            print(f"Error spawning entities: {e}")
            import traceback
            traceback.print_exc()

    def _find_spawn_position(self, valid_biomes):
        """Find a valid spawn position for an entity"""
        try:
            # Try multiple times to find a valid position
            for _ in range(100):  # Try up to 100 times
                # Choose random chunk coordinates
                chunk_x = random.randint(0, self.world.width - 1)
                chunk_y = random.randint(0, self.world.height - 1)
                chunk_pos = (chunk_x, chunk_y)
                
                # Generate chunk if it doesn't exist
                if chunk_pos not in self.world.chunks:
                    chunk_data = self.terrain_generator.generate_chunk(chunk_x, chunk_y)
                    if chunk_data and 'heightmap' in chunk_data and 'biome_map' in chunk_data:
                        new_chunk = Chunk(self.world, chunk_pos)
                        new_chunk.initialize(chunk_data['heightmap'], chunk_data['biome_map'])
                        self.world.chunks[chunk_pos] = new_chunk
                
                chunk = self.world.chunks.get(chunk_pos)
                if not chunk:
                    continue
                
                # Choose random position within chunk
                local_x = random.randint(0, CHUNK_SIZE - 1)
                local_y = random.randint(0, CHUNK_SIZE - 1)
                
                # Get tile information
                tile = chunk.get_tile(local_x, local_y)
                if not tile:
                    continue
                    
                # Check if tile is suitable
                if tile.get('walkable', False) and tile.get('biome') in valid_biomes:
                    # Convert to world coordinates
                    world_x = (chunk_x * CHUNK_SIZE + local_x) * TILE_SIZE
                    world_y = (chunk_y * CHUNK_SIZE + local_y) * TILE_SIZE
                    
                    # Add some random offset within the tile
                    world_x += random.uniform(0, TILE_SIZE)
                    world_y += random.uniform(0, TILE_SIZE)
                    
                    return world_x, world_y
                    
            print("Warning: Could not find valid spawn position")
            return None, None
            
        except Exception as e:
            print(f"Error finding spawn position: {e}")
            traceback.print_exc()
            return None, None

    def _generate_chunks(self, world_data):
        """Generate the initial chunks of the world"""
        chunks_x = WORLD_WIDTH // (CHUNK_SIZE * 32)
        chunks_y = WORLD_HEIGHT // (CHUNK_SIZE * 32)
        
        for x in range(-chunks_x, chunks_x + 1):
            for y in range(-chunks_y, chunks_y + 1):
                chunk = self.terrain_generator.generate_chunk(x, y)
                world_data['chunks'][(x, y)] = chunk
                
    def _find_valid_position(self, chunks, valid_biomes):
        """Find a valid position for entity placement"""
        for _ in range(100):  # Try 100 times to find valid position
            # Choose random chunk
            chunk_x = random.randint(-5, 5)
            chunk_y = random.randint(-5, 5)
            
            if (chunk_x, chunk_y) not in chunks:
                continue
                
            # Choose random position within chunk
            x = chunk_x * CHUNK_SIZE + random.randint(0, CHUNK_SIZE-1)
            y = chunk_y * CHUNK_SIZE + random.randint(0, CHUNK_SIZE-1)
            
            # Check if position is valid
            chunk = chunks[(chunk_x, chunk_y)]
            tile = chunk[y % CHUNK_SIZE][x % CHUNK_SIZE]
            
            if tile['biome'] in valid_biomes:
                return x * 32, y * 32  # Convert to world coordinates
                
        return None 

    def generate(self) -> Dict:
        """Generate a complete world"""
        print("Generating world...")
        
        # Generate base terrain
        elevation = self._generate_noise_map('elevation')
        moisture = self._generate_noise_map('moisture')
        temperature = self._generate_noise_map('temperature')
        
        # Generate tiles
        tiles = self._generate_tiles(elevation, moisture, temperature)
        
        # Add resources
        resources = self._generate_resources(tiles)
        
        # Generate points of interest
        points_of_interest = self._generate_points_of_interest(tiles)
        
        # Generate paths
        paths = self._generate_paths(points_of_interest, tiles)
        
        return {
            'tiles': tiles,
            'resources': resources,
            'points_of_interest': points_of_interest,
            'paths': paths,
            'seed': self.world.seed
        }
        
    def _generate_tiles(self, elevation: List[List[float]], 
                       moisture: List[List[float]], 
                       temperature: List[List[float]]) -> List[List[Dict]]:
        """Generate tiles based on noise maps"""
        tiles = []
        
        for y in range(self.world.height):
            row = []
            for x in range(self.world.width):
                # Determine biome based on elevation, moisture, and temperature
                biome = self._determine_biome(
                    elevation[y][x],
                    moisture[y][x],
                    temperature[y][x]
                )
                
                # Create tile
                tile = {
                    'x': x,
                    'y': y,
                    'biome': biome,
                    'elevation': elevation[y][x],
                    'moisture': moisture[y][x],
                    'temperature': temperature[y][x],
                    'walkable': self.world.biomes[biome]['walkable'],
                    'color': self._vary_color(self.world.biomes[biome]['color'], 20),
                    'resources': [],
                    'features': []
                }
                row.append(tile)
            tiles.append(row)
            
        return tiles
        
    def _determine_biome(self, elevation: float, moisture: float, temperature: float) -> str:
        """Determine biome based on elevation, moisture, and temperature"""
        if elevation < 0.2:
            return 'ocean'
        elif elevation < 0.3:
            return 'beach'
        elif elevation > 0.8:
            if temperature < 0.2:
                return 'snow'
            else:
                return 'mountain'
        else:
            if temperature < 0.2:
                return 'snow'
            elif temperature < 0.4:
                if moisture > 0.6:
                    return 'forest'
                else:
                    return 'grass'
            elif temperature < 0.7:
                if moisture > 0.6:
                    return 'forest'
                elif moisture > 0.3:
                    return 'grass'
                else:
                    return 'savanna'
            else:
                if moisture > 0.6:
                    return 'jungle'
                elif moisture < 0.2:
                    return 'desert'
                else:
                    return 'savanna'
                    
    def _vary_color(self, base_color: Tuple[int, int, int], variation: int) -> Tuple[int, int, int]:
        """Add slight random variation to a color"""
        return tuple(
            max(0, min(255, c + random.randint(-variation, variation)))
            for c in base_color
        )
        
    def _generate_resources(self, tiles: List[List[Dict]]) -> List[Dict]:
        """Generate resources across the world"""
        try:
            resources = []
            
            for y in range(self.world.height):
                for x in range(self.world.width):
                    tile = tiles[y][x]
                    biome = tile.get('biome', 'plains')  # Default to plains if no biome
                    
                    # Check each resource type
                    for resource_type, settings in RESOURCE_TYPES.items():
                        # Skip water tiles except for fish
                        if biome in ['ocean', 'river', 'lake'] and resource_type != 'fish':
                            continue
                            
                        # Skip if biome not in allowed biomes
                        if biome not in settings['biomes']:
                            continue
                            
                        # Calculate spawn chance
                        base_chance = settings['frequency']
                        
                        # Modify chance based on biome and settings
                        if biome == 'mountains' and resource_type in ['stone', 'ore']:
                            base_chance *= 1.5
                        elif biome == 'forest' and resource_type in ['wood', 'berry']:
                            base_chance *= 1.3
                        
                        # Random check with density modifier
                        if random.random() < (base_chance * self.settings['resource_density']):
                            try:
                                # Create resource data
                                resource_data = {
                                    'type': resource_type,
                                    'x': x,
                                    'y': y,
                                    'quantity': random.randint(
                                        int(settings['max_quantity'] * 0.5),
                                        settings['max_quantity']
                                    ),
                                    'properties': settings.copy()
                                }
                                
                                resources.append(resource_data)
                                
                                # Add to tile's resources list
                                if 'resources' not in tile:
                                    tile['resources'] = []
                                tile['resources'].append(resource_type)
                                
                            except Exception as e:
                                print(f"Error generating specific resource {resource_type}: {e}")
                                continue
                    
            return resources
            
        except Exception as e:
            print(f"Error generating resources: {e}")
            traceback.print_exc()
            return []
        
    def _generate_points_of_interest(self, tiles: List[List[Dict]]) -> List[Dict]:
        """Generate points of interest like villages, caves, etc."""
        points = []
        min_distance = 10  # Minimum distance between points
        
        # Try to place points of interest
        for _ in range(20):  # Number of attempts
            x = random.randint(0, self.world.width-1)
            y = random.randint(0, self.world.height-1)
            
            # Check if location is suitable
            if not tiles[y][x]['walkable']:
                continue
                
            # Check distance from other points
            too_close = False
            for point in points:
                dx = point['x'] - x
                dy = point['y'] - y
                if (dx*dx + dy*dy) < min_distance*min_distance:
                    too_close = True
                    break
                    
            if too_close:
                continue
                
            # Determine point type based on biome
            biome = tiles[y][x]['biome']
            if biome == 'forest':
                poi_type = random.choice(['village', 'cave', 'ruins'])
            elif biome == 'mountain':
                poi_type = random.choice(['cave', 'mine', 'peak'])
            elif biome == 'desert':
                poi_type = random.choice(['oasis', 'ruins', 'pyramid'])
            else:
                poi_type = random.choice(['village', 'camp', 'ruins'])
                
            points.append({
                'type': poi_type,
                'x': x,
                'y': y,
                'name': self._generate_poi_name(poi_type)
            })
            
            # Add to tile features
            tiles[y][x]['features'].append(poi_type)
            
        return points
        
    def _generate_paths(self, points_of_interest: List[Dict], tiles: List[List[Dict]]) -> List[List[Tuple[int, int]]]:
        """Generate paths between points of interest"""
        paths = []
        
        # Sort points by type to prioritize connections
        villages = [p for p in points_of_interest if p['type'] == 'village']
        resources = [p for p in points_of_interest if p['type'] in ['mine', 'cave', 'oasis']]
        
        # Connect villages to nearest resources
        for village in villages:
            nearest_resources = sorted(
                resources,
                key=lambda r: (r['x'] - village['x'])**2 + (r['y'] - village['y'])**2
            )[:2]
            
            for resource in nearest_resources:
                path = self._generate_path(village, resource, tiles)
                if path:
                    paths.append(path)
                    # Mark path tiles
                    for x, y in path:
                        if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]):
                            tiles[y][x]['features'].append('path')
        
        # Connect villages to nearest villages
        for i, village1 in enumerate(villages):
            if i + 1 < len(villages):
                nearest_village = min(
                    villages[i+1:],
                    key=lambda v: (v['x'] - village1['x'])**2 + (v['y'] - village1['y'])**2
                )
                path = self._generate_path(village1, nearest_village, tiles)
                if path:
                    paths.append(path)
                    # Mark path tiles
                    for x, y in path:
                        if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]):
                            tiles[y][x]['features'].append('path')
        
        return paths
        
    def _generate_path(self, start: Dict, end: Dict, tiles: List[List[Dict]]) -> List[Tuple[int, int]]:
        """Generate a path between two points using A* pathfinding"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.world.width and 0 <= ny < self.world.height and
                    tiles[ny][nx]['walkable']):
                    neighbors.append((nx, ny))
            return neighbors
            
        # A* pathfinding
        start_pos = (start['x'], start['y'])
        end_pos = (end['x'], end['y'])
        
        frontier = [(0, start_pos)]
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}
        
        while frontier:
            current = frontier.pop(0)[1]
            
            if current == end_pos:
                break
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(end_pos, next_pos)
                    frontier.append((priority, next_pos))
                    frontier.sort()
                    came_from[next_pos] = current
                    
        # Reconstruct path
        if end_pos not in came_from:
            return None
            
        path = []
        current = end_pos
        while current != start_pos:
            path.append(current)
            current = came_from[current]
        path.append(start_pos)
        path.reverse()
        
        return path
        
    def _generate_poi_name(self, poi_type: str) -> str:
        """Generate a name for a point of interest"""
        prefixes = {
            'village': ['Green', 'River', 'Hill', 'Lake', 'Sun'],
            'cave': ['Dark', 'Deep', 'Crystal', 'Shadow', 'Echo'],
            'ruins': ['Ancient', 'Lost', 'Forgotten', 'Hidden', 'Mystic'],
            'mine': ['Iron', 'Gold', 'Silver', 'Copper', 'Crystal'],
            'oasis': ['Palm', 'Desert', 'Spring', 'Moon', 'Star'],
            'pyramid': ['Sun', 'Moon', 'Star', 'Sand', 'Golden'],
            'peak': ['Cloud', 'Storm', 'Thunder', 'Snow', 'Ice']
        }
        
        suffixes = {
            'village': ['Village', 'Town', 'Settlement', 'Haven', 'Rest'],
            'cave': ['Cave', 'Cavern', 'Grotto', 'Hollow', 'Den'],
            'ruins': ['Ruins', 'Remains', 'Remnants', 'Stones', 'Pillars'],
            'mine': ['Mine', 'Depths', 'Dig', 'Shaft', 'Quarry'],
            'oasis': ['Oasis', 'Spring', 'Pool', 'Waters', 'Garden'],
            'pyramid': ['Pyramid', 'Temple', 'Tomb', 'Spire', 'Monument'],
            'peak': ['Peak', 'Summit', 'Top', 'Spire', 'Point']
        }
        
        prefix = random.choice(prefixes.get(poi_type, prefixes['village']))
        suffix = random.choice(suffixes.get(poi_type, suffixes['village']))
        
        return f"{prefix} {suffix}"

    def generate_plants(self, num_plants):
        """Generate initial plants across the world"""
        try:
            print(f"Spawning {num_plants} plants...")
            for _ in range(num_plants):
                # Get random position
                x = random.randint(0, self.world.width - 1)
                y = random.randint(0, self.world.height - 1)
                
                # Get tile at position
                tile = self.world.get_tile(x, y)
                if not tile or 'biome' not in tile:
                    continue
                    
                biome = tile['biome']
                if biome not in BIOMES:
                    continue
                    
                # Get valid plant types for this biome
                valid_plants = []
                for plant_type in BIOMES[biome]:
                    if plant_type in ENTITY_TYPES:
                        valid_plants.append(plant_type)
                        
                # Add flower types if biome supports flowers
                if biome in RESOURCE_TYPES.get('flower', {}).get('biomes', []):
                    flower_types = RESOURCE_TYPES['flower']['types']
                    valid_plants.extend([ft for ft in flower_types if ft in ENTITY_TYPES])
                
                if not valid_plants:
                    continue
                    
                # Select plant type based on biome and elevation
                elevation = self.terrain_generator.get_elevation(x, y)
                
                # Get possible plant types based on elevation
                possible_plants = []
                for plant in valid_plants:
                    # Check if plant has resource type rules
                    resource_info = RESOURCE_TYPES.get(plant)
                    if resource_info:
                        if resource_info['biomes'] == ['all'] or biome in resource_info['biomes']:
                            if resource_info['min_elevation'] <= elevation <= resource_info['max_elevation']:
                                possible_plants.append(plant)
                    # If plant is a flower type
                    elif plant in RESOURCE_TYPES['flower']['types']:
                        if (RESOURCE_TYPES['flower']['min_elevation'] <= elevation <= 
                            RESOURCE_TYPES['flower']['max_elevation']):
                            possible_plants.append(plant)
                    else:
                        possible_plants.append(plant)  # If no resource info, always allow
                
                if not possible_plants:
                    continue
                    
                # Select random plant type and create plant
                plant_type = random.choice(possible_plants)
                
                # Add slight position variation
                x = x + random.uniform(-0.4, 0.4)
                y = y + random.uniform(-0.4, 0.4)
                
                try:
                    if self.world:
                        plant = Plant(self.world, x, y, plant_type)
                        self.world.add_entity(plant)
                        print(f"Created plant: {plant_type} at ({x}, {y})")
                except Exception as e:
                    print(f"Error creating plant: {e}")
                    
        except Exception as e:
            print(f"Error generating plants: {e}")
            import traceback
            traceback.print_exc()

    def _add_resources_to_chunk(self, chunk_data, chunk_x, chunk_y):
        """Add resources to a chunk based on biome"""
        try:
            # Convert chunk coordinates to world coordinates
            base_x = chunk_x * CHUNK_SIZE * TILE_SIZE
            base_y = chunk_y * CHUNK_SIZE * TILE_SIZE
            
            # Iterate through each tile in the chunk
            for local_y in range(CHUNK_SIZE):
                for local_x in range(CHUNK_SIZE):
                    tile_key = (local_x, local_y)
                    if tile_key not in chunk_data:
                        continue
                        
                    tile = chunk_data[tile_key]
                    if not isinstance(tile, dict) or 'biome' not in tile:
                        continue
                        
                    # Calculate world coordinates for this tile
                    world_x = base_x + local_x * TILE_SIZE
                    world_y = base_y + local_y * TILE_SIZE
                    
                    # Add vegetation based on biome
                    if tile['biome'] in BIOMES:
                        if random.random() < 0.1:  # 10% chance for vegetation
                            valid_plants = [p for p in BIOMES[tile['biome']] 
                                          if p in ENTITY_TYPES]
                            if valid_plants:
                                plant_type = random.choice(valid_plants)
                                if self.world:
                                    plant = Plant(self.world, float(world_x), float(world_y), plant_type)
                                    self.world.add_entity(plant)
                
        except Exception as e:
            print(f"Error adding resources to chunk: {e}")
            import traceback
            traceback.print_exc()

    def _generate_noise_map(self, noise_type: str) -> List[List[float]]:
        """Generate a noise map for the given type (elevation, moisture, temperature)"""
        noise_map = []
        settings = self.terrain_generator.noise_settings[noise_type]
        
        for y in range(self.world.height):
            row = []
            for x in range(self.world.width):
                # Generate noise value using multiple octaves
                value = 0
                amplitude = 1.0
                frequency = 1.0
                max_value = 0
                
                for _ in range(settings['octaves']):
                    nx = x * frequency / settings['scale']
                    ny = y * frequency / settings['scale']
                    value += noise.pnoise2(
                        nx,
                        ny,
                        octaves=1,
                        persistence=settings['persistence'],
                        lacunarity=settings['lacunarity'],
                        base=settings['base']
                    ) * amplitude
                    max_value += amplitude
                    amplitude *= settings['persistence']
                    frequency *= settings['lacunarity']
                
                # Normalize to [0,1]
                value = (value / max_value + 1) / 2
                row.append(value)
            noise_map.append(row)
            
        return noise_map

    def generate_terrain(self) -> bool:
        """Generate initial terrain chunks"""
        try:
            print("Generating initial terrain...")
            
            # Calculate center chunk coordinates
            center_x = self.world.width // (2 * CHUNK_SIZE * TILE_SIZE)
            center_y = self.world.height // (2 * CHUNK_SIZE * TILE_SIZE)
            
            # Generate initial 3x3 grid of chunks around center
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    chunk_x = center_x + dx
                    chunk_y = center_y + dy
                    
                    print(f"Generating chunk at ({chunk_x}, {chunk_y})")
                    chunk = self.terrain_generator.generate_chunk(chunk_x, chunk_y)
                    if chunk:
                        self.world.chunks[(chunk_x, chunk_y)] = chunk
                    else:
                        print(f"Failed to generate chunk at ({chunk_x}, {chunk_y})")
                        return False
                        
            print("Initial terrain generation complete")
            return True
            
        except Exception as e:
            print(f"Error generating terrain: {e}")
            traceback.print_exc()
            return False

    def _generate_chunk(self, chunk_x: int, chunk_y: int) -> Optional[Dict]:
        """Generate a single chunk"""
        try:
            return self.terrain_generator.generate_chunk(chunk_x, chunk_y)
        except Exception as e:
            print(f"Error generating chunk at ({chunk_x}, {chunk_y}): {e}")
            traceback.print_exc()
            return None