import pygame
import random
import traceback
import math
from typing import Dict, List, Optional, Tuple
from ...constants import (
    BIOMES, BIOME_VEGETATION, UI_COLORS, CHUNK_SIZE, TILE_SIZE,
    RESOURCE_TYPES, WEATHER_TYPES, SEASONS
)
from .perlin import Perlin

class TerrainGenerator:
    def __init__(self, seed: Optional[int] = None, world=None):
        """Initialize the terrain generator"""
        self.seed = seed or random.randint(0, 999999)
        self.world = world
        
        # Initialize noise generators with different seeds for variety
        self.elevation_noise = Perlin(seed=self.seed)
        self.moisture_noise = Perlin(seed=self.seed + 1)
        self.temperature_noise = Perlin(seed=self.seed + 2)
        self.feature_noise = Perlin(seed=self.seed + 3)
        
        # Noise scale factors - adjusted for more interesting terrain
        self.noise_scale = {
            'elevation': 100.0,  # Larger scale for smoother elevation changes
            'moisture': 150.0,   # Larger scale for broader biome regions
            'temperature': 200.0,  # Largest scale for climate zones
            'feature': 50.0     # Small scale for local terrain features
        }
        
        # Biome thresholds - adjusted for better biome distribution
        self.biome_thresholds = {
            'elevation': {
                'deep_water': 0.2,
                'shallow_water': 0.4,
                'beach': 0.45,
                'lowland': 0.6,
                'highland': 0.8,
                'mountain': 1.0
            },
            'moisture': {
                'arid': 0.2,
                'dry': 0.4,
                'normal': 0.6,
                'wet': 0.8,
                'saturated': 1.0
            },
            'temperature': {
                'freezing': 0.2,
                'cold': 0.4,
                'mild': 0.6,
                'warm': 0.8,
                'hot': 1.0
            }
        }
        
        # Cache for generated chunks
        self.chunk_cache = {}
        self.chunk_size = CHUNK_SIZE
        
        # Resource generation settings
        self.resource_settings = {
            'tree': {'density': 0.1, 'min_elevation': 0.45},
            'rock': {'density': 0.05, 'min_elevation': 0.5},
            'bush': {'density': 0.15, 'min_elevation': 0.45},
            'grass': {'density': 0.3, 'min_elevation': 0.45},
            'flower': {'density': 0.08, 'min_elevation': 0.45}
        }
        
        random.seed(self.seed)
        
    def generate_chunk(self, chunk_x: int, chunk_y: int) -> Optional[Dict]:
        """Generate a new terrain chunk or get from cache"""
        try:
            # Check cache first
            chunk_key = (chunk_x, chunk_y)
            if chunk_key in self.chunk_cache:
                return self.chunk_cache[chunk_key]
            
            # Generate base noise maps
            elevation = self._generate_noise_map(chunk_x, chunk_y, 'elevation')
            moisture = self._generate_noise_map(chunk_x, chunk_y, 'moisture')
            temperature = self._generate_noise_map(chunk_x, chunk_y, 'temperature')
            feature = self._generate_noise_map(chunk_x, chunk_y, 'feature')
            
            # Initialize maps
            heightmap = [[0.0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
            biome_map = [['' for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
            resource_map = [[[] for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
            
            # Generate terrain for each tile
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    # Get base noise values
                    e = elevation[y][x]
                    m = moisture[y][x]
                    t = temperature[y][x]
                    f = feature[y][x]
                    
                    # Apply feature noise to elevation
                    e = e * 0.8 + f * 0.2
                    
                    # Store height
                    heightmap[y][x] = e
                    
                    # Determine biome
                    biome = self._determine_biome(e, m, t)
                    biome_map[y][x] = biome
                    
                    # Generate resources based on biome and noise
                    resources = self._generate_resources(biome, e, m, t)
                    resource_map[y][x] = resources
            
            # Create chunk data
            chunk_data = {
                'position': (chunk_x, chunk_y),
                'heightmap': heightmap,
                'biome_map': biome_map,
                'resource_map': resource_map,
                'elevation': elevation,
                'moisture': moisture,
                'temperature': temperature,
                'feature': feature
            }
            
            # Cache the chunk
            self.chunk_cache[chunk_key] = chunk_data
            return chunk_data
            
        except Exception as e:
            print(f"Error generating chunk at ({chunk_x}, {chunk_y}): {e}")
            traceback.print_exc()
            return None
            
    def _generate_noise_map(self, chunk_x: int, chunk_y: int, noise_type: str) -> List[List[float]]:
        """Generate a noise map for a chunk"""
        try:
            noise_map = [[0.0 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
            noise_gen = getattr(self, f'{noise_type}_noise')
            scale = self.noise_scale[noise_type]
            
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    # Calculate world coordinates
                    world_x = (chunk_x * CHUNK_SIZE + x) / scale
                    world_y = (chunk_y * CHUNK_SIZE + y) / scale
                    
                    # Generate base noise
                    value = noise_gen.noise2d(world_x, world_y)
                    
                    # Normalize to 0-1 range
                    value = (value + 1) * 0.5
                    
                    # Apply type-specific modifications
                    if noise_type == 'elevation':
                        # Add some variation to make terrain more interesting
                        value = value * 0.8 + abs(noise_gen.noise2d(world_x * 2, world_y * 2)) * 0.2
                    elif noise_type == 'moisture':
                        # Smooth out moisture transitions
                        value = value * 0.7 + 0.3
                    elif noise_type == 'temperature':
                        # Add latitude-based temperature variation
                        latitude_factor = abs(chunk_y) / (self.world.height / 2)
                        value = value * 0.6 + (1 - latitude_factor) * 0.4
                    
                    noise_map[y][x] = max(0.0, min(1.0, value))
                    
            return noise_map
            
        except Exception as e:
            print(f"Error generating noise map: {e}")
            traceback.print_exc()
            return [[0.5 for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

    def _get_latitude_temperature(self, world_y: int) -> float:
        """Calculate temperature modifier based on latitude"""
        # Normalize y coordinate to -1 to 1 range
        latitude = (world_y / (CHUNK_SIZE * 100)) * 2 - 1
        # Temperature decreases towards poles
        return 1.0 - abs(latitude)

    def _determine_biome(self, elevation: float, moisture: float, temperature: float) -> str:
        """Determine biome type based on environmental factors"""
        try:
            # Get biome thresholds
            elev = self.biome_thresholds['elevation']
            moist = self.biome_thresholds['moisture']
            temp = self.biome_thresholds['temperature']
            
            # Determine basic terrain type based on elevation
            if elevation < elev['deep_water']:
                return 'deep_ocean'
            elif elevation < elev['shallow_water']:
                return 'ocean'
            elif elevation < elev['beach']:
                return 'beach'
            
            # For land biomes, consider moisture and temperature
            if elevation < elev['lowland']:
                if temperature < temp['cold']:
                    if moisture < moist['dry']:
                        return 'tundra'
                    else:
                        return 'snowy_plains'
                elif temperature < temp['mild']:
                    if moisture < moist['dry']:
                        return 'plains'
                    elif moisture < moist['wet']:
                        return 'forest'
                    else:
                        return 'rainforest'
                else:
                    if moisture < moist['dry']:
                        return 'desert'
                    elif moisture < moist['wet']:
                        return 'savanna'
                    else:
                        return 'jungle'
            
            # Highland biomes
            elif elevation < elev['highland']:
                if temperature < temp['cold']:
                    return 'snowy_mountains'
                elif moisture < moist['dry']:
                    return 'hills'
                else:
                    return 'forest_hills'
            
            # Mountain biomes
            else:
                if temperature < temp['cold']:
                    return 'snowy_peaks'
                else:
                    return 'mountains'
                    
        except Exception as e:
            print(f"Error determining biome: {e}")
            return 'plains'  # Default biome on error
            
    def _apply_biome_colors(self, base_color: Tuple[int, int, int], biome: str,
                           moisture: float, temperature: float) -> Tuple[int, int, int]:
        """Apply environmental factors to biome colors"""
        try:
            # Adjust for moisture (darker when wet)
            moisture_factor = 0.8 + (moisture * 0.4)
            
            # Adjust for temperature (warmer colors in high temp)
            temp_factor = 0.8 + (temperature * 0.4)
            
            # Add time of day influence (not implemented yet)
            time_factor = 1.0
            
            # Calculate final color with improved blending
            r = int(base_color[0] * moisture_factor * temp_factor * time_factor)
            g = int(base_color[1] * moisture_factor * time_factor)
            b = int(base_color[2] * moisture_factor * time_factor)
            
            return (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b))
            )
            
        except Exception as e:
            print(f"Error applying biome colors: {e}")
            traceback.print_exc()
            return base_color
            
    def _add_tile_variation(self, tile_data):
        """Add visual variation to tiles"""
        try:
            # Add height variation
            tile_data['height_offset'] = random.uniform(-0.1, 0.1)
            
            # Add color variation based on biome
            if tile_data['biome'] in BIOMES:
                base_color = BIOMES[tile_data['biome']]['color']
                variation = random.uniform(0.9, 1.1)
                tile_data['color'] = tuple(
                    min(255, max(0, int(c * variation)))
                    for c in base_color
                )
                
            # Add fertility variation
            base_fertility = BIOMES.get(tile_data['biome'], {}).get('base_fertility', 0.5)
            tile_data['fertility'] = min(1.0, max(0.0, base_fertility + random.uniform(-0.1, 0.1)))
            
            # Add moisture retention
            base_moisture = BIOMES.get(tile_data['biome'], {}).get('moisture_retention', 0.5)
            tile_data['moisture_retention'] = min(1.0, max(0.0, base_moisture + random.uniform(-0.1, 0.1)))
            
        except Exception as e:
            print(f"Error adding tile variation: {e}")
            
    def _add_features_to_chunk(self, chunk_data):
        """Add biome-specific features to chunk"""
        try:
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile = chunk_data['tiles'][y][x]
                    if not tile or not tile['walkable']:
                        continue
                        
                    # 10% chance to add a feature
                    if random.random() < 0.1:
                        feature = self._generate_biome_feature(
                            tile['biome'],
                            x + chunk_data['position'][0] * CHUNK_SIZE,
                            y + chunk_data['position'][1] * CHUNK_SIZE
                        )
                        if feature:
                            tile['features'].append(feature)
                            
        except Exception as e:
            print(f"Error adding features to chunk: {e}")
            
    def _add_resources_to_chunk(self, chunk_data):
        """Add resources to chunk based on biome"""
        try:
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile = chunk_data['tiles'][y][x]
                    if not tile or not tile['walkable']:
                        continue
                        
                    # Check each resource type
                    for resource_type, settings in self.resource_settings.items():
                        # Skip if resource not allowed in this biome
                        if not self._is_resource_allowed(resource_type, tile['biome']):
                            continue
                            
                        # Check density threshold
                        if random.random() < settings['density']:
                            resource = self._generate_resource(
                                resource_type,
                                x + chunk_data['position'][0] * CHUNK_SIZE,
                                y + chunk_data['position'][1] * CHUNK_SIZE
                            )
                            if resource:
                                tile['resources'].append(resource)
                                
        except Exception as e:
            print(f"Error adding resources to chunk: {e}")
            
    def _generate_biome_feature(self, biome: str, x: int, y: int) -> Optional[Dict]:
        """Generate a biome-specific feature"""
        try:
            if biome not in BIOMES:
                return None
                
            feature_types = {
                'mountains': ['rock_formation', 'cave_entrance'],
                'forest': ['fallen_log', 'mushroom_circle', 'berry_bush'],
                'desert': ['cactus', 'sand_dune', 'oasis'],
                'swamp': ['mud_pool', 'vine_cluster'],
                'tundra': ['ice_formation', 'snow_drift'],
                'plains': ['tall_grass', 'flower_patch'],
                'beach': ['seashells', 'driftwood'],
                'rainforest': ['vine_canopy', 'exotic_flower']
            }
            
            if biome in feature_types:
                feature_type = random.choice(feature_types[biome])
                return {
                    'type': feature_type,
                    'x': x,
                    'y': y,
                    'size': random.uniform(0.5, 1.5),
                    'variation': random.uniform(0.8, 1.2),
                    'properties': {}  # Additional properties can be added based on feature type
                }
                
            return None
            
        except Exception as e:
            print(f"Error generating biome feature: {e}")
            return None
            
    def _generate_resource(self, resource_type: str, x: int, y: int) -> Optional[Dict]:
        """Generate a resource with properties"""
        try:
            base_properties = {
                'tree': {
                    'quantity': random.randint(50, 100),
                    'regrowth_rate': 0.1,
                    'hardness': 1.0,
                    'resource_type': 'wood'
                },
                'rock': {
                    'quantity': random.randint(30, 70),
                    'hardness': 2.0,
                    'resource_type': 'stone'
                },
                'bush': {
                    'quantity': random.randint(20, 40),
                    'regrowth_rate': 0.2,
                    'resource_type': 'berries'
                },
                'grass': {
                    'quantity': random.randint(10, 30),
                    'regrowth_rate': 0.3,
                    'resource_type': 'fiber'
                },
                'flower': {
                    'quantity': random.randint(5, 15),
                    'regrowth_rate': 0.15,
                    'resource_type': 'herbs'
                }
            }
            
            if resource_type in base_properties:
                properties = base_properties[resource_type].copy()
                properties.update({
                    'x': x,
                    'y': y,
                    'state': 'normal',
                    'last_interaction': 0,
                    'size': random.uniform(0.8, 1.2)
                })
                return {
                    'type': resource_type,
                    'properties': properties
                }
                
            return None
            
        except Exception as e:
            print(f"Error generating resource: {e}")
            return None
            
    def _is_resource_allowed(self, resource_type: str, biome: str) -> bool:
        """Check if resource is allowed in biome"""
        try:
            # Define biome-specific resource restrictions
            allowed_resources = {
                'ocean': ['fish'],
                'beach': ['rock', 'seashell'],
                'desert': ['rock', 'cactus'],
                'tundra': ['rock'],
                'mountains': ['rock', 'ore'],
                'forest': ['tree', 'bush', 'flower', 'grass'],
                'rainforest': ['tree', 'bush', 'flower', 'grass', 'vine'],
                'plains': ['grass', 'flower', 'bush'],
                'swamp': ['tree', 'grass', 'mushroom']
            }
            
            if biome in allowed_resources:
                return resource_type in allowed_resources[biome]
            return True  # Allow all resources in undefined biomes
            
        except Exception as e:
            print(f"Error checking resource allowance: {e}")
            return False
            
    def clear_cache(self):
        """Clear the chunk cache"""
        self.chunk_cache.clear()

    def _generate_resources(self, biome_name: str, elevation: float, moisture: float, temperature: float) -> List[Dict]:
        """Generate resources for a tile based on biome and conditions"""
        try:
            resources = []
            
            # Skip resource generation for water tiles
            if biome_name in ['deep_ocean', 'ocean']:
                if random.random() < 0.1:  # 10% chance for fish
                    resources.append({
                        'type': 'fish',
                        'variant': 'default',
                        'properties': RESOURCE_TYPES['fish'].copy()
                    })
                return resources
                
            # Skip if elevation too low
            if elevation < self.biome_thresholds['elevation']['beach']:
                return resources
                
            # Define biome-specific resource chances
            biome_resources = {
                'beach': {
                    'seashell': 0.2,
                    'rock': 0.1
                },
                'tundra': {
                    'rock': 0.15,
                    'grass': 0.1
                },
                'snowy_plains': {
                    'grass': 0.2,
                    'rock': 0.1
                },
                'plains': {
                    'grass': 0.4,
                    'flower': 0.2,
                    'bush': 0.1
                },
                'forest': {
                    'tree': 0.3,
                    'bush': 0.2,
                    'grass': 0.3,
                    'flower': 0.15
                },
                'rainforest': {
                    'tree': 0.4,
                    'bush': 0.3,
                    'grass': 0.2,
                    'flower': 0.2
                },
                'desert': {
                    'rock': 0.2,
                    'grass': 0.05
                },
                'savanna': {
                    'grass': 0.3,
                    'tree': 0.1,
                    'bush': 0.15
                },
                'jungle': {
                    'tree': 0.4,
                    'bush': 0.3,
                    'grass': 0.2,
                    'flower': 0.2
                }
            }
            
            # Get resource chances for this biome
            biome_chances = biome_resources.get(biome_name, {})
            
            # Check each possible resource for this biome
            for resource_type, base_chance in biome_chances.items():
                if resource_type not in RESOURCE_TYPES:
                    continue
                    
                settings = self.resource_settings.get(resource_type, {})
                if elevation < settings.get('min_elevation', 0):
                    continue
                    
                # Calculate final chance
                chance = base_chance * settings.get('density', 1.0)
                
                # Apply environmental modifiers
                if resource_type == 'tree':
                    chance *= moisture  # More trees in wet areas
                elif resource_type == 'grass':
                    chance *= moisture * 1.5  # Much more grass in wet areas
                elif resource_type == 'flower':
                    chance *= temperature  # More flowers in warm areas
                elif resource_type == 'rock':
                    chance *= (1 + elevation)  # More rocks at higher elevations
                    
                # Random check
                if random.random() < chance:
                    resource_data = {
                        'type': resource_type,
                        'variant': 'default',
                        'properties': RESOURCE_TYPES[resource_type].copy()
                    }
                    
                    # Add position-based variation
                    resource_data['properties']['size'] = random.uniform(0.8, 1.2)
                    resource_data['properties']['quality'] = random.uniform(0.7, 1.0)
                    
                    resources.append(resource_data)
            
            return resources
            
        except Exception as e:
            print(f"Error generating resources: {e}")
            traceback.print_exc()
            return [] 