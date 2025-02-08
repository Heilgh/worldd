"""Entity type definitions"""
from ...constants import (
    TILE_SIZE,
    ENTITY_TYPES,
    ENTITY_STATES,
    ENTITY_NEEDS
)

# Re-export the constants for backward compatibility
__all__ = ['ENTITY_TYPES', 'ENTITY_STATES', 'ENTITY_NEEDS']

# Base entity types
ENTITY_TYPES = {
    'human': {
        'size': TILE_SIZE,
        'speed': 2.0,
        'base_health': 100,
        'base_energy': 100,
        'vision_range': 8,
        'interaction_range': 2
    },
    'animal': {
        'size': TILE_SIZE * 0.8,
        'speed': 2.5,
        'base_health': 80,
        'base_energy': 90,
        'vision_range': 6,
        'interaction_range': 1
    },
    'plant': {
        'size': TILE_SIZE * 0.6,
        'speed': 0,
        'base_health': 50,
        'base_energy': 100,
        'vision_range': 0,
        'interaction_range': 1
    }
}

# Entity states
ENTITY_STATES = [
    'idle',
    'moving',
    'interacting',
    'resting',
    'eating',
    'drinking',
    'sleeping',
    'working',
    'fleeing',
    'hunting',
    'gathering',
    'building'
]

# Entity needs
ENTITY_NEEDS = {
    'health': {
        'min': 0,
        'max': 100,
        'decay_rate': 0.1,  # Per second
        'critical': 20,
        'warning': 50
    },
    'energy': {
        'min': 0,
        'max': 100,
        'decay_rate': 0.2,
        'critical': 20,
        'warning': 40
    },
    'hunger': {
        'min': 0,
        'max': 100,
        'increase_rate': 0.3,
        'critical': 80,
        'warning': 60
    },
    'thirst': {
        'min': 0,
        'max': 100,
        'increase_rate': 0.4,
        'critical': 80,
        'warning': 60
    }
}

# Entity actions
ENTITY_ACTIONS = {
    'move': {
        'energy_cost': 0.5,
        'duration': 0
    },
    'interact': {
        'energy_cost': 1.0,
        'duration': 2.0
    },
    'rest': {
        'energy_gain': 5.0,
        'duration': 5.0
    },
    'eat': {
        'hunger_reduction': 30,
        'duration': 3.0
    },
    'drink': {
        'thirst_reduction': 40,
        'duration': 2.0
    },
    'sleep': {
        'energy_gain': 10.0,
        'duration': 20.0
    }
}

def is_human(entity):
    """Check if entity is a human without importing Human class"""
    return entity.__class__.__name__ == 'Human'

def is_animal(entity):
    """Check if entity is an animal without importing Animal class"""
    return entity.__class__.__name__ == 'Animal'

def is_plant(entity):
    """Check if entity is a plant without importing Plant class"""
    return entity.__class__.__name__ == 'Plant' 