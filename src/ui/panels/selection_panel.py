import pygame
from ..panel import UIPanel
from ...constants import UI_COLORS

class SelectionPanel:
    def __init__(self):
        self.selected_entity = None
        self.selected_tile = None
        self.hover_entity = None
        self.world = None
        
    def initialize(self, world):
        """Initialize with world reference"""
        self.world = world
        
    def update(self, world, mouse_pos):
        """Update hover and selection state"""
        try:
            # Update hover entity
            self.hover_entity = None
            if world:
                for entity in world.entities:
                    if hasattr(entity, 'rect') and entity.rect.collidepoint(mouse_pos):
                        self.hover_entity = entity
                        break
                        
        except Exception as e:
            print(f"Error updating selection: {e}")
            import traceback
            traceback.print_exc()
                    
    def handle_click(self, pos):
        """Handle selection click"""
        try:
            # Handle selection
            if self.hover_entity:
                self.selected_entity = self.hover_entity
                return True
            else:
                self.selected_entity = None
                return False
                
        except Exception as e:
            print(f"Error handling selection click: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def draw(self, screen, world):
        """Draw selection and hover effects"""
        try:
            if not world:
                return
                
            # Draw hover effect
            if self.hover_entity and hasattr(self.hover_entity, 'rect'):
                hover_rect = self.hover_entity.rect.copy()
                hover_rect.inflate_ip(4, 4)  # Make hover rect slightly larger
                pygame.draw.rect(screen, UI_COLORS['hover'], hover_rect, 2)
                
            # Draw selection effect
            if self.selected_entity and hasattr(self.selected_entity, 'rect'):
                select_rect = self.selected_entity.rect.copy()
                select_rect.inflate_ip(6, 6)  # Make selection rect larger than hover
                pygame.draw.rect(screen, UI_COLORS['selection'], select_rect, 3)
                
                # Draw selection glow
                glow_rect = select_rect.copy()
                glow_rect.inflate_ip(4, 4)
                for i in range(3):
                    glow_alpha = 100 - i * 30
                    glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*UI_COLORS['selection'][:3], glow_alpha),
                                   glow_surface.get_rect(), 1)
                    screen.blit(glow_surface, glow_rect)
                    glow_rect.inflate_ip(2, 2)
                    
        except Exception as e:
            print(f"Error drawing selection: {e}")
            import traceback
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up resources"""
        self.selected_entity = None
        self.hover_entity = None
        self.world = None 