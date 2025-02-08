import pygame
from ..panel import UIPanel
from ...constants import UI_COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE
from ...world.entities.human import Human
from ...world.entities.animal import Animal
from ...world.entities.plant import Plant
import traceback

class MinimapPanel(UIPanel):
    def __init__(self, x, y, width, height, title="Minimap", icon="🗺️"):
        super().__init__(x, y, width, height, title, icon)
        
        # Initialize minimap surface
        self.map_width = width - 20
        self.map_height = height - 40
        self.map_surface = pygame.Surface((self.map_width, self.map_height))
        self.map_surface.fill(UI_COLORS['minimap_bg'])
        
        # Initialize colors
        self.colors = {
            'water': UI_COLORS['minimap_water'],
            'grass': UI_COLORS['minimap_grass'],
            'forest': UI_COLORS['minimap_forest'],
            'mountain': UI_COLORS['minimap_mountain'],
            'desert': UI_COLORS['minimap_desert'],
            'snow': UI_COLORS['minimap_snow'],
            'entity': UI_COLORS['minimap_entity'],
            'player': UI_COLORS['minimap_player']
        }
        
    def initialize(self, world):
        """Initialize panel with world reference"""
        self.world = world
        
    def draw(self, screen, world):
        """Draw the minimap panel"""
        try:
            # Draw base panel
            super().draw(screen)
            
            if not world:
                return
                
            # Clear minimap surface
            self.map_surface.fill(UI_COLORS['minimap_bg'])
            
            # Calculate scale factors
            scale_x = self.map_width / world.width
            scale_y = self.map_height / world.height
            
            # Draw terrain
            for chunk in world.visible_chunks:
                chunk_x, chunk_y = chunk
                for tile_x in range(TILE_SIZE):
                    for tile_y in range(TILE_SIZE):
                        world_x = chunk_x * TILE_SIZE + tile_x
                        world_y = chunk_y * TILE_SIZE + tile_y
                        
                        if 0 <= world_x < world.width and 0 <= world_y < world.height:
                            tile = world.get_tile(world_x, world_y)
                            if tile:
                                color = self.colors.get(tile['biome'], UI_COLORS['minimap_unknown'])
                                x = int(world_x * scale_x)
                                y = int(world_y * scale_y)
                                pygame.draw.rect(self.map_surface, color, (x, y, max(1, scale_x), max(1, scale_y)))
            
            # Draw entities
            for entity in world.active_entities:
                if hasattr(entity, 'x') and hasattr(entity, 'y'):
                    x = int(entity.x * scale_x)
                    y = int(entity.y * scale_y)
                    color = self.colors['player'] if entity.type == 'player' else self.colors['entity']
                    pygame.draw.circle(self.map_surface, color, (x, y), max(1, int(2 * scale_x)))
            
            # Draw viewport rectangle
            if hasattr(world, 'camera'):
                view_x = int(world.camera['x'] * scale_x)
                view_y = int(world.camera['y'] * scale_y)
                view_w = int(world.camera['viewport_width'] * scale_x)
                view_h = int(world.camera['viewport_height'] * scale_y)
                pygame.draw.rect(self.map_surface, UI_COLORS['minimap_viewport'],
                               (view_x, view_y, view_w, view_h), 1)
            
            # Draw minimap surface
            screen.blit(self.map_surface, (self.x + 10, self.y + 30))
            
        except Exception as e:
            print(f"Error drawing minimap: {e}")
            traceback.print_exc()
            
    def handle_event(self, event, world):
        """Handle mouse events for map navigation"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Calculate clicked position in world coordinates
                rel_x = (event.pos[0] - self.rect.x) / self.rect.width
                rel_y = (event.pos[1] - self.rect.y) / self.rect.height
                
                world_x = rel_x * world.width
                world_y = rel_y * world.height
                
                # Center camera on clicked position
                world.camera['x'] = world_x - (WINDOW_WIDTH / world.camera['zoom']) / 2
                world.camera['y'] = world_y - (WINDOW_HEIGHT / world.camera['zoom']) / 2
                return True
        return False 