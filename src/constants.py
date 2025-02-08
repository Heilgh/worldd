"""Game constants and configuration"""
import os
import pygame
import math
from typing import Dict, List, Tuple, Callable

# Initialize pygame for font support
pygame.init()
if not pygame.font.get_init():
    pygame.font.init()

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "World Simulation"
DISPLAY_FLAGS = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED

# Performance settings
TARGET_FPS = 60
FRAME_LENGTH = 1.0 / TARGET_FPS
VSYNC = True

# World dimensions
WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000
CHUNK_SIZE = 32
TILE_SIZE = 32
WORLD_CHUNKS_X = WORLD_WIDTH // (CHUNK_SIZE * TILE_SIZE)
WORLD_CHUNKS_Y = WORLD_HEIGHT // (CHUNK_SIZE * TILE_SIZE)

# Time system constants
TIME_SCALE = 60.0  # 1 second real time = 60 seconds game time
SEASON_LENGTH = 30  # Days per season
DAY_LENGTH = 1440  # Seconds per day (24 minutes real time)

# Time speeds
TIME_SPEEDS = {
    'paused': 0.0,
    'slow': 0.5,
    'normal': 1.0,
    'fast': 2.0,
    'ultra': 5.0
}

# World dimensions
WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000
CHUNK_SIZE = 32
TILE_SIZE = 32
WORLD_CHUNKS_X = WORLD_WIDTH // (CHUNK_SIZE * TILE_SIZE)
WORLD_CHUNKS_Y = WORLD_HEIGHT // (CHUNK_SIZE * TILE_SIZE)

# Seasons and their properties
SEASONS = {
    'spring': {
        'base_temp': 15,
        'growth_mod': 1.2,
        'precipitation': 0.6,
        'day_length': 12,
        'color': (124, 252, 0)
    },
    'summer': {
        'base_temp': 25,
        'growth_mod': 1.0,
        'precipitation': 0.3,
        'day_length': 14,
        'color': (255, 255, 0)
    },
    'autumn': {
        'base_temp': 10,
        'growth_mod': 0.8,
        'precipitation': 0.7,
        'day_length': 10,
        'color': (255, 140, 0)
    },
    'winter': {
        'base_temp': 0,
        'growth_mod': 0.4,
        'precipitation': 0.8,
        'day_length': 8,
        'color': (255, 250, 250)
    }
}

# Weather types and their properties
WEATHER_TYPES = {
    'clear': {
        'description': 'Clear sunny weather',
        'temperature_mod': 5,
        'wind_speed': 0.2,
        'humidity': 0.3,
        'precipitation': 0,
        'darkness': 0,
        'fog': 0,
        'particle_rate': 0,
        'particle_color': None,
        'duration': (1800, 3600),  # 30-60 minutes
        'max_wind': 2.0,
        'possible_seasons': ['spring', 'summer', 'autumn'],
        'probability': 0.4,
        'season_probability_mod': {
            'summer': 1.5,
            'winter': 0.5
        },
        'particle_count': 0,
        'overlay_alpha': 0,
        'status_effects': [],
        'visibility': 1.0,
        'movement_speed': 1.0,
        'entity_effects': {
            'mood': 0.1,  # Slight mood boost
            'energy': 0.05  # Slight energy boost
        },
        'graphics': {
            'sky_color': (135, 206, 235),  # Sky blue
            'cloud_color': (255, 255, 255),
            'sun_intensity': 1.0,
            'shadow_intensity': 1.0,
            'particle_effects': False
        }
    },
    'cloudy': {
        'description': 'Overcast with clouds',
        'temperature_mod': -2,
        'wind_speed': 0.4,
        'humidity': 0.6,
        'precipitation': 0,
        'darkness': 0.2,
        'fog': 0.1,
        'particle_rate': 0,
        'particle_color': None,
        'duration': (1200, 2400),  # 20-40 minutes
        'max_wind': 3.0,
        'possible_seasons': ['spring', 'summer', 'autumn', 'winter'],
        'probability': 0.3,
        'season_probability_mod': {
            'autumn': 1.3,
            'spring': 1.2
        },
        'particle_count': 0,
        'overlay_alpha': 0.2,
        'status_effects': [],
        'visibility': 0.8,
        'movement_speed': 1.0,
        'entity_effects': {
            'mood': -0.05,  # Slight mood decrease
            'energy': 0
        },
        'graphics': {
            'sky_color': (169, 169, 169),  # Dark gray
            'cloud_color': (128, 128, 128),
            'sun_intensity': 0.6,
            'shadow_intensity': 0.7,
            'particle_effects': False
        }
    },
    'rain': {
        'description': 'Steady rainfall',
        'temperature_mod': -5,
        'wind_speed': 0.6,
        'humidity': 0.9,
        'precipitation': 0.5,
        'darkness': 0.4,
        'fog': 0.2,
        'particle_rate': 100,
        'particle_color': (200, 200, 255),
        'duration': (600, 1800),  # 10-30 minutes
        'max_wind': 4.0,
        'possible_seasons': ['spring', 'summer', 'autumn'],
        'probability': 0.2,
        'season_probability_mod': {
            'spring': 1.5,
            'winter': 0.2
        },
        'particle_count': 100,
        'overlay_alpha': 0.4,
        'status_effects': ['wet'],
        'visibility': 0.6,
        'movement_speed': 0.8,
        'entity_effects': {
            'mood': -0.1,  # Mood decrease
            'energy': -0.05  # Slight energy decrease
        },
        'graphics': {
            'sky_color': (105, 105, 105),  # Dim gray
            'cloud_color': (82, 82, 82),
            'sun_intensity': 0.3,
            'shadow_intensity': 0.4,
            'particle_effects': True
        }
    },
    'storm': {
        'description': 'Thunderstorm with heavy rain',
        'temperature_mod': -8,
        'wind_speed': 1.0,
        'humidity': 1.0,
        'precipitation': 1.0,
        'darkness': 0.7,
        'fog': 0.3,
        'particle_rate': 200,
        'particle_color': (180, 180, 255),
        'duration': (300, 900),  # 5-15 minutes
        'max_wind': 8.0,
        'possible_seasons': ['spring', 'summer'],
        'probability': 0.1,
        'season_probability_mod': {
            'summer': 1.3,
            'winter': 0
        },
        'particle_count': 200,
        'overlay_alpha': 0.6,
        'status_effects': ['wet', 'scared'],
        'visibility': 0.3,
        'movement_speed': 0.6,
        'entity_effects': {
            'mood': -0.2,  # Significant mood decrease
            'energy': -0.1  # Energy decrease
        },
        'graphics': {
            'sky_color': (47, 79, 79),  # Dark slate gray
            'cloud_color': (44, 62, 80),
            'sun_intensity': 0.1,
            'shadow_intensity': 0.2,
            'particle_effects': True,
            'lightning': {
                'frequency': 0.1,  # Lightning strikes per second
                'intensity': 1.0,
                'duration': 0.2  # Duration of flash in seconds
            }
        }
    },
    'snow': {
        'description': 'Gentle snowfall',
        'temperature_mod': -10,
        'wind_speed': 0.3,
        'humidity': 0.7,
        'precipitation': 0.4,
        'darkness': 0.3,
        'fog': 0.4,
        'particle_rate': 50,
        'particle_color': (255, 255, 255),
        'duration': (1200, 2400),  # 20-40 minutes
        'max_wind': 2.0,
        'possible_seasons': ['winter'],
        'probability': 0.3,
        'season_probability_mod': {
            'winter': 2.0,
            'summer': 0
        },
        'particle_count': 50,
        'overlay_alpha': 0.3,
        'status_effects': ['cold'],
        'visibility': 0.7,
        'movement_speed': 0.7,
        'entity_effects': {
            'mood': 0.05,  # Slight mood boost (scenic)
            'energy': -0.1  # Energy decrease due to cold
        },
        'graphics': {
            'sky_color': (220, 220, 220),  # Light gray
            'cloud_color': (192, 192, 192),
            'sun_intensity': 0.5,
            'shadow_intensity': 0.6,
            'particle_effects': True
        }
    },
    'blizzard': {
        'description': 'Heavy snowstorm with strong winds',
        'temperature_mod': -15,
        'wind_speed': 0.9,
        'humidity': 0.8,
        'precipitation': 0.8,
        'darkness': 0.6,
        'fog': 0.7,
        'particle_rate': 150,
        'particle_color': (255, 255, 255),
        'duration': (600, 1800),  # 10-30 minutes
        'max_wind': 7.0,
        'possible_seasons': ['winter'],
        'probability': 0.1,
        'season_probability_mod': {
            'winter': 1.5,
            'summer': 0
        },
        'particle_count': 150,
        'overlay_alpha': 0.5,
        'status_effects': ['frozen', 'scared'],
        'visibility': 0.2,
        'movement_speed': 0.4,
        'entity_effects': {
            'mood': -0.2,  # Significant mood decrease
            'energy': -0.2  # Significant energy decrease
        },
        'graphics': {
            'sky_color': (200, 200, 200),  # Light gray
            'cloud_color': (169, 169, 169),
            'sun_intensity': 0.2,
            'shadow_intensity': 0.3,
            'particle_effects': True,
            'wind_effects': {
                'intensity': 1.0,
                'direction_change_rate': 0.2,  # Direction changes per second
                'sound_volume': 0.8
            }
        }
    }
}

