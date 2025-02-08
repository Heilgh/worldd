import pygame
import traceback
from typing import Dict, List, Optional, Tuple
from ..constants import TILE_SIZE, CHUNK_SIZE

class Chunk:
    def __init__(self, x: int, y: int, terrain_generator):
        """Initialize chunk"""
        try:
            print(f"Creating chunk at ({x}, {y})")
            self.x = x
            self.y = y
            self.size = CHUNK_SIZE
            self.tile_size = TILE_SIZE
            
            # Generate chunk data
            self.data = terrain_generator.generate_chunk(x, y, CHUNK_SIZE)
            
            # Rendering optimization
            self.surface = None
            self.needs_update = True
            
            print(f"Chunk ({x}, {y}) created successfully")
            
        except Exception as e:
            print(f"Error creating chunk: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update chunk state"""
        try:
            # Update resources
            if 'resources' in self.data:
                for resource in self.data['resources']:
                    if hasattr(resource, 'update'):
                        resource.update(dt)
                        
        except Exception as e:
            print(f"Error updating chunk: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface, camera_pos: Tuple[float, float], zoom: float):
        """Draw chunk contents"""
        try:
            # Calculate chunk screen position
            chunk_screen_x = (self.x * self.size * self.tile_size - camera_pos[0]) * zoom
            chunk_screen_y = (self.y * self.size * self.tile_size - camera_pos[1]) * zoom
            
            # Check if chunk is visible
            screen_rect = surface.get_rect()
            chunk_rect = pygame.Rect(
                chunk_screen_x,
                chunk_screen_y,
                self.size * self.tile_size * zoom,
                self.size * self.tile_size * zoom
            )
            
            if not screen_rect.colliderect(chunk_rect):
                return
                
            # Update chunk surface if needed
            if self.needs_update or self.surface is None:
                self._update_surface()
                
            # Draw chunk surface
            scaled_size = (
                int(self.size * self.tile_size * zoom),
                int(self.size * self.tile_size * zoom)
            )
            scaled_surface = pygame.transform.scale(self.surface, scaled_size)
            surface.blit(scaled_surface, (chunk_screen_x, chunk_screen_y))
            
            # Draw resources
            if 'resources' in self.data:
                for resource in self.data['resources']:
                    if hasattr(resource, 'draw'):
                        resource.draw(surface, camera_pos, zoom)
                        
        except Exception as e:
            print(f"Error drawing chunk: {e}")
            traceback.print_exc()
            
    def _update_surface(self):
        """Update chunk surface"""
        try:
            # Create surface if needed
            if self.surface is None:
                self.surface = pygame.Surface(
                    (self.size * self.tile_size, self.size * self.tile_size)
                )
                
            # Draw terrain
            for y in range(self.size):
                for x in range(self.size):
                    # Get tile properties
                    biome = self.data['biomes'][y][x]
                    height = self.data['heightmap'][y][x]
                    
                    # Calculate tile color
                    base_color = self._get_biome_color(biome)
                    shade = 0.8 + height * 0.4  # Height-based shading
                    color = tuple(int(c * shade) for c in base_color)
                    
                    # Draw tile
                    tile_rect = pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(self.surface, color, tile_rect)
                    
            self.needs_update = False
            
        except Exception as e:
            print(f"Error updating chunk surface: {e}")
            traceback.print_exc()
            
    def _get_biome_color(self, biome: str) -> Tuple[int, int, int]:
        """Get color for biome type"""
        try:
            # Default colors for basic biomes
            colors = {
                'ocean': (0, 0, 139),
                'beach': (238, 214, 175),
                'grass': (34, 139, 34),
                'forest': (0, 100, 0),
                'mountain': (139, 137, 137),
                'snow': (255, 250, 250)
            }
            return colors.get(biome, (128, 128, 128))  # Gray as fallback
            
        except Exception as e:
            print(f"Error getting biome color: {e}")
            traceback.print_exc()
            return (128, 128, 128)  # Gray as fallback
            
    def get_tile_height(self, x: int, y: int) -> float:
        """Get height value for tile position"""
        try:
            if 0 <= x < self.size and 0 <= y < self.size:
                return self.data['heightmap'][y][x]
            return 0.0
            
        except Exception as e:
            print(f"Error getting tile height: {e}")
            traceback.print_exc()
            return 0.0
            
    def get_tile_biome(self, x: int, y: int) -> str:
        """Get biome type for tile position"""
        try:
            if 0 <= x < self.size and 0 <= y < self.size:
                return self.data['biomes'][y][x]
            return 'ocean'
            
        except Exception as e:
            print(f"Error getting tile biome: {e}")
            traceback.print_exc()
            return 'ocean'
            
    def get_resources_at(self, x: int, y: int) -> List[Dict]:
        """Get resources at tile position"""
        try:
            resources = []
            if 'resources' in self.data:
                for resource in self.data['resources']:
                    if resource['x'] == x and resource['y'] == y:
                        resources.append(resource)
            return resources
            
        except Exception as e:
            print(f"Error getting resources: {e}")
            traceback.print_exc()
            return []
            
    def cleanup(self):
        """Clean up chunk resources"""
        try:
            print(f"Cleaning up chunk ({self.x}, {self.y})")
            
            # Clean up resources
            if 'resources' in self.data:
                for resource in self.data['resources']:
                    if hasattr(resource, 'cleanup'):
                        resource.cleanup()
                        
            # Clear surface
            if self.surface:
                self.surface = None
                
            # Clear data
            self.data.clear()
            
        except Exception as e:
            print(f"Error cleaning up chunk: {e}")
            traceback.print_exc()