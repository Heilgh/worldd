import pygame
import random
import traceback
from typing import Dict, List, Optional, Tuple
from ..constants import (
    CHUNK_SIZE, TILE_SIZE, BIOMES,
    RESOURCE_TYPES, ENTITY_TYPES,
    WINDOW_WIDTH, WINDOW_HEIGHT
)

# Grid display setting
SHOW_GRID = False  # Can be toggled for debugging

class Chunk:
    def __init__(self, world, pos: Tuple[int, int]):
        """Initialize chunk"""
        self.world = world
        self.x, self.y = pos
        self.pos = pos
        self.active = False
        self.needs_update = True
        self.surface = None
        self.entities = set()  # Use set for faster lookups
        self.heightmap = None
        self.biome_map = None
        self.tiles = {}
        
    def initialize(self, heightmap, biome_map):
        """Initialize chunk with terrain data"""
        try:
            self.heightmap = heightmap
            self.biome_map = biome_map
            self.needs_update = True
            
            # Initialize tiles
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile_pos = (x, y)
                    self.tiles[tile_pos] = {
                        'height': heightmap[y][x],
                        'biome': biome_map[y][x],
                        'walkable': True  # Default to walkable
                    }
                    
            print(f"Initialized chunk at {self.pos}")
            
        except Exception as e:
            print(f"Error initializing chunk: {e}")
            traceback.print_exc()
            
    def add_entity(self, entity):
        """Add entity to chunk"""
        try:
            if entity not in self.entities:
                self.entities.add(entity)
                self.needs_update = True
                print(f"Added entity {entity.id} to chunk {self.pos}")
                
        except Exception as e:
            print(f"Error adding entity to chunk: {e}")
            traceback.print_exc()
            
    def remove_entity(self, entity):
        """Remove entity from chunk"""
        try:
            if entity in self.entities:
                self.entities.remove(entity)
                self.needs_update = True
                print(f"Removed entity {entity.id} from chunk {self.pos}")
                
        except Exception as e:
            print(f"Error removing entity from chunk: {e}")
            traceback.print_exc()
            
    def get_entities(self):
        """Get all entities in chunk"""
        return list(self.entities)
        
    def get_tile(self, x: int, y: int) -> Optional[Dict]:
        """Get tile data at local coordinates"""
        return self.tiles.get((x, y))
        
    def update(self, dt: float):
        """Update chunk state"""
        try:
            if not self.active:
                return
                
            # Update entities in chunk
            for entity in list(self.entities):
                if hasattr(entity, 'update'):
                    entity.update(self.world, dt)
                    
            self.needs_update = False
            
        except Exception as e:
            print(f"Error updating chunk: {e}")
            traceback.print_exc()
            
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float):
        """Draw chunk and its entities"""
        try:
            if not self.active:
                return
                
            # Calculate screen position
            screen_x = int((self.x * CHUNK_SIZE * TILE_SIZE - camera_x) * zoom)
            screen_y = int((self.y * CHUNK_SIZE * TILE_SIZE - camera_y) * zoom)
            
            # Skip if chunk is completely off screen
            chunk_size_pixels = CHUNK_SIZE * TILE_SIZE * zoom
            if (screen_x + chunk_size_pixels < 0 or
                screen_x > WINDOW_WIDTH or
                screen_y + chunk_size_pixels < 0 or
                screen_y > WINDOW_HEIGHT):
                return
                
            # Update surface if needed
            if self.needs_update or not self.surface:
                self._update_surface()
                
            # Draw terrain if surface exists
            if self.surface:
                # Scale surface
                scaled_size = int(CHUNK_SIZE * TILE_SIZE * zoom)
                if scaled_size > 0:
                    try:
                        scaled_surface = pygame.transform.scale(self.surface, (scaled_size, scaled_size))
                        screen.blit(scaled_surface, (screen_x, screen_y))
                    except Exception as e:
                        print(f"Error scaling chunk surface: {e}")
                    
            # Draw grid for debugging if enabled
            if SHOW_GRID:
                grid_color = (100, 100, 100, 128)
                pygame.draw.rect(screen, grid_color, 
                               (screen_x, screen_y, scaled_size, scaled_size), 1)
                    
            # Draw entities in chunk
            for entity in sorted(self.entities, key=lambda e: e.y if hasattr(e, 'y') else 0):
                if hasattr(entity, 'draw') and hasattr(entity, 'active') and entity.active:
                    try:
                        entity.draw(screen, camera_x, camera_y, zoom)
                    except Exception as e:
                        print(f"Error drawing entity {entity.id}: {e}")
                        
        except Exception as e:
            print(f"Error drawing chunk: {e}")
            traceback.print_exc()
            
    def _update_surface(self):
        """Update chunk surface with current terrain"""
        try:
            if not self.heightmap or not self.biome_map:
                return
                
            # Create surface if needed
            if not self.surface:
                self.surface = pygame.Surface((CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE))
                
            # Draw terrain
            for y in range(CHUNK_SIZE):
                for x in range(CHUNK_SIZE):
                    tile = self.tiles.get((x, y))
                    if not tile:
                        continue
                        
                    # Get tile color based on biome and height
                    biome = tile['biome']
                    height = tile['height']
                    
                    if biome in BIOMES:
                        base_color = BIOMES[biome]['color']
                        # Adjust color based on height
                        color = [
                            min(255, int(c * (0.7 + height * 0.6)))
                            for c in base_color
                        ]
                    else:
                        color = (100, 100, 100)  # Default gray
                        
                    # Draw tile with slight variation
                    variation = random.uniform(0.95, 1.05)
                    final_color = [min(255, int(c * variation)) for c in color]
                    
                    # Draw tile
                    tile_rect = pygame.Rect(
                        x * TILE_SIZE, y * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    pygame.draw.rect(self.surface, final_color, tile_rect)
                    
                    # Add border for better visibility
                    pygame.draw.rect(self.surface, [c * 0.8 for c in final_color], tile_rect, 1)
                    
            self.needs_update = False
            
        except Exception as e:
            print(f"Error updating chunk surface: {e}")
            traceback.print_exc()

    def cleanup(self):
        """Clean up chunk resources"""
        try:
            # Clear surface
            if self.surface:
                self.surface = None
            
            # Clear entity references
            self.entities.clear()
            
            # Clear tile data
            self.tiles.clear()
            
            # Clear other references
            self.world = None
            self.heightmap = None
            self.biome_map = None
            
            print(f"Cleaned up chunk at {self.pos}")
            
        except Exception as e:
            print(f"Error cleaning up chunk: {e}")
            traceback.print_exc()

    def draw_terrain(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float):
        """Draw only the terrain part of the chunk"""
        try:
            if not self.active:
                return
                
            # Calculate screen position
            screen_x = int((self.x * CHUNK_SIZE * TILE_SIZE - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y * CHUNK_SIZE * TILE_SIZE - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Skip if chunk is completely off screen
            chunk_size_pixels = CHUNK_SIZE * TILE_SIZE * zoom
            if (screen_x + chunk_size_pixels < 0 or
                screen_x > WINDOW_WIDTH or
                screen_y + chunk_size_pixels < 0 or
                screen_y > WINDOW_HEIGHT):
                return
                
            # Update surface if needed
            if self.needs_update or not self.surface:
                self._update_surface()
                
            # Draw terrain if surface exists
            if self.surface:
                # Scale surface
                scaled_size = int(CHUNK_SIZE * TILE_SIZE * zoom)
                if scaled_size > 0:
                    try:
                        scaled_surface = pygame.transform.scale(self.surface, (scaled_size, scaled_size))
                        screen.blit(scaled_surface, (screen_x, screen_y))
                    except Exception as e:
                        print(f"Error scaling chunk surface: {e}")
                        
        except Exception as e:
            print(f"Error drawing chunk terrain: {e}")
            traceback.print_exc()