# Season order for progression
SEASON_ORDER = ['spring', 'summer', 'autumn', 'winter']

# Weather effects
def rain_effect(screen: pygame.Surface):
    """Draw rain effect"""
    for _ in range(100):
        x = random.randint(0, screen.get_width())
        y = random.randint(0, screen.get_height())
        length = random.randint(5, 15)
        alpha = random.randint(50, 150)
        color = (200, 200, 255, alpha)
        end_pos = (x + length//2, y + length)
        pygame.draw.line(screen, color, (x, y), end_pos, 1)

def snow_effect(screen: pygame.Surface):
    """Draw snow effect"""
    for _ in range(50):
        x = random.randint(0, screen.get_width())
        y = random.randint(0, screen.get_height())
        size = random.randint(2, 4)
        alpha = random.randint(50, 200)
        color = (255, 255, 255, alpha)
        pygame.draw.circle(screen, color, (x, y), size)

# Entity types and their properties
ENTITY_TYPES = {
    'human': {
        'size': TILE_SIZE,
        'speed': 2.0,
        'base_health': 100,
        'base_energy': 100,
        'vision_range': 8,
        'interaction_range': 2,
        'sprite': '👤',
        'specs': {
            'max_health': 100,
            'max_energy': 100,
            'vision_range': 8,
            'interaction_range': 2
        }
    },
    'animal': {
        'size': TILE_SIZE * 0.8,
        'speed': 2.5,
        'base_health': 80,
        'base_energy': 90,
        'vision_range': 6,
        'interaction_range': 1,
        'sprite': '🐾',
        'specs': {
            'max_health': 80,
            'max_energy': 90,
            'vision_range': 6,
            'interaction_range': 1
        }
    },
    'plant': {
        'size': TILE_SIZE * 0.6,
        'speed': 0,
        'base_health': 50,
        'base_energy': 100,
        'vision_range': 0,
        'interaction_range': 1,
        'sprite': '🌱',
        'specs': {
            'max_health': 50,
            'max_energy': 100,
            'vision_range': 0,
            'interaction_range': 1
        }
    }
}

# Entity states and behaviors
ENTITY_STATES = {
    'idle': {
        'description': 'Entity is not actively engaged in any task',
        'animation': 'idle',
        'movement_speed': 1.0,
        'energy_cost': 0.1,
        'thought_types': ['random', 'need', 'social'],
        'duration_range': (5, 15),
        'interruption_chance': 0.8,
        'state_effects': {
            'stress': -0.1,  # Slight stress reduction
            'energy': 0.05  # Slight energy recovery
        },
        'transitions': ['walk', 'work', 'interact', 'rest']
    },
    'walk': {
        'description': 'Entity is moving to a destination',
        'animation': 'walk',
        'movement_speed': 1.2,
        'energy_cost': 0.2,
        'thought_types': ['environment', 'goal', 'social'],
        'duration_range': (10, 30),
        'interruption_chance': 0.4,
        'state_effects': {
            'energy': -0.1,
            'health': 0.05  # Light exercise benefit
        },
        'transitions': ['idle', 'run', 'interact', 'work']
    },
    'run': {
        'description': 'Entity is moving quickly',
        'animation': 'run',
        'movement_speed': 2.0,
        'energy_cost': 0.4,
        'thought_types': ['urgent', 'danger', 'goal'],
        'duration_range': (5, 15),
        'interruption_chance': 0.2,
        'state_effects': {
            'energy': -0.3,
            'health': 0.1,
            'stress': 0.2
        },
        'transitions': ['walk', 'idle', 'rest']
    },
    'work': {
        'description': 'Entity is performing a task',
        'animation': 'work',
        'movement_speed': 0.8,
        'energy_cost': 0.3,
        'thought_types': ['work', 'goal', 'need'],
        'duration_range': (20, 60),
        'interruption_chance': 0.3,
        'state_effects': {
            'energy': -0.2,
            'stress': 0.1,
            'satisfaction': 0.2
        },
        'transitions': ['idle', 'rest', 'interact']
    },
    'rest': {
        'description': 'Entity is recovering energy',
        'animation': 'rest',
        'movement_speed': 0.0,
        'energy_cost': -0.3,  # Negative cost means energy recovery
        'thought_types': ['relaxed', 'memory', 'creative'],
        'duration_range': (30, 120),
        'interruption_chance': 0.5,
        'state_effects': {
            'energy': 0.3,
            'stress': -0.2,
            'health': 0.1
        },
        'transitions': ['idle', 'sleep']
    },
    'sleep': {
        'description': 'Entity is sleeping',
        'animation': 'sleep',
        'movement_speed': 0.0,
        'energy_cost': -0.5,
        'thought_types': ['dream'],
        'duration_range': (240, 480),
        'interruption_chance': 0.1,
        'state_effects': {
            'energy': 0.5,
            'stress': -0.3,
            'health': 0.2,
            'memory': 0.1  # Memory consolidation
        },
        'transitions': ['idle', 'rest']
    },
    'interact': {
        'description': 'Entity is interacting with another entity',
        'animation': 'interact',
        'movement_speed': 0.5,
        'energy_cost': 0.2,
        'thought_types': ['social', 'emotional', 'goal'],
        'duration_range': (10, 30),
        'interruption_chance': 0.4,
        'state_effects': {
            'social': 0.3,
            'stress': -0.1,
            'mood': 0.2
        },
        'transitions': ['idle', 'walk', 'work']
    },
    'craft': {
        'description': 'Entity is crafting items',
        'animation': 'craft',
        'movement_speed': 0.3,
        'energy_cost': 0.3,
        'thought_types': ['work', 'creative', 'goal'],
        'duration_range': (30, 90),
        'interruption_chance': 0.2,
        'state_effects': {
            'energy': -0.2,
            'satisfaction': 0.3,
            'skill': 0.1
        },
        'transitions': ['idle', 'rest', 'work']
    },
    'gather': {
        'description': 'Entity is gathering resources',
        'animation': 'gather',
        'movement_speed': 0.7,
        'energy_cost': 0.25,
        'thought_types': ['work', 'environment', 'goal'],
        'duration_range': (15, 45),
        'interruption_chance': 0.3,
        'state_effects': {
            'energy': -0.2,
            'satisfaction': 0.2,
            'skill': 0.05
        },
        'transitions': ['idle', 'walk', 'rest']
    },
    'fight': {
        'description': 'Entity is engaged in combat',
        'animation': 'fight',
        'movement_speed': 1.5,
        'energy_cost': 0.5,
        'thought_types': ['danger', 'survival', 'emotional'],
        'duration_range': (5, 20),
        'interruption_chance': 0.1,
        'state_effects': {
            'energy': -0.4,
            'stress': 0.4,
            'health': -0.2
        },
        'transitions': ['run', 'idle', 'rest']
    }
}

# Entity needs and their properties
ENTITY_NEEDS = {
    'hunger': {
        'decay_rate': 0.1,  # Units per second
        'critical_threshold': 20,
        'death_threshold': 0,
        'restore_rate': 10,  # Units per food item
        'affects_mood': True,
        'affects_energy': True
    },
    'thirst': {
        'decay_rate': 0.15,
        'critical_threshold': 15,
        'death_threshold': 0,
        'restore_rate': 15,
        'affects_mood': True,
        'affects_energy': True
    },
    'energy': {
        'decay_rate': 0.05,
        'critical_threshold': 10,
        'death_threshold': -1,  # Can't die from lack of energy
        'restore_rate': 5,  # Units per rest action
        'affects_mood': True,
        'affects_speed': True
    },
    'social': {
        'decay_rate': 0.03,
        'critical_threshold': 30,
        'death_threshold': -1,
        'restore_rate': 8,
        'affects_mood': True,
        'affects_productivity': True
    },
    'comfort': {
        'decay_rate': 0.02,
        'critical_threshold': 40,
        'death_threshold': -1,
        'restore_rate': 12,
        'affects_mood': True,
        'affects_rest_quality': True
    }
}

# Resource types
RESOURCE_TYPES = {
    'wood': {
        'max_quantity': 100,
        'respawn_time': 300,
        'tool_required': 'axe',
        'hardness': 2,
        'value': 10,
        'biomes': ['forest', 'rainforest', 'plains', 'swamp'],
        'frequency': 0.3,
        'sprite': 'assets/sprites/resources/wood.png',
        'regeneration_rate': 0.1,
        'growth_rate': 0.05
    },
    'stone': {
        'max_quantity': 50,
        'respawn_time': 600,
        'tool_required': 'pickaxe',
        'hardness': 3,
        'value': 15,
        'biomes': ['mountains', 'hills', 'desert', 'tundra'],
        'frequency': 0.25,
        'sprite': 'assets/sprites/resources/stone.png',
        'regeneration_rate': 0.05
    },
    'ore': {
        'max_quantity': 30,
        'respawn_time': 900,
        'tool_required': 'pickaxe',
        'hardness': 4,
        'value': 25,
        'biomes': ['mountains', 'hills'],
        'frequency': 0.15,
        'sprite': 'assets/sprites/resources/ore.png',
        'regeneration_rate': 0.03
    },
    'herb': {
        'max_quantity': 20,
        'respawn_time': 120,
        'tool_required': None,
        'hardness': 1,
        'value': 8,
        'biomes': ['forest', 'plains', 'hills'],
        'frequency': 0.2,
        'sprite': 'assets/sprites/resources/herb.png',
        'regeneration_rate': 0.15,
        'growth_rate': 0.1
    },
    'berry': {
        'max_quantity': 15,
        'respawn_time': 180,
        'tool_required': None,
        'hardness': 1,
        'value': 5,
        'biomes': ['forest', 'plains', 'hills'],
        'frequency': 0.25,
        'sprite': 'assets/sprites/resources/berry.png',
        'regeneration_rate': 0.2,
        'growth_rate': 0.15
    },
    'mushroom': {
        'max_quantity': 10,
        'respawn_time': 240,
        'tool_required': None,
        'hardness': 1,
        'value': 6,
        'biomes': ['forest', 'swamp'],
        'frequency': 0.2,
        'sprite': 'assets/sprites/resources/mushroom.png',
        'regeneration_rate': 0.25,
        'growth_rate': 0.2
    },
    'fish': {
        'max_quantity': 25,
        'respawn_time': 360,
        'tool_required': 'fishing_rod',
        'hardness': 1,
        'value': 12,
        'biomes': ['ocean', 'river', 'lake'],
        'frequency': 0.3,
        'sprite': 'assets/sprites/resources/fish.png',
        'regeneration_rate': 0.15
    },
    'seashell': {
        'max_quantity': 8,
        'respawn_time': 420,
        'tool_required': None,
        'hardness': 1,
        'value': 3,
        'biomes': ['beach'],
        'frequency': 0.2,
        'sprite': 'assets/sprites/resources/seashell.png',
        'regeneration_rate': 0.1
    },
    'sand': {
        'max_quantity': 40,
        'respawn_time': 300,
        'tool_required': 'shovel',
        'hardness': 1,
        'value': 2
    },
    'ice': {
        'max_quantity': 30,
        'respawn_time': 480,
        'tool_required': 'pickaxe',
        'hardness': 2,
        'value': 4
    },
    'grass': {
        'max_quantity': 20,
        'respawn_time': 60,
        'tool_required': None,
        'hardness': 1,
        'value': 2
    },
    'flower': {
        'max_quantity': 12,
        'respawn_time': 180,
        'tool_required': None,
        'hardness': 1,
        'value': 4
    },
    'fruit': {
        'max_quantity': 15,
        'respawn_time': 240,
        'tool_required': None,
        'hardness': 1,
        'value': 7
    },
    'cactus': {
        'max_quantity': 10,
        'respawn_time': 540,
        'tool_required': 'knife',
        'hardness': 2,
        'value': 5
    }
}

# Biome definitions with complete properties
BIOMES = {
    'ocean': {
        'color': (0, 105, 148),
        'walkable': False,
        'base_fertility': 0.0,
        'moisture_retention': 1.0,
        'temperature_mod': -2,
        'features': ['coral_reef', 'seaweed'],
        'resources': ['fish', 'seashell']
    },
    'frozen_ocean': {
        'color': (200, 230, 255),
        'walkable': True,
        'base_fertility': 0.0,
        'moisture_retention': 0.8,
        'temperature_mod': -10,
        'features': ['ice_sheet'],
        'resources': ['ice']
    },
    'beach': {
        'color': (238, 214, 175),
        'walkable': True,
        'base_fertility': 0.2,
        'moisture_retention': 0.3,
        'temperature_mod': 0,
        'features': ['palm_tree', 'seashells'],
        'resources': ['sand', 'seashell']
    },
    'snowy_beach': {
        'color': (230, 230, 240),
        'walkable': True,
        'base_fertility': 0.1,
        'moisture_retention': 0.4,
        'temperature_mod': -5,
        'features': ['ice_formation'],
        'resources': ['ice', 'sand']
    },
    'mountains': {
        'color': (120, 120, 120),
        'walkable': True,
        'base_fertility': 0.3,
        'moisture_retention': 0.4,
        'temperature_mod': -8,
        'features': ['rock_formation', 'cave'],
        'resources': ['stone', 'ore']
    },
    'snowy_mountains': {
        'color': (200, 200, 210),
        'walkable': True,
        'base_fertility': 0.1,
        'moisture_retention': 0.5,
        'temperature_mod': -12,
        'features': ['ice_cave', 'snow_drift'],
        'resources': ['ice', 'stone']
    },
    'rainforest_mountains': {
        'color': (80, 120, 80),
        'walkable': True,
        'base_fertility': 0.7,
        'moisture_retention': 0.9,
        'temperature_mod': -4,
        'features': ['waterfall', 'vine_covered_rocks'],
        'resources': ['stone', 'herbs']
    },
    'tundra': {
        'color': (221, 221, 228),
        'walkable': True,
        'base_fertility': 0.2,
        'moisture_retention': 0.3,
        'temperature_mod': -10,
        'features': ['frozen_pond', 'snow_drift'],
        'resources': ['ice', 'berry']
    },
    'snowy_forest': {
        'color': (200, 210, 200),
        'walkable': True,
        'base_fertility': 0.4,
        'moisture_retention': 0.6,
        'temperature_mod': -8,
        'features': ['evergreen_tree', 'snow_drift'],
        'resources': ['wood', 'berry']
    },
    'desert': {
        'color': (238, 218, 130),
        'walkable': True,
        'base_fertility': 0.1,
        'moisture_retention': 0.1,
        'temperature_mod': 10,
        'features': ['cactus', 'sand_dune'],
        'resources': ['sand', 'cactus']
    },
    'rainforest': {
        'color': (34, 139, 34),
        'walkable': True,
        'base_fertility': 1.0,
        'moisture_retention': 1.0,
        'temperature_mod': 3,
        'features': ['giant_tree', 'vine_canopy'],
        'resources': ['wood', 'fruit', 'herbs']
    },
    'savanna': {
        'color': (177, 209, 110),
        'walkable': True,
        'base_fertility': 0.5,
        'moisture_retention': 0.3,
        'temperature_mod': 5,
        'features': ['acacia_tree', 'tall_grass'],
        'resources': ['wood', 'grass']
    },
    'plains': {
        'color': (164, 225, 99),
        'walkable': True,
        'base_fertility': 0.7,
        'moisture_retention': 0.4,
        'temperature_mod': 0,
        'features': ['flower_patch', 'tall_grass'],
        'resources': ['grass', 'flower']
    },
    'forest': {
        'color': (34, 139, 34),
        'walkable': True,
        'base_fertility': 0.8,
        'moisture_retention': 0.7,
        'temperature_mod': -2,
        'features': ['tree_cluster', 'mushroom_ring'],
        'resources': ['wood', 'mushroom', 'berry']
    },
    'swamp': {
        'color': (71, 108, 108),
        'walkable': True,
        'base_fertility': 0.6,
        'moisture_retention': 0.9,
        'temperature_mod': -1,
        'features': ['willow_tree', 'mud_pool'],
        'resources': ['wood', 'herb', 'mushroom']
    }
}

# Biome vegetation definitions
BIOME_VEGETATION = {
    'water': ['seaweed', 'coral'],
    'beach': ['palm_trees', 'beach_grass'],
    'mountain': ['mountain_flowers', 'alpine_grass', 'small_trees'],
    'snow': ['snow_grass', 'evergreen_trees'],
    'tundra': ['tundra_grass', 'arctic_flowers', 'small_bushes'],
    'plains': ['tall_grass', 'wildflowers', 'scattered_trees'],
    'forest': ['oak_trees', 'pine_trees', 'mushrooms', 'ferns'],
    'jungle': ['tropical_trees', 'vines', 'exotic_flowers'],
    'desert': ['cactus', 'desert_brush', 'desert_flowers'],
    'savanna': ['acacia_trees', 'savanna_grass', 'thorny_bushes']
}

# Initialize pygame font system
pygame.font.init()

# Font definitions with proper Font objects
FONTS = {
    'title': pygame.font.Font(None, 48),  # Large title font
    'subtitle': pygame.font.Font(None, 36),  # Subtitle font
    'normal': pygame.font.Font(None, 24),  # Normal text
    'small': pygame.font.Font(None, 18),  # Small text
    'tiny': pygame.font.Font(None, 14),  # Tiny text for details
    'ui': pygame.font.Font(None, 20),  # UI elements
    'button': pygame.font.Font(None, 22),  # Button text
    'debug': pygame.font.Font(None, 16),  # Debug information
    'emoji': pygame.font.Font(None, 24)  # For emoji characters
}

# Font styles for different text types
FONT_STYLES = {
    'title': {
        'shadow_offset': 2,
        'glow_radius': 10,
        'outline_width': 2
    },
    'normal': {
        'shadow_offset': 1,
        'glow_radius': 5,
        'outline_width': 1
    },
    'ui': {
        'shadow_offset': 1,
        'glow_radius': 3,
        'outline_width': 1
    }
}

# UI Colors
UI_COLORS = {
    # Panel colors
    'panel_bg': (30, 30, 40, 180),  # Dark blue-gray with transparency
    'panel_border': (60, 60, 80),  # Lighter blue-gray
    'panel_glow': (100, 150, 255, 30),  # Soft blue glow
    'panel_header': (40, 40, 50),  # Slightly lighter than background
    
    # Text colors
    'text_normal': (220, 220, 220),  # Light gray
    'text_highlight': (255, 255, 255),  # Pure white
    'text_dim': (150, 150, 150),  # Dimmed text
    'text_warning': (255, 200, 0),  # Yellow warning
    'text_error': (255, 80, 80),  # Red error
    'text_success': (100, 255, 100),  # Green success
    
    # Button colors
    'button_bg': (60, 60, 80),  # Base button color
    'button_hover': (80, 80, 100),  # Lighter when hovered
    'button_active': (100, 100, 120),  # Even lighter when pressed
    'button_disabled': (40, 40, 50),  # Darker when disabled
    'button_text': (220, 220, 220),  # Button text color
    'button_glow': (100, 150, 255, 30),  # Button glow effect
    
    # Slider colors
    'slider_track': (40, 40, 50),  # Slider background
    'slider_track_hover': (50, 50, 60),  # Slider background when hovered
    'slider_fill': (100, 150, 255),  # Filled portion of slider
    'text_normal': (200, 200, 200),
    'text_highlight': (255, 255, 255),
    'text_dark': (100, 100, 100),
    'panel_bg': (40, 44, 52, 200),  # Dark background with some transparency
    'panel_border': (61, 66, 77),
    'button_bg': (60, 60, 60),
    'button_hover': (80, 80, 80),
    'button_active': (100, 100, 100),
    'minimap_bg': (30, 30, 30),
    'minimap_water': (64, 128, 255),
    'minimap_grass': (64, 200, 64),
    'minimap_forest': (32, 160, 32),
    'minimap_mountain': (160, 160, 160),
    'minimap_desert': (224, 192, 96),
    'minimap_snow': (224, 224, 224),
    'minimap_unknown': (50, 50, 50),
    'minimap_entity': (255, 200, 150),
    'minimap_player': (255, 255, 0),
    'minimap_viewport': (255, 255, 255),
    'panel_bg': (40, 44, 52, 200),  # Dark background with some transparency
    'panel_border': (61, 66, 77),
    'panel_glow': (229, 192, 123, 40),  # Semi-transparent gold glow for panels
    'text_normal': (171, 178, 191),  # Light gray text
    'text_highlight': (229, 192, 123),  # Gold highlight
    'text_error': (224, 108, 117),  # Soft red for errors
    'text_dim': (120, 125, 135),  # Dimmed text
    'text_shadow': (0, 0, 0, 160),  # Semi-transparent black for text shadows
    'text_outline': (0, 0, 0),  # Black for text outlines
    'text_glow': (229, 192, 123, 40),  # Semi-transparent gold for text glow
    'title_text': (229, 192, 123),  # Gold color for title text
    'title_shadow': (0, 0, 0, 180),  # Darker shadow for title text
    'title_glow': (229, 192, 123, 60),  # Stronger gold glow for title
    'background': (30, 33, 39),  # Dark background color
    'button_bg': (55, 59, 69),
    'button_hover': (71, 77, 89),
    'button_active': (82, 89, 103),
    'button_normal': (55, 59, 69),  # Same as button_bg
    'button_pressed': (45, 49, 57),  # Darker when pressed
    'button_disabled': (40, 43, 51),  # Even darker when disabled
    'button_border': (61, 66, 77),  # Same as panel_border
    'button_text': (171, 178, 191),  # Same as text_normal
    'button_glow': (229, 192, 123, 40),  # Semi-transparent gold glow
    'glow': (229, 192, 123),  # Gold color for glowing effects
    'shadow': (0, 0, 0, 60),  # Semi-transparent black for shadows
    'progress_bar': (40, 44, 52),  # Dark background matching panel_bg
    'progress_bar_background': (30, 33, 39, 200),  # Slightly darker than progress_bar
    'progress_bar_fill': (229, 192, 123),  # Gold color matching text_highlight
    'progress_bar_border': (61, 66, 77),  # Matching panel_border
    'progress_bar_glow': (229, 192, 123, 40),  # Semi-transparent gold matching button_glow
    'progress_bar_shine': (255, 255, 255, 30),  # Semi-transparent white for shine effect
    'progress_bar_pulse': (229, 192, 123, 40),  # Semi-transparent gold for pulse effect
    'input_bg': (30, 33, 39),
    'input_border': (61, 66, 77),
    'scrollbar_bg': (30, 33, 39),
    'scrollbar_fg': (61, 66, 77),
    'tooltip_bg': (40, 44, 52, 230),
    'tooltip_border': (61, 66, 77)
}

# Enhanced button styles with maximum visual quality
BUTTON_STYLES = {
    'normal': {
        'bg_color': UI_COLORS['button_normal'],
        'border_color': UI_COLORS['button_border'],
        'text_color': UI_COLORS['text_normal'],
        'glow_color': UI_COLORS['button_glow'],
        'shadow_color': UI_COLORS['shadow'],
        'border_width': 2,
        'border_radius': 10,
        'padding': 10,
        'font': FONTS['normal'],
        'shadow_offset': 2,
        'glow_radius': 10,
        'transition_speed': 0.2,
        'pulse_effect': True
    },
    'hover': {
        'bg_color': UI_COLORS['button_hover'],
        'border_color': UI_COLORS['button_border'],
        'text_color': UI_COLORS['text_highlight'],
        'glow_color': (*UI_COLORS['button_glow'][:3], 60),
        'shadow_color': UI_COLORS['shadow'],
        'border_width': 2,
        'border_radius': 10,
        'padding': 10,
        'font': FONTS['normal'],
        'shadow_offset': 3,
        'glow_radius': 15,
        'transition_speed': 0.15,
        'pulse_effect': True
    },
    'pressed': {
        'bg_color': UI_COLORS['button_pressed'],
        'border_color': UI_COLORS['button_border'],
        'text_color': UI_COLORS['text_normal'],
        'glow_color': (*UI_COLORS['button_glow'][:3], 20),
        'shadow_color': UI_COLORS['shadow'],
        'border_width': 2,
        'border_radius': 10,
        'padding': 10,
        'font': FONTS['normal'],
        'shadow_offset': 1,
        'glow_radius': 5,
        'transition_speed': 0.1,
        'pulse_effect': False
    },
    'disabled': {
        'bg_color': UI_COLORS['button_disabled'],
        'border_color': UI_COLORS['button_border'],
        'text_color': UI_COLORS['text_dim'],
        'glow_color': None,
        'shadow_color': UI_COLORS['shadow'],
        'border_width': 1,
        'border_radius': 10,
        'padding': 10,
        'font': FONTS['normal'],
        'shadow_offset': 1,
        'glow_radius': 0,
        'transition_speed': 0.2,
        'pulse_effect': False
    }
}

# Screen states
SCREEN_STATES = {
    'MAIN_MENU': 'main_menu',
    'WORLD_GEN': 'world_gen',
    'GAME': 'game',
    'PAUSE': 'pause',
    'SETTINGS': 'settings',
    'OPTIONS': 'options'
}

# Camera settings
CAMERA_MOVE_SPEED = 500
CAMERA_ZOOM_SPEED = 0.1
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0

CAMERA_SETTINGS = {
    'default_zoom': 1.0,
    'min_zoom': MIN_ZOOM,
    'max_zoom': MAX_ZOOM,
    'move_speed': CAMERA_MOVE_SPEED,
    'zoom_speed': CAMERA_ZOOM_SPEED,
    'edge_scroll_margin': 50,  # Pixels from edge to start scrolling
    'edge_scroll_speed': 1.0,  # Multiplier for edge scrolling
    'smooth_follow': True,  # Whether to smoothly follow targets
    'follow_speed': 5.0,  # Speed of smooth following
    'shake_decay': 0.9,  # How quickly screen shake decays
    'max_shake': 10.0,  # Maximum screen shake offset
    'zoom_to_cursor': True,  # Whether to zoom towards cursor position
    'rotation_speed': 1.0,  # Speed of camera rotation
    'tilt_range': (-30, 30),  # Minimum and maximum camera tilt angles
    'bounds_margin': 100  # Margin from world edges in pixels
}

# Thought system
MAX_THOUGHTS = 10
THOUGHT_DURATION = 5.0
THOUGHT_INTERVAL = 2.0

THOUGHT_TYPES = {
    'need': {'priority': 3, 'duration': 5.0},
    'social': {'priority': 2, 'duration': 8.0},
    'goal': {'priority': 1, 'duration': 15.0},
    'memory': {'priority': 1, 'duration': 10.0},
    'environment': {'priority': 2, 'duration': 6.0}
}

# Thought categories
THOUGHT_CATEGORIES = [
    'needs',      # Basic needs like hunger, thirst, rest
    'social',     # Interactions with other humans
    'work',       # Tasks and jobs
    'explore',    # Curiosity and exploration
    'emotional',  # Feelings and reactions
]

# Thought complexity levels and their characteristics
THOUGHT_COMPLEXITY_LEVELS = {
    'basic': {
        'description': 'Simple, instinctive thoughts related to immediate needs',
        'processing_time': 0.5,  # Time in seconds to process
        'energy_cost': 0.1,  # Energy cost per thought
        'stress_impact': 0.05,  # Stress generated by thought
        'memory_chance': 0.2,  # Chance to create a memory
        'max_concurrent': 3,  # Maximum concurrent thoughts of this type
        'priority_boost': 1.2,  # Priority multiplier for urgent needs
        'interruption_chance': 0.8  # Chance to be interrupted by higher priority thoughts
    },
    'simple': {
        'description': 'Common thoughts about routine activities and observations',
        'processing_time': 1.0,
        'energy_cost': 0.2,
        'stress_impact': 0.1,
        'memory_chance': 0.4,
        'max_concurrent': 2,
        'priority_boost': 1.0,
        'interruption_chance': 0.6
    },
    'normal': {
        'description': 'Regular thoughts about daily activities and social interactions',
        'processing_time': 1.5,
        'energy_cost': 0.3,
        'stress_impact': 0.15,
        'memory_chance': 0.6,
        'max_concurrent': 2,
        'priority_boost': 0.9,
        'interruption_chance': 0.4
    },
    'complex': {
        'description': 'Advanced thoughts requiring analysis and planning',
        'processing_time': 2.0,
        'energy_cost': 0.4,
        'stress_impact': 0.2,
        'memory_chance': 0.8,
        'max_concurrent': 1,
        'priority_boost': 0.8,
        'interruption_chance': 0.2
    },
    'abstract': {
        'description': 'Deep, philosophical or creative thoughts',
        'processing_time': 3.0,
        'energy_cost': 0.5,
        'stress_impact': 0.25,
        'memory_chance': 1.0,
        'max_concurrent': 1,
        'priority_boost': 0.7,
        'interruption_chance': 0.1
    }
}

THOUGHT_SYSTEM_SETTINGS = {
    'max_thoughts': MAX_THOUGHTS,
    'thought_duration': THOUGHT_DURATION,
    'thought_interval': THOUGHT_INTERVAL,
    'fade_speed': 2.0,  # Speed of thought bubble fade in/out
    'glow_speed': 1.0,  # Speed of thought bubble glow effect
    'bubble_size': (200, 100),  # Width and height of thought bubbles
    'bubble_padding': 10,  # Padding inside thought bubbles
    'bubble_spacing': 5,  # Vertical spacing between bubbles
    'bubble_offset': (0, -50),  # Offset from entity position
    'font_size': 14,  # Font size for thought text
    'max_text_length': 50,  # Maximum length of thought text
    'wrap_width': 180,  # Width at which to wrap text
    'priority_decay': 0.1,  # Rate at which thought priority decays
    'emotion_influence': 0.5,  # How much emotions influence thoughts
    'memory_weight': 0.3,  # How much memories influence thoughts
    'personality_weight': 0.4,  # How much personality influences thoughts
    'environment_weight': 0.2,  # How much environment influences thoughts
    'social_weight': 0.3,  # How much social factors influence thoughts
    'need_threshold': 0.3,  # Threshold for need-based thoughts
    'max_memory_age': 300,  # Maximum age of memories to consider
    'thought_variety': 0.7  # Preference for varied thoughts (0-1)
}

# Emotion system settings
EMOTION_SYSTEM_SETTINGS = {
    'base_emotions': {
        'happiness': {'decay_rate': 0.1, 'max_value': 1.0, 'min_value': 0.0},
        'sadness': {'decay_rate': 0.15, 'max_value': 1.0, 'min_value': 0.0},
        'anger': {'decay_rate': 0.2, 'max_value': 1.0, 'min_value': 0.0},
        'fear': {'decay_rate': 0.25, 'max_value': 1.0, 'min_value': 0.0},
        'surprise': {'decay_rate': 0.3, 'max_value': 1.0, 'min_value': 0.0},
        'disgust': {'decay_rate': 0.2, 'max_value': 1.0, 'min_value': 0.0},
        'trust': {'decay_rate': 0.1, 'max_value': 1.0, 'min_value': 0.0},
        'anticipation': {'decay_rate': 0.15, 'max_value': 1.0, 'min_value': 0.0}
    },
    'emotion_triggers': {
        'need_satisfaction': 0.2,  # Emotion boost when needs are satisfied
        'social_interaction': 0.3,  # Emotion change from social interactions
        'goal_achievement': 0.4,  # Emotion boost from completing goals
        'environment_impact': 0.2,  # How much environment affects emotions
        'personality_influence': 0.3  # How much personality affects emotion changes
    },
    'mood_thresholds': {
        'joyful': 0.8,
        'content': 0.6,
        'neutral': 0.4,
        'sad': 0.2,
        'depressed': 0.0
    },
    'emotion_expression': {
        'facial_expression_threshold': 0.5,  # Threshold for showing facial expressions
        'gesture_threshold': 0.6,  # Threshold for showing emotional gestures
        'voice_modulation': 0.4  # Threshold for emotional voice changes
    },
    'emotion_memory': {
        'memory_impact': 0.3,  # How much memories affect emotions
        'memory_duration': 300,  # How long emotional memories last
        'memory_decay': 0.1  # Rate of decay with distance
    },
    'social_contagion': {
        'radius': 100,  # Radius for emotional influence
        'strength': 0.2,  # Strength of emotional contagion
        'decay': 0.1  # Rate of decay with distance
    },
    'visualization': {
        'color_intensity': 0.8,  # Intensity of emotion colors
        'particle_count': 20,  # Number of emotion particles
        'fade_speed': 2.0,  # Speed of emotional effect fading
        'glow_intensity': 0.5  # Intensity of emotional glow effects
    }
}

# Mood system
MOODS = {
    'joyful': {
        'color': (255, 223, 128),  # Bright yellow
        'glow_color': (255, 223, 128, 100),
        'particle_color': (255, 223, 128),
        'thought_boost': 1.2,  # Boost to thought generation
        'energy_boost': 1.1,  # Boost to energy regeneration
        'social_boost': 1.2,  # Boost to social interactions
        'productivity_boost': 1.1,  # Boost to work efficiency
        'duration_range': (300, 600),  # Duration range in seconds
        'contagion_radius': 150,  # How far the mood spreads
        'contagion_strength': 0.3,  # How strongly it affects others
        'weather_resistance': 1.2,  # Resistance to negative weather effects
        'stress_resistance': 1.2,  # Resistance to stress
        'memory_boost': 1.1,  # Better memory formation
        'learning_boost': 1.2,  # Better skill learning
        'creativity_boost': 1.3,  # Boost to creative activities
        'expressions': ['smile', 'laugh', 'dance'],  # Possible expressions
        'thought_types': ['positive', 'creative', 'social']  # Common thought types
    },
    'content': {
        'color': (173, 216, 230),  # Light blue
        'glow_color': (173, 216, 230, 80),
        'particle_color': (173, 216, 230),
        'thought_boost': 1.1,
        'energy_boost': 1.0,
        'social_boost': 1.1,
        'productivity_boost': 1.2,
        'duration_range': (600, 1200),
        'contagion_radius': 100,
        'contagion_strength': 0.2,
        'weather_resistance': 1.1,
        'stress_resistance': 1.1,
        'memory_boost': 1.2,
        'learning_boost': 1.1,
        'creativity_boost': 1.1,
        'expressions': ['smile', 'nod', 'relax'],
        'thought_types': ['productive', 'planning', 'curious']
    },
    'neutral': {
        'color': (200, 200, 200),  # Gray
        'glow_color': (200, 200, 200, 60),
        'particle_color': (200, 200, 200),
        'thought_boost': 1.0,
        'energy_boost': 1.0,
        'social_boost': 1.0,
        'productivity_boost': 1.0,
        'duration_range': (900, 1800),
        'contagion_radius': 50,
        'contagion_strength': 0.1,
        'weather_resistance': 1.0,
        'stress_resistance': 1.0,
        'memory_boost': 1.0,
        'learning_boost': 1.0,
        'creativity_boost': 1.0,
        'expressions': ['neutral', 'observe', 'think'],
        'thought_types': ['analytical', 'observant', 'practical']
    },
    'sad': {
        'color': (128, 128, 255),  # Blue
        'glow_color': (128, 128, 255, 70),
        'particle_color': (128, 128, 255),
        'thought_boost': 0.9,
        'energy_boost': 0.9,
        'social_boost': 0.8,
        'productivity_boost': 0.9,
        'duration_range': (300, 900),
        'contagion_radius': 120,
        'contagion_strength': 0.25,
        'weather_resistance': 0.9,
        'stress_resistance': 0.8,
        'memory_boost': 1.1,  # Sometimes better at remembering in sad moods
        'learning_boost': 0.9,
        'creativity_boost': 1.1,  # Can be more creative when sad
        'expressions': ['frown', 'sigh', 'slump'],
        'thought_types': ['reflective', 'emotional', 'introspective']
    },
    'tired': {
        'color': (169, 169, 169),  # Dark gray
        'glow_color': (169, 169, 169, 50),
        'particle_color': (169, 169, 169),
        'thought_boost': 0.8,
        'energy_boost': 0.7,
        'social_boost': 0.9,
        'productivity_boost': 0.8,
        'duration_range': (200, 600),
        'contagion_radius': 80,
        'contagion_strength': 0.15,
        'weather_resistance': 0.8,
        'stress_resistance': 0.7,
        'memory_boost': 0.8,
        'learning_boost': 0.8,
        'creativity_boost': 0.9,
        'expressions': ['yawn', 'stretch', 'rest'],
        'thought_types': ['basic', 'rest', 'comfort']
    }
}

# Personality system
PERSONALITY_TRAITS = {
    'openness': {
        'description': 'Openness to experience, creativity, and intellectual curiosity',
        'effects': {
            'learning_rate': 1.2,  # Learns new skills faster
            'exploration_range': 1.3,  # Explores further from home
            'creativity': 1.3,  # Better at creative tasks
            'adaptability': 1.2,  # Adapts better to changes
            'curiosity': 1.3  # More likely to investigate new things
        },
        'thought_types': ['creative', 'philosophical', 'abstract'],
        'interaction_bonus': {
            'explore': 1.3,
            'learn': 1.2,
            'create': 1.3
        },
        'mood_resistance': 1.1,  # Better at handling mood changes
        'stress_threshold': 0.9  # More sensitive to stress
    },
    'conscientiousness': {
        'description': 'Organization, responsibility, and work ethic',
        'effects': {
            'work_efficiency': 1.3,  # More efficient at tasks
            'resource_management': 1.2,  # Better at managing resources
            'planning': 1.3,  # Better at planning ahead
            'persistence': 1.2,  # More likely to complete tasks
            'precision': 1.2  # More accurate in tasks
        },
        'thought_types': ['planning', 'analytical', 'practical'],
        'interaction_bonus': {
            'work': 1.3,
            'organize': 1.2,
            'maintain': 1.2
        },
        'mood_resistance': 1.2,  # More stable moods
        'stress_threshold': 1.1  # Better stress handling
    },
    'extraversion': {
        'description': 'Sociability, energy, and assertiveness',
        'effects': {
            'social_range': 1.3,  # Interacts with more entities
            'social_energy': 1.2,  # Gains more energy from social interactions
            'leadership': 1.2,  # Better at leading groups
            'charisma': 1.3,  # More influential in social situations
            'mood_boost': 1.2  # Gets bigger mood boosts from positive events
        },
        'thought_types': ['social', 'expressive', 'energetic'],
        'interaction_bonus': {
            'socialize': 1.3,
            'lead': 1.2,
            'perform': 1.2
        },
        'mood_resistance': 0.9,  # More affected by moods
        'stress_threshold': 1.0  # Average stress handling
    },
    'agreeableness': {
        'description': 'Compassion, cooperation, and consideration of others',
        'effects': {
            'cooperation': 1.3,  # Better at working with others
            'empathy': 1.2,  # Better at understanding others' needs
            'helping': 1.3,  # More likely to help others
            'conflict_resolution': 1.2,  # Better at resolving conflicts
            'trust': 1.2  # More likely to trust others
        },
        'thought_types': ['helpful', 'empathetic', 'cooperative'],
        'interaction_bonus': {
            'help': 1.3,
            'comfort': 1.2,
            'share': 1.2
        },
        'mood_resistance': 1.0,  # Average mood stability
        'stress_threshold': 1.1  # Better stress handling
    },
    'neuroticism': {
        'description': 'Emotional sensitivity and tendency to experience negative emotions',
        'effects': {
            'emotional_intensity': 1.3,  # Stronger emotional responses
            'stress_sensitivity': 1.2,  # More affected by stressful situations
            'caution': 1.3,  # More careful in dangerous situations
            'recovery_rate': 0.8,  # Slower to recover from negative states
            'perception': 1.2  # Better at noticing potential threats
        },
        'thought_types': ['worried', 'cautious', 'emotional'],
        'interaction_bonus': {
            'avoid_danger': 1.3,
            'seek_safety': 1.2,
            'process_emotions': 1.2
        },
        'mood_resistance': 0.8,  # More volatile moods
        'stress_threshold': 0.8  # More easily stressed
    }
}

# Status effects
STATUS_EFFECTS = {
    'well_rested': {
        'duration': 300,
        'energy_regen': 1.5,
        'mood_boost': 10
    },
    'hungry': {
        'duration': -1,
        'energy_drain': 0.5,
        'mood_penalty': -10
    },
    'inspired': {
        'duration': 180,
        'creativity_boost': 1.5,
        'work_efficiency': 1.2
    },
    'tired': {
        'duration': -1,
        'speed_penalty': 0.7,
        'work_efficiency': 0.8
    },
    'sick': {
        'duration': 600,
        'health_drain': 0.2,
        'energy_drain': 0.3
    }
}

# Add missing imports
import random 

# Human types and attributes
HUMAN_TYPES = {
    'villager': {
        'sprite': '👨',
        'speed': 2.0,
        'size': TILE_SIZE,
        'vision_range': 8,
        'intelligence': 1.0,
        'starting_skills': {
            'farming': 1,
            'crafting': 1,
            'gathering': 1,
            'social': 1
        },
        'biomes': ['plains', 'forest', 'savanna']
    },
    'merchant': {
        'sprite': '🧔',
        'speed': 1.8,
        'size': TILE_SIZE,
        'vision_range': 10,
        'intelligence': 1.2,
        'starting_skills': {
            'trading': 2,
            'social': 2,
            'negotiation': 2
        },
        'biomes': ['plains', 'forest', 'savanna', 'beach']
    }
}

# Animal types and their properties
ANIMAL_TYPES = {
    'wolf': {
        'sprite': '🐺',
        'speed': 150,
        'size': 32,
        'behavior': 'predator',
        'vision_range': 300,
        'damage': 20,
        'health': 100,
        'max_energy': 100,
        'diet': ['meat'],
        'pack_animal': True
    },
    'deer': {
        'sprite': '🦌',
        'speed': 180,
        'size': 32,
        'behavior': 'prey',
        'vision_range': 250,
        'damage': 5,
        'health': 80,
        'max_energy': 120,
        'diet': ['grass', 'leaves'],
        'pack_animal': True
    },
    'rabbit': {
        'sprite': '🐰',
        'speed': 200,
        'size': 24,
        'behavior': 'prey',
        'vision_range': 200,
        'damage': 2,
        'health': 50,
        'max_energy': 80,
        'diet': ['grass', 'vegetables'],
        'pack_animal': False
    },
    'fox': {
        'sprite': '🦊',
        'speed': 170,
        'size': 28,
        'behavior': 'predator',
        'vision_range': 280,
        'damage': 15,
        'health': 70,
        'max_energy': 90,
        'diet': ['meat'],
        'pack_animal': False
    },
    'bear': {
        'sprite': '🐻',
        'speed': 130,
        'size': 40,
        'behavior': 'predator',
        'vision_range': 220,
        'damage': 30,
        'health': 150,
        'max_energy': 120,
        'diet': ['meat', 'fish', 'berries'],
        'pack_animal': False
    }
}

# Plant types and their properties
PLANT_TYPES = {
    'tree': {
        'sprite': '🌳',
        'max_size': 3.0,
        'growth_rate': 0.05,
        'reproduction_rate': 0.01,
        'resource_value': 20,
        'provides_shelter': True,
        'seasonal_behavior': True,
        'biomes': ['forest', 'plains', 'savanna']
    },
    'bush': {
        'sprite': '🌿',
        'max_size': 1.5,
        'growth_rate': 0.08,
        'reproduction_rate': 0.02,
        'resource_value': 10,
        'provides_shelter': False,
        'seasonal_behavior': True,
        'biomes': ['plains', 'forest', 'savanna']
    },
    'flower': {
        'sprite': '🌸',
        'max_size': 1.0,
        'growth_rate': 0.15,
        'reproduction_rate': 0.03,
        'resource_value': 5,
        'provides_shelter': False,
        'seasonal_behavior': True,
        'biomes': ['plains', 'forest', 'savanna']
    }
}

# Animal behaviors and their properties
ANIMAL_BEHAVIORS = {
    'idle': {
        'emoji': '💤',
        'duration': (5, 15)
    },
    'wandering': {
        'emoji': '🚶',
        'duration': (10, 30)
    },
    'hunting': {
        'emoji': '🏃',
        'duration': (20, 40)
    },
    'fleeing': {
        'emoji': '💨',
        'duration': (5, 15)
    },
    'resting': {
        'emoji': '😴',
        'duration': (15, 30)
    },
    'eating': {
        'emoji': '🍖',
        'duration': (5, 10)
    },
    'drinking': {
        'emoji': '💧',
        'duration': (3, 8)
    },
    'socializing': {
        'emoji': '💬',
        'duration': (10, 20)
    }
}

# Animal states and animations
ANIMAL_STATES = {
    'idle': {
        'frames': 1,
        'loop': True
    },
    'walk': {
        'frames': 4,
        'loop': True
    },
    'run': {
        'frames': 4,
        'loop': True
    },
    'eat': {
        'frames': 3,
        'loop': True
    },
    'attack': {
        'frames': 3,
        'loop': False
    },
    'hurt': {
        'frames': 2,
        'loop': False
    },
    'die': {
        'frames': 4,
        'loop': False
    },
    'sleep': {
        'frames': 2,
        'loop': True
    }
}

# Plant types and their properties
PLANT_TYPES = {
    'tree': {
        'sprite': '🌳',
        'max_size': 3.0,
        'growth_rate': 0.05,
        'reproduction_rate': 0.01,
        'resource_value': 20,
        'provides_shelter': True,
        'seasonal_behavior': True,
        'biomes': ['forest', 'plains', 'savanna']
    },
    'bush': {
        'sprite': '🌿',
        'max_size': 1.5,
        'growth_rate': 0.08,
        'reproduction_rate': 0.02,
        'resource_value': 10,
        'provides_shelter': False,
        'seasonal_behavior': True,
        'biomes': ['plains', 'forest', 'savanna']
    },
    'flower': {
        'sprite': '🌸',
        'max_size': 1.0,
        'growth_rate': 0.15,
        'reproduction_rate': 0.03,
        'resource_value': 5,
        'provides_shelter': False,
        'seasonal_behavior': True,
        'biomes': ['plains', 'forest', 'savanna']
    }
}

# Biome vegetation mapping
BIOME_VEGETATION = {
    'forest': ['tree', 'bush', 'flower', 'grass'],
    'rainforest': ['tree', 'bush', 'flower'],
    'jungle': ['tree', 'bush', 'flower'],
    'grassland': ['grass', 'bush', 'flower'],
    'savanna': ['grass', 'bush', 'tree'],
    'desert': ['cactus'],
    'tundra': ['grass'],
    'plains': ['grass', 'flower', 'bush']
}

# Graphics settings
GRAPHICS_QUALITY = {
    'ultra': {
        'particle_count': 1000,
        'glow_effects': True,
        'shadows': True,
        'antialiasing': True,
        'weather_effects': True,
        'animation_quality': 'high',
        'texture_quality': 'high',
        'reflection_quality': 'high',
        'particle_detail': 'high',
        'lighting_quality': 'high'
    },
    'high': {
        'particle_count': 500,
        'glow_effects': True,
        'shadows': True,
        'antialiasing': True,
        'weather_effects': True,
        'animation_quality': 'high',
        'texture_quality': 'high',
        'reflection_quality': 'medium',
        'particle_detail': 'medium',
        'lighting_quality': 'high'
    },
    'medium': {
        'particle_count': 250,
        'glow_effects': True,
        'shadows': True,
        'antialiasing': False,
        'weather_effects': True,
        'animation_quality': 'medium',
        'texture_quality': 'medium',
        'reflection_quality': 'low',
        'particle_detail': 'low',
        'lighting_quality': 'medium'
    },
    'low': {
        'particle_count': 100,
        'glow_effects': False,
        'shadows': False,
        'antialiasing': False,
        'weather_effects': False,
        'animation_quality': 'low',
        'texture_quality': 'low',
        'reflection_quality': 'off',
        'particle_detail': 'minimal',
        'lighting_quality': 'low'
    }
}

# Display flags for maximum graphics quality
DISPLAY_FLAGS = (
    pygame.HWSURFACE |  # Hardware surface for faster blitting
    pygame.DOUBLEBUF |  # Double buffering for smoother updates
    pygame.SCALED      # Allow for resolution scaling
)

# Visual Effects settings
VISUAL_EFFECTS = {
    'rain': {
        'particle_count': 200,
        'particle_size': (1, 3),
        'particle_speed': (500, 700),
        'particle_color': (200, 200, 255, 160)
    },
    'snow': {
        'particle_count': 150,
        'particle_size': (2, 4),
        'particle_speed': (100, 200),
        'particle_color': (255, 255, 255, 200)
    },
    'dust': {
        'particle_count': 50,
        'particle_size': (1, 2),
        'particle_speed': (50, 100),
        'particle_color': (180, 170, 150, 120)
    },
    'lightning': {
        'flash_duration': 0.1,
        'flash_intensity': 0.8,
        'flash_color': (255, 255, 255)
    }
}

# Entity settings
MAX_ENTITIES = 1000
ENTITY_VIEW_DISTANCE = 200
ENTITY_INTERACTION_DISTANCE = 50

# World settings
ACTIVE_CHUNKS_RADIUS = 3
WORLD_SEED = None  # Will be randomly generated if None

# Debug settings
DEBUG_MODE = __debug__
SHOW_FPS = True
SHOW_HITBOXES = False
SHOW_PATHS = False
SHOW_CHUNKS = False

# Biome colors and properties
BIOME_COLORS = {
    'ocean': (0, 105, 148),
    'beach': (238, 214, 175),
    'desert': (242, 209, 107),
    'tundra': (221, 221, 228),
    'mountains': (136, 140, 141),
    'forest': (34, 139, 34),
    'rainforest': (27, 113, 27),
    'plains': (143, 170, 64),
    'swamp': (71, 99, 71),
    'frozen_ocean': (166, 198, 219),
    'snowy_beach': (230, 230, 230),
    'snowy_mountains': (190, 190, 190),
    'rainforest_mountains': (47, 133, 47),
    'snowy_forest': (190, 214, 190)
}

# Graphics quality presets
GRAPHICS_QUALITY = {
    'ultra': {
        'particle_count': 1000,
        'shadow_quality': 3,
        'animation_frames': 8,
        'texture_size': 2,
        'antialiasing': True,
        'bloom_effect': True,
        'motion_blur': True,
        'weather_effects': True,
        'dynamic_lighting': True,
        'reflection_quality': 2,
        'vegetation_density': 1.0
    },
    'high': {
        'particle_count': 500,
        'shadow_quality': 2,
        'animation_frames': 6,
        'texture_size': 1,
        'antialiasing': True,
        'bloom_effect': True,
        'motion_blur': False,
        'weather_effects': True,
        'dynamic_lighting': True,
        'reflection_quality': 1,
        'vegetation_density': 0.8
    },
    'medium': {
        'particle_count': 250,
        'shadow_quality': 1,
        'animation_frames': 4,
        'texture_size': 1,
        'antialiasing': True,
        'bloom_effect': False,
        'motion_blur': False,
        'weather_effects': True,
        'dynamic_lighting': False,
        'reflection_quality': 0,
        'vegetation_density': 0.6
    },
    'low': {
        'particle_count': 100,
        'shadow_quality': 0,
        'animation_frames': 2,
        'texture_size': 0,
        'antialiasing': False,
        'bloom_effect': False,
        'motion_blur': False,
        'weather_effects': False,
        'dynamic_lighting': False,
        'reflection_quality': 0,
        'vegetation_density': 0.4
    }
}

# Screen states
SCREEN_STATES = {
    'main_menu': 'main_menu',
    'game': 'game',
    'pause': 'pause',
    'options': 'options',
    'world_gen': 'world_gen'
}

# Button styles with enhanced visual effects
BUTTON_STYLES = {
    'normal': {
        'border_radius': 10,
        'border_width': 2,
        'border_color': UI_COLORS['panel_border'],
        'glow_color': UI_COLORS['button_glow'],
        'shadow_color': (0, 0, 0, 60),
        'shadow_offset': 2,
        'transition_speed': 0.2,
        'pulse_effect': True
    },
    'hover': {
        'border_radius': 10,
        'border_width': 2,
        'border_color': UI_COLORS['text_highlight'],
        'glow_color': UI_COLORS['button_glow'],
        'shadow_color': (0, 0, 0, 80),
        'shadow_offset': 3,
        'transition_speed': 0.2,
        'pulse_effect': True
    },
    'pressed': {
        'border_radius': 10,
        'border_width': 2,
        'border_color': UI_COLORS['text_dim'],
        'glow_color': (0, 0, 0, 0),
        'shadow_color': (0, 0, 0, 100),
        'shadow_offset': 1,
        'transition_speed': 0.1,
        'pulse_effect': False
    },
    'disabled': {
        'border_radius': 10,
        'border_width': 1,
        'border_color': UI_COLORS['text_dim'],
        'glow_color': (0, 0, 0, 0),
        'shadow_color': (0, 0, 0, 40),
        'shadow_offset': 1,
        'transition_speed': 0.3,
        'pulse_effect': False
    }
}

# Initialize fonts
FONTS = {
    'title': pygame.font.Font(None, 64),
    'normal': pygame.font.Font(None, 32),
    'small': pygame.font.Font(None, 24),
    'tiny': pygame.font.Font(None, 16),
    'button': pygame.font.Font(None, 28)
} 

# Entity interaction types
INTERACTION_TYPES = {
    'talk': {
        'name': 'Talk',
        'icon': '💬',
        'duration': 5,
        'social_impact': 0.1
    },
    'trade': {
        'name': 'Trade',
        'icon': '💰',
        'duration': 10,
        'social_impact': 0.2
    },
    'help': {
        'name': 'Help',
        'icon': '🤝',
        'duration': 15,
        'social_impact': 0.3
    },
    'teach': {
        'name': 'Teach',
        'icon': '📚',
        'duration': 20,
        'social_impact': 0.25
    },
    'play': {
        'name': 'Play',
        'icon': '🎮',
        'duration': 10,
        'social_impact': 0.15
    }
}

# Entity states
ENTITY_STATES = {
    'idle': {
        'name': 'Idle',
        'icon': '💤',
        'energy_cost': 0
    },
    'moving': {
        'name': 'Moving',
        'icon': '🚶',
        'energy_cost': 0.5
    },
    'working': {
        'name': 'Working',
        'icon': '⚒️',
        'energy_cost': 1.0
    },
    'resting': {
        'name': 'Resting',
        'icon': '😴',
        'energy_cost': -1.0
    },
    'socializing': {
        'name': 'Socializing',
        'icon': '👥',
        'energy_cost': 0.3
    },
    'eating': {
        'name': 'Eating',
        'icon': '🍽️',
        'energy_cost': -0.5
    },
    'sleeping': {
        'name': 'Sleeping',
        'icon': '💤',
        'energy_cost': -2.0
    }
}

# Entity needs
ENTITY_NEEDS = {
    'hunger': {
        'name': 'Hunger',
        'icon': '🍖',
        'decay_rate': 0.1,
        'critical_threshold': 20
    },
    'thirst': {
        'name': 'Thirst',
        'icon': '💧',
        'decay_rate': 0.15,
        'critical_threshold': 15
    },
    'energy': {
        'name': 'Energy',
        'icon': '⚡',
        'decay_rate': 0.05,
        'critical_threshold': 10
    },
    'social': {
        'name': 'Social',
        'icon': '👥',
        'decay_rate': 0.03,
        'critical_threshold': 25
    },
    'comfort': {
        'name': 'Comfort',
        'icon': '🛋️',
        'decay_rate': 0.02,
        'critical_threshold': 30
    }
}

# Personality traits
PERSONALITY_TRAITS = {
    'openness': (0, 1),
    'conscientiousness': (0, 1),
    'extraversion': (0, 1),
    'agreeableness': (0, 1),
    'neuroticism': (0, 1)
}

# Moods
MOODS = {
    'happy': {
        'icon': '😊',
        'color': (50, 205, 50),
        'social_bonus': 0.2
    },
    'content': {
        'icon': '😌',
        'color': (135, 206, 235),
        'social_bonus': 0.1
    },
    'neutral': {
        'icon': '😐',
        'color': (200, 200, 200),
        'social_bonus': 0
    },
    'sad': {
        'icon': '😢',
        'color': (100, 149, 237),
        'social_bonus': -0.1
    },
    'angry': {
        'icon': '😠',
        'color': (220, 20, 60),
        'social_bonus': -0.2
    }
}

# Thought types
THOUGHT_TYPES = {
    'need': {
        'icon': '💭',
        'priority': 0.8
    },
    'social': {
        'icon': '👥',
        'priority': 0.6
    },
    'work': {
        'icon': '💼',
        'priority': 0.7
    },
    'explore': {
        'icon': '🗺️',
        'priority': 0.5
    },
    'rest': {
        'icon': '😴',
        'priority': 0.9
    }
}

# Human types
HUMAN_TYPES = {
    'villager': {
        'sprite': '👤',
        'speed': 2.0,
        'vision_range': 8,
        'intelligence': 1.0,
        'starting_skills': {
            'farming': 0.2,
            'crafting': 0.2,
            'social': 0.5
        }
    },
    'merchant': {
        'sprite': '👨‍💼',
        'speed': 1.8,
        'vision_range': 10,
        'intelligence': 1.2,
        'starting_skills': {
            'trading': 0.6,
            'social': 0.7,
            'negotiation': 0.5
        }
    },
    'farmer': {
        'sprite': '👨‍🌾',
        'speed': 1.5,
        'vision_range': 6,
        'intelligence': 0.9,
        'starting_skills': {
            'farming': 0.7,
            'nature': 0.6,
            'crafting': 0.3
        }
    }
}