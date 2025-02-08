import pygame
from ..panel import UIPanel
from ...constants import UI_COLORS
from ...world.entities.human import Human
from ...world.entities.animal import Animal
from ...world.entities.plant import Plant

class EntityListPanel(UIPanel):
    def __init__(self, x, y, width, height, title="Entities", icon="👥"):
        super().__init__(x, y, width, height, title, icon)
        self.selected_entity = None
        self.scroll_offset = 0
        self.max_visible_items = 10
        self.item_height = 30
        self.world = None
        
    def initialize(self, world):
        """Initialize panel with world reference"""
        self.world = world
        
    def update(self, world, dt):
        """Update entity list"""
        self.world = world
        
    def draw(self, screen, world):
        """Draw entity list panel"""
        try:
            # Draw panel background
            super().draw(screen)
            
            if not world or not hasattr(world, 'entities'):
                return
                
            # Get sorted list of entities
            entities = sorted(world.entities, key=lambda e: self._get_entity_name(e))
            
            # Calculate visible range
            start_idx = self.scroll_offset
            end_idx = min(start_idx + self.max_visible_items, len(entities))
            
            # Draw visible entities
            y_pos = self.y + 40  # Start below title
            for i in range(start_idx, end_idx):
                entity = entities[i]
                
                # Get entity name and type
                name = self._get_entity_name(entity)
                type_text = self._get_entity_type(entity)
                
                # Calculate item rect
                item_rect = pygame.Rect(self.x + 5, y_pos, self.width - 10, self.item_height)
                
                # Draw selection highlight
                if entity == self.selected_entity:
                    pygame.draw.rect(screen, UI_COLORS['selection'], item_rect)
                
                # Draw entity info
                if name:
                    name_text = self.font.render(name, True, UI_COLORS['text_normal'])
                    screen.blit(name_text, (item_rect.x + 5, item_rect.y + 5))
                    
                if type_text:
                    type_surface = self.font.render(type_text, True, UI_COLORS['text_dim'])
                    screen.blit(type_surface, (item_rect.right - type_surface.get_width() - 5, item_rect.y + 5))
                
                y_pos += self.item_height
                
            # Draw scroll indicators if needed
            if self.scroll_offset > 0:
                self._draw_scroll_indicator(screen, "▲", self.y + 30)
            if end_idx < len(entities):
                self._draw_scroll_indicator(screen, "▼", self.y + self.height - 20)
                
        except Exception as e:
            print(f"Error drawing entity list: {e}")
            import traceback
            traceback.print_exc()
            
    def _get_entity_name(self, entity) -> str:
        """Get entity display name"""
        try:
            # First try to get explicit name
            if hasattr(entity, 'name') and entity.name:
                return str(entity.name)
            
            # Try to construct a descriptive name
            type_str = ""
            if hasattr(entity, 'subtype') and entity.subtype:
                type_str = str(entity.subtype).title()
            elif hasattr(entity, 'type') and entity.type:
                type_str = str(entity.type).title()
            else:
                type_str = entity.__class__.__name__
                
            # Add ID to make unique
            entity_id = id(entity) % 1000
            return f"{type_str} {entity_id}"
            
        except Exception as e:
            print(f"Error getting entity name: {e}")
            return f"Entity {id(entity) % 1000}"
            
    def _get_entity_type(self, entity) -> str:
        """Get entity type display text"""
        try:
            # First try to get subtype
            if hasattr(entity, 'subtype') and entity.subtype:
                return str(entity.subtype).title()
            # Then try type
            elif hasattr(entity, 'type') and entity.type:
                return str(entity.type).title()
            # If both are None or missing, check class name
            elif hasattr(entity, '__class__'):
                return entity.__class__.__name__
            else:
                return "Unknown"
        except Exception as e:
            print(f"Error getting entity type: {e}")
            return "Unknown"
            
    def _draw_scroll_indicator(self, screen, text, y):
        """Draw scroll indicator arrow"""
        text_surface = self.font.render(text, True, UI_COLORS['text_dim'])
        x = self.x + (self.width - text_surface.get_width()) // 2
        screen.blit(text_surface, (x, y))
        
    def handle_event(self, event, world):
        """Handle mouse events"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle scrolling
                if event.button in (4, 5):  # Mouse wheel
                    if event.button == 4:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                    else:  # Scroll down
                        if world and hasattr(world, 'entities'):
                            max_offset = max(0, len(world.entities) - self.max_visible_items)
                            self.scroll_offset = min(max_offset, self.scroll_offset + 1)
                    return True
                
                # Handle entity selection
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    if self.x <= mouse_pos[0] <= self.x + self.width:
                        # Calculate clicked index
                        rel_y = mouse_pos[1] - (self.y + 40)
                        clicked_idx = self.scroll_offset + (rel_y // self.item_height)
                        
                        if world and hasattr(world, 'entities'):
                            entities = sorted(world.entities, key=lambda e: self._get_entity_name(e))
                            if 0 <= clicked_idx < len(entities):
                                clicked_entity = entities[clicked_idx]
                                self.selected_entity = clicked_entity
                                
                                # Center camera on selected entity
                                if hasattr(world, 'camera') and hasattr(clicked_entity, 'x') and hasattr(clicked_entity, 'y'):
                                    target_x = clicked_entity.x
                                    target_y = clicked_entity.y
                                    
                                    # Set camera position to center on entity
                                    world.camera['x'] = target_x - (world.camera['viewport_width'] / world.camera['zoom']) / 2
                                    world.camera['y'] = target_y - (world.camera['viewport_height'] / world.camera['zoom']) / 2
                                    
                                    # Zoom in slightly
                                    world.camera['zoom'] = min(2.0, world.camera['zoom'] * 1.5)
                                    
                                return True
            return False
            
        except Exception as e:
            print(f"Error handling entity list event: {e}")
            return False 