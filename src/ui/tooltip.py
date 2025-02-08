import pygame
from ..constants import UI_COLORS

class TooltipSystem:
    def __init__(self):
        try:
            self.current_tooltip = None
            self.font = pygame.font.Font(None, 24)
            self.padding = 8
            self.border_radius = 5
            self.glow_size = 3
            
            # Use UI_COLORS for consistent styling
            self.background_color = UI_COLORS.get('tooltip_bg', (40, 40, 40, 230))
            self.text_color = UI_COLORS.get('text_normal', (255, 255, 255))
            self.border_color = UI_COLORS.get('panel_border', (100, 100, 100))
            self.glow_color = UI_COLORS.get('tooltip_glow', (255, 255, 255, 30))
        except Exception as e:
            print(f"Error initializing TooltipSystem: {e}")
            self.current_tooltip = None
    
    def set_tooltip(self, text, pos):
        try:
            self.current_tooltip = {
                'text': text,
                'pos': pos,
                'alpha': 255,
                'fade_time': 0.2,
                'fade_timer': 0.0
            }
        except Exception as e:
            print(f"Error setting tooltip: {e}")
            self.current_tooltip = None
    
    def clear_tooltip(self):
        self.current_tooltip = None
        
    def draw(self, screen):
        if not self.current_tooltip:
            return
            
        try:
            lines = self.current_tooltip['text'].split('\n')
            text_surfaces = [self.font.render(line, True, self.text_color) for line in lines]
            
            # Calculate tooltip dimensions
            width = max(surface.get_width() for surface in text_surfaces) + self.padding * 2
            height = sum(surface.get_height() for surface in text_surfaces) + self.padding * 2
            x, y = self.current_tooltip['pos']
            
            # Ensure tooltip stays within screen bounds
            screen_rect = screen.get_rect()
            if x + width > screen_rect.right:
                x = screen_rect.right - width - 5
            if y + height > screen_rect.bottom:
                y = screen_rect.bottom - height - 5
            
            # Create tooltip surface with alpha
            surface = pygame.Surface((width + self.glow_size * 2, height + self.glow_size * 2), pygame.SRCALPHA)
            
            # Draw glow effect
            glow_rect = pygame.Rect(self.glow_size, self.glow_size, width, height)
            pygame.draw.rect(surface, self.glow_color, glow_rect.inflate(self.glow_size * 2, self.glow_size * 2), 
                           border_radius=self.border_radius + self.glow_size)
            
            # Draw background
            pygame.draw.rect(surface, self.background_color, glow_rect, border_radius=self.border_radius)
            
            # Draw border
            pygame.draw.rect(surface, self.border_color, glow_rect, 1, border_radius=self.border_radius)
            
            # Draw text
            current_y = self.padding + self.glow_size
            for text_surface in text_surfaces:
                surface.blit(text_surface, (self.padding + self.glow_size, current_y))
                current_y += text_surface.get_height()
            
            # Apply fade effect if needed
            if self.current_tooltip.get('fade_timer', 0) > 0:
                alpha = int(255 * (1 - self.current_tooltip['fade_timer'] / self.current_tooltip['fade_time']))
                surface.set_alpha(alpha)
            
            screen.blit(surface, (x - self.glow_size, y - self.glow_size))
            
        except Exception as e:
            print(f"Error drawing tooltip: {e}")
            self.current_tooltip = None

    def update(self, world, mouse_pos):
        """Update tooltip based on mouse position"""
        self.current_tooltip = None
        if world:
            # Check for entities under mouse
            for entity in world.entities:
                if entity.rect.collidepoint(mouse_pos):
                    if hasattr(entity, 'get_tooltip_text'):
                        text = entity.get_tooltip_text()
                    else:
                        text = f"Type: {entity.entity_type}\nPosition: ({int(entity.x)}, {int(entity.y)})"
                    self.set_tooltip(text, mouse_pos)
                    break 