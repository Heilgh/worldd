import pygame
import math
from typing import Tuple, Optional
from ...constants import UI_COLORS, FONTS

class ProgressBar:
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int],
                 bg_color: Tuple[int, int, int] = UI_COLORS['progress_bar'],
                 fill_color: Tuple[int, int, int] = UI_COLORS['progress_bar_fill'],
                 border_color: Tuple[int, int, int] = UI_COLORS['progress_bar_border'],
                 text_color: Tuple[int, int, int] = UI_COLORS['text_highlight'],
                 show_percentage: bool = True,
                 show_glow: bool = True,
                 show_shine: bool = True,
                 show_pulse: bool = True):
        """Initialize progress bar with enhanced visual effects"""
        self.rect = pygame.Rect(position, size)
        self.progress = 0.0
        self.target_progress = 0.0
        self.transition_speed = 3.0  # Units per second
        
        # Colors
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.text_color = text_color
        
        # Visual effects
        self.show_percentage = show_percentage
        self.show_glow = show_glow
        self.show_shine = show_shine
        self.show_pulse = show_pulse
        self.pulse_value = 0.0
        self.shine_offset = 0.0
        
        # Create font for percentage text
        self.font = FONTS['small']  # Use predefined small font
        
        # Create surfaces
        self._create_surfaces()
        
    def _create_surfaces(self):
        """Create all surfaces needed for rendering"""
        try:
            # Background surface
            self.bg_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(self.bg_surface, 
                           UI_COLORS['progress_bar_background'],
                           (0, 0, *self.rect.size),
                           border_radius=5)
            
            # Fill surface template
            self.fill_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            
            # Glow surface
            if self.show_glow:
                self.glow_surface = pygame.Surface((self.rect.width + 20, 
                                                  self.rect.height + 20),
                                                 pygame.SRCALPHA)
                for i in range(5):
                    alpha = 20 - i * 3
                    pygame.draw.rect(self.glow_surface,
                                   (*UI_COLORS['progress_bar_glow'][:3], alpha),
                                   (i, i, 
                                    self.rect.width + 20 - 2*i,
                                    self.rect.height + 20 - 2*i),
                                   border_radius=8)
            
            # Shine gradient
            if self.show_shine:
                self.shine_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                for i in range(self.rect.height):
                    alpha = int(15 * math.sin(i / self.rect.height * math.pi))
                    pygame.draw.line(self.shine_surface,
                                   (*UI_COLORS['progress_bar_shine'][:3], alpha),
                                   (0, i), (self.rect.width, i))
                    
        except Exception as e:
            print(f"Error creating progress bar surfaces: {e}")
            import traceback
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update progress bar animations"""
        try:
            # Smooth progress transition
            if self.progress != self.target_progress:
                diff = self.target_progress - self.progress
                change = self.transition_speed * dt
                if abs(diff) <= change:
                    self.progress = self.target_progress
                else:
                    self.progress += math.copysign(change, diff)
                    
            # Update pulse animation
            if self.show_pulse:
                self.pulse_value = (self.pulse_value + dt * 2) % (math.pi * 2)
                
            # Update shine animation
            if self.show_shine:
                self.shine_offset = (self.shine_offset + dt * 30) % (self.rect.width * 2)
                
        except Exception as e:
            print(f"Error updating progress bar: {e}")
            import traceback
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface):
        """Draw progress bar with all effects"""
        try:
            # Draw background
            surface.blit(self.bg_surface, self.rect)
            
            # Draw glow effect
            if self.show_glow:
                glow_rect = self.glow_surface.get_rect(center=self.rect.center)
                surface.blit(self.glow_surface, glow_rect)
            
            # Calculate fill width
            fill_width = int(self.rect.width * self.progress)
            
            # Draw progress fill
            if fill_width > 0:
                # Create fill surface
                fill_surface = pygame.Surface((fill_width, self.rect.height), 
                                           pygame.SRCALPHA)
                
                # Draw base fill
                pygame.draw.rect(fill_surface, self.fill_color,
                               (0, 0, fill_width, self.rect.height),
                               border_radius=5)
                
                # Add pulse effect
                if self.show_pulse and self.progress < 1.0:
                    pulse_alpha = int(20 + 10 * math.sin(self.pulse_value))
                    pulse_surface = pygame.Surface((fill_width, self.rect.height),
                                                pygame.SRCALPHA)
                    pygame.draw.rect(pulse_surface,
                                   (*UI_COLORS['progress_bar_pulse'][:3], pulse_alpha),
                                   (0, 0, fill_width, self.rect.height),
                                   border_radius=5)
                    fill_surface.blit(pulse_surface, (0, 0))
                
                # Add shine effect
                if self.show_shine:
                    shine_x = int(self.shine_offset - self.rect.width)
                    fill_surface.blit(self.shine_surface, (shine_x, 0))
                
                # Draw fill surface
                surface.blit(fill_surface, self.rect)
            
            # Draw border
            pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=5)
            
            # Draw percentage text
            if self.show_percentage:
                text = f"{int(self.progress * 100)}%"
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
                
        except Exception as e:
            print(f"Error drawing progress bar: {e}")
            import traceback
            traceback.print_exc()
            
    def set_progress(self, value: float):
        """Set target progress value (0-1)"""
        self.target_progress = max(0.0, min(1.0, value))
        
    def get_progress(self) -> float:
        """Get current progress value"""
        return self.progress