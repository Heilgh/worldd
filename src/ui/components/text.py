import pygame
from typing import Tuple, Optional
from ...constants import UI_COLORS, FONTS

class Text:
    def __init__(self, text: str, pos: Tuple[int, int],
                 font_name: str = 'normal',
                 color: Tuple[int, int, int] = None,
                 center: bool = False,
                 shadow: bool = False,
                 shadow_color: Tuple[int, int, int] = None,
                 glow: bool = False,
                 glow_color: Tuple[int, int, int, int] = None,
                 alpha: int = 255,
                 scale: float = 1.0,
                 rotation: float = 0.0,
                 outline: bool = False,
                 outline_color: Tuple[int, int, int] = None,
                 outline_width: int = 2):
        """Initialize text component with advanced rendering options"""
        try:
            self.text = str(text)
            self.pos = pos
            
            # Get font with fallback
            if font_name not in FONTS:
                print(f"Warning: Font '{font_name}' not found, using 'normal' font")
                font_name = 'normal'
            self.font = FONTS[font_name]
            if not self.font:
                print(f"Error: Could not load font '{font_name}', using system default")
                self.font = pygame.font.Font(None, 24)
            
            self.color = color or UI_COLORS['text_normal']
            self.center = center
            self.shadow = shadow
            self.shadow_color = shadow_color or UI_COLORS.get('shadow', (0, 0, 0))
            self.glow = glow
            self.glow_color = glow_color or UI_COLORS.get('glow', (255, 255, 255, 128))
            self.alpha = alpha
            self.scale = scale
            self.rotation = rotation
            self.outline = outline
            self.outline_color = outline_color or UI_COLORS.get('outline', (0, 0, 0))
            self.outline_width = outline_width
            self.visible = True
            self.effects = []
            
            # Initialize surfaces
            self.surface = None
            self.shadow_surface = None
            self.glow_surface = None
            self.rect = None
            self.shadow_rect = None
            self.glow_rect = None
            
            # Create initial surfaces
            self._create_surfaces()
            
        except Exception as e:
            print(f"Error initializing text: {e}")
            import traceback
            traceback.print_exc()
            # Set fallback values
            self.font = pygame.font.Font(None, 24)
            self.color = (255, 255, 255)
            self.surface = self.font.render(str(text), True, self.color)
            self.rect = self.surface.get_rect()
            if center:
                self.rect.center = pos
            else:
                self.rect.topleft = pos

    def _create_surfaces(self):
        """Create text surfaces with effects"""
        try:
            # Create main text surface
            self.surface = self.font.render(self.text, True, self.color)
            self.rect = self.surface.get_rect()
            
            if self.center:
                self.rect.center = self.pos
            else:
                self.rect.topleft = self.pos
                
            # Create shadow surface if enabled
            if self.shadow:
                self.shadow_surface = self.font.render(self.text, True, self.shadow_color)
                self.shadow_rect = self.shadow_surface.get_rect()
                shadow_offset = 2
                if self.center:
                    self.shadow_rect.center = (self.rect.centerx + shadow_offset,
                                             self.rect.centery + shadow_offset)
                else:
                    self.shadow_rect.topleft = (self.rect.x + shadow_offset,
                                              self.rect.y + shadow_offset)
                    
            # Create glow surface if enabled
            if self.glow:
                glow_size = 4
                glow_surface_size = (self.rect.width + glow_size * 2,
                                   self.rect.height + glow_size * 2)
                self.glow_surface = pygame.Surface(glow_surface_size, pygame.SRCALPHA)
                
                # Create multiple layers of glow
                for i in range(glow_size):
                    alpha = 30 - i * 5
                    glow_text = self.font.render(self.text, True,
                                               (*self.glow_color[:3], alpha))
                    for offset_x in range(-1, 2):
                        for offset_y in range(-1, 2):
                            pos = (glow_size + offset_x * i,
                                 glow_size + offset_y * i)
                            self.glow_surface.blit(glow_text, pos)
                            
                self.glow_rect = self.glow_surface.get_rect()
                if self.center:
                    self.glow_rect.center = self.rect.center
                else:
                    self.glow_rect.topleft = (self.rect.x - glow_size,
                                            self.rect.y - glow_size)
                    
        except Exception as e:
            print(f"Error creating text surfaces: {e}")
            import traceback
            traceback.print_exc()
            
    def update_position(self, pos):
        """Update text position"""
        try:
            self.pos = pos
            if self.center:
                self.rect.center = pos
            else:
                self.rect.topleft = pos
                
            # Update shadow position if enabled
            if self.shadow and self.shadow_rect:
                shadow_offset = 2
                if self.center:
                    self.shadow_rect.center = (self.rect.centerx + shadow_offset,
                                             self.rect.centery + shadow_offset)
                else:
                    self.shadow_rect.topleft = (self.rect.x + shadow_offset,
                                              self.rect.y + shadow_offset)
                    
            # Update glow position if enabled
            if self.glow and self.glow_rect:
                glow_size = 4
                if self.center:
                    self.glow_rect.center = self.rect.center
                else:
                    self.glow_rect.topleft = (self.rect.x - glow_size,
                                            self.rect.y - glow_size)
                    
        except Exception as e:
            print(f"Error updating text position: {e}")
            
    def update_text(self, text):
        """Update text content"""
        try:
            if self.text != str(text):
                self.text = str(text)
                self._create_surfaces()
        except Exception as e:
            print(f"Error updating text content: {e}")
            
    def draw(self, surface):
        """Draw text with all effects"""
        try:
            if not self.visible:
                return
                
            # Draw glow
            if self.glow and self.glow_surface and self.glow_rect:
                surface.blit(self.glow_surface, self.glow_rect)
                
            # Draw shadow
            if self.shadow and self.shadow_surface and self.shadow_rect:
                surface.blit(self.shadow_surface, self.shadow_rect)
                
            # Draw main text
            if self.surface and self.rect:
                surface.blit(self.surface, self.rect)
                
            # Draw any additional effects
            for effect in self.effects:
                effect.draw(surface, self.rect)
                
        except Exception as e:
            print(f"Error drawing text: {e}")
            import traceback
            traceback.print_exc()

    def set_text(self, text: str):
        """Update text content"""
        if str(text) != self.text:
            self.text = str(text)
            self._create_surfaces()

    def set_color(self, color: Tuple[int, int, int]):
        """Update text color"""
        if color != self.color:
            self.color = color
            self._create_surfaces()

    def set_position(self, pos: Tuple[int, int]):
        """Update text position"""
        self.pos = pos
        if self.center:
            self.rect.center = pos
        else:
            self.rect.topleft = pos

    def set_alpha(self, alpha: int):
        """Update text transparency"""
        if alpha != self.alpha:
            self.alpha = max(0, min(255, alpha))
            self._create_surfaces()

    def set_scale(self, scale: float):
        """Update text scale"""
        if scale != self.scale:
            self.scale = max(0.1, scale)
            self._create_surfaces()

    def set_rotation(self, rotation: float):
        """Update text rotation"""
        if rotation != self.rotation:
            self.rotation = rotation % 360
            self._create_surfaces()

    def set_outline(self, enabled: bool, color: Optional[Tuple[int, int, int]] = None):
        """Update text outline"""
        update_needed = False
        if enabled != self.outline:
            self.outline = enabled
            update_needed = True
        if color and color != self.outline_color:
            self.outline_color = color
            update_needed = True
        if update_needed:
            self._create_surfaces()

    def add_effect(self, effect):
        """Add a visual effect to the text"""
        self.effects.append(effect)

    def remove_effect(self, effect):
        """Remove a visual effect from the text"""
        if effect in self.effects:
            self.effects.remove(effect)

    def clear_effects(self):
        """Remove all visual effects"""
        self.effects.clear()

    def show(self):
        """Make text visible"""
        self.visible = True

    def hide(self):
        """Make text invisible"""
        self.visible = False

    def toggle_visibility(self):
        """Toggle text visibility"""
        self.visible = not self.visible

    def get_rect(self) -> pygame.Rect:
        """Get text rectangle"""
        return self.rect.copy()
    
    def get_size(self) -> Tuple[int, int]:
        """Get text dimensions"""
        return self.surface.get_size() if self.surface else (0, 0)
    
    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        """Check if point collides with text"""
        return self.rect.collidepoint(pos) if self.rect else False