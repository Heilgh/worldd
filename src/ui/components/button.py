import pygame
import traceback
import math
from typing import Tuple, Callable, Optional
from ...constants import UI_COLORS, FONTS, BUTTON_STYLES
from ..components.text import Text

class Button:
    def __init__(self, text, position, size, callback,
                 text_color=UI_COLORS['button_text'],
                 bg_color=UI_COLORS['button_bg'],
                 hover_color=UI_COLORS['button_hover'],
                 font_name='button'):
        """Initialize button component with enhanced visual effects"""
        try:
            self.text_str = text
            self.position = position
            self.size = size
            self.callback = callback
            self.text_color = text_color
            self.bg_color = bg_color
            self.hover_color = hover_color
            self.font_name = font_name
            
            self.rect = pygame.Rect(position, size)
            self.is_hovered = False
            self.enabled = True
            self.pulse_value = 0
            self.transition_value = 0
            self.style = BUTTON_STYLES['normal']
            
            # Create text component with enhanced effects
            self._create_text()
            
            # Create surfaces
            self._update_surfaces()
            
        except Exception as e:
            print(f"Error initializing button: {e}")
            
    def _create_text(self):
        """Create text component"""
        try:
            text_x = self.position[0] + self.size[0] // 2
            text_y = self.position[1] + self.size[1] // 2
            
            # Create Text component
            self.text = Text(
                text=self.text_str,
                pos=(text_x, text_y),
                font_name=self.font_name,
                color=self.text_color,
                center=True,
                shadow=True,
                glow=True,
                glow_color=UI_COLORS['button_glow']
            )
            
        except Exception as e:
            print(f"Error creating button text: {e}")
            traceback.print_exc()
            
    def update_position(self, position, size=None):
        """Update button position and optionally size"""
        try:
            self.position = position
            if size:
                self.size = size
                
            # Update rect
            self.rect = pygame.Rect(position, self.size)
            
            # Update text position
            text_x = position[0] + self.size[0] // 2
            text_y = position[1] + self.size[1] // 2
            self.text.update_position((text_x, text_y))
            
            # Update surfaces
            self._update_surfaces()
            
        except Exception as e:
            print(f"Error updating button position: {e}")
            
    def _update_surfaces(self):
        """Update button surfaces with enhanced visual effects"""
        try:
            # Create normal surface
            self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            
            # Draw base button with rounded corners
            pygame.draw.rect(self.surface, self.bg_color, 
                           (0, 0, *self.rect.size), 
                           border_radius=self.style['border_radius'])
            
            # Add border
            if self.style['border_width'] > 0:
                pygame.draw.rect(self.surface, self.style['border_color'],
                               (0, 0, *self.rect.size),
                               border_radius=self.style['border_radius'],
                               width=self.style['border_width'])
            
            # Create hover surface with glow
            self.hover_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            
            # Draw base hover button
            pygame.draw.rect(self.hover_surface, self.hover_color,
                           (0, 0, *self.rect.size),
                           border_radius=self.style['border_radius'])
            
            # Add enhanced glow effect
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), 
                                        pygame.SRCALPHA)
            glow_color = self.style['glow_color']
            for i in range(5):
                alpha = 30 - i * 5
                pygame.draw.rect(glow_surface,
                               (*UI_COLORS['glow'][:3], alpha),
                               (i, i, self.rect.width + 20 - 2*i, 
                                self.rect.height + 20 - 2*i),
                               border_radius=self.style['border_radius'] + 5)
            
            # Add shadow
            shadow_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            shadow_offset = self.style['shadow_offset']
            pygame.draw.rect(shadow_surface,
                           self.style['shadow_color'],
                           (shadow_offset, shadow_offset,
                            self.rect.width - shadow_offset,
                            self.rect.height - shadow_offset),
                           border_radius=self.style['border_radius'])
            
            # Combine effects
            self.hover_surface.blit(glow_surface, (-10, -10))
            self.surface.blit(shadow_surface, (0, 0))
            self.hover_surface.blit(shadow_surface, (0, 0))
            
        except Exception as e:
            print(f"Error updating button surfaces: {e}")
            traceback.print_exc()
            
    def update(self, dt):
        """Update button state and animations"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled
            
            # Update hover transition
            if self.is_hovered:
                self.transition_value = min(1.0, self.transition_value + dt / self.style['transition_speed'])
            else:
                self.transition_value = max(0.0, self.transition_value - dt / self.style['transition_speed'])
            
            # Update pulse effect
            if self.style['pulse_effect'] and self.is_hovered:
                self.pulse_value = (self.pulse_value + dt * 3) % (math.pi * 2)
            
            # Update style based on state
            if not self.enabled:
                self.style = BUTTON_STYLES['disabled']
            elif self.is_hovered:
                self.style = BUTTON_STYLES['hover']
            else:
                self.style = BUTTON_STYLES['normal']
                
            if was_hovered != self.is_hovered:
                self._update_surfaces()
                
        except Exception as e:
            print(f"Error updating button: {e}")
            
    def draw(self, surface):
        """Draw the button with all visual effects"""
        try:
            # Calculate pulse scale
            pulse_scale = 1.0
            if self.style['pulse_effect'] and self.is_hovered:
                pulse_scale = 1.0 + math.sin(self.pulse_value) * 0.02
            
            # Calculate scaled rect
            scaled_width = int(self.rect.width * pulse_scale)
            scaled_height = int(self.rect.height * pulse_scale)
            scaled_x = self.rect.x + (self.rect.width - scaled_width) // 2
            scaled_y = self.rect.y + (self.rect.height - scaled_height) // 2
            
            # Draw interpolated between normal and hover states
            if self.transition_value > 0:
                # Draw normal state
                surface.blit(pygame.transform.scale(self.surface, (scaled_width, scaled_height)),
                           (scaled_x, scaled_y))
                
                # Draw hover state with alpha
                hover_surface = pygame.transform.scale(self.hover_surface, 
                                                     (scaled_width, scaled_height))
                hover_surface.set_alpha(int(255 * self.transition_value))
                surface.blit(hover_surface, (scaled_x, scaled_y))
            else:
                # Draw normal state only
                surface.blit(pygame.transform.scale(self.surface, (scaled_width, scaled_height)),
                           (scaled_x, scaled_y))
            
            # Draw text
            self.text.draw(surface)
            
        except Exception as e:
            print(f"Error drawing button: {e}")
            traceback.print_exc()
            
    def on_click(self):
        """Handle button click with visual feedback"""
        try:
            if self.enabled and self.callback:
                self.style = BUTTON_STYLES['pressed']
                self._update_surfaces()
                self.callback()
        except Exception as e:
            print(f"Error handling button click: {e}")
            traceback.print_exc()
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False
        
    def _lerp_color(self, color1: Tuple[int, int, int],
                    color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Linearly interpolate between two colors"""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
        
    def set_enabled(self, enabled: bool):
        """Set button enabled state"""
        if self.enabled != enabled:
            self.enabled = enabled
            if not enabled:
                self.is_hovered = False
                self.style = BUTTON_STYLES['disabled']
            else:
                self.style = BUTTON_STYLES['normal']
            self._update_surfaces() 