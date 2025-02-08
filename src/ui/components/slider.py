import pygame
from typing import Tuple, Callable
from src.constants import UI_COLORS, FONTS

class Slider:
    def __init__(self, label: str, pos: Tuple[int, int], size: Tuple[int, int],
                 min_value: float, max_value: float, default_value: float,
                 on_change: Callable[[float], None]):
        """Initialize slider component"""
        try:
            self.label = label
            self.pos = pos
            self.size = size
            self.min_value = min_value
            self.max_value = max_value
            self.value = default_value
            self.on_change = on_change
            
            # Calculate rects
            self._create_rects()
            
            # State
            self.is_dragging = False
            self.is_hovered = False
            self.needs_update = True
            
            # Create surfaces
            self._create_surfaces()
            
        except Exception as e:
            print(f"Error initializing slider: {e}")
            
    def _create_rects(self):
        """Create slider rects"""
        try:
            # Track rect (the line the handle moves along)
            self.track_rect = pygame.Rect(
                self.pos[0],
                self.pos[1] + self.size[1] // 2 - 2,
                self.size[0],
                4
            )
            
            # Handle rect (the draggable circle)
            handle_size = self.size[1]
            self.handle_rect = pygame.Rect(0, 0, handle_size, handle_size)
            self._update_handle_pos()
            
            # Label rect
            self.label_rect = pygame.Rect(
                self.pos[0],
                self.pos[1] - 25,
                self.size[0],
                20
            )
            
            # Value rect
            self.value_rect = pygame.Rect(
                self.track_rect.right - 40,
                self.track_rect.top - 25,
                40,
                20
            )
            
        except Exception as e:
            print(f"Error creating slider rects: {e}")
            
    def _create_surfaces(self):
        """Create text surfaces"""
        try:
            # Create label text
            self.label_surface = FONTS['normal'].render(
                self.label,
                True,
                UI_COLORS['text_normal']
            )
            
            # Create value text
            self._update_value_text()
            
        except Exception as e:
            print(f"Error creating slider surfaces: {e}")
            
    def update_position(self, pos: Tuple[int, int], size: Tuple[int, int] = None):
        """Update slider position and optionally size"""
        try:
            self.pos = pos
            if size:
                self.size = size
                
            # Recreate rects with new position/size
            self._create_rects()
            
            # Mark for update
            self.needs_update = True
            
        except Exception as e:
            print(f"Error updating slider position: {e}")
            
    def _update_handle_pos(self):
        """Update handle position based on current value"""
        try:
            value_ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
            handle_x = self.track_rect.left + (self.track_rect.width - self.handle_rect.width) * value_ratio
            self.handle_rect.centerx = handle_x
            self.handle_rect.centery = self.track_rect.centery
            
        except Exception as e:
            print(f"Error updating handle position: {e}")
            
    def _update_value_text(self):
        """Update value text surface"""
        try:
            self.value_surface = FONTS['small'].render(
                f"{int(self.value)}",
                True,
                UI_COLORS['text_normal']
            )
            
        except Exception as e:
            print(f"Error updating value text: {e}")
            
    def _set_value_from_pos(self, x_pos: int):
        """Set value based on handle position"""
        try:
            relative_x = max(0, min(x_pos - self.track_rect.left, self.track_rect.width))
            value_ratio = relative_x / self.track_rect.width
            new_value = self.min_value + (self.max_value - self.min_value) * value_ratio
            
            if new_value != self.value:
                self.value = new_value
                self._update_handle_pos()
                self._update_value_text()
                self.on_change(self.value)
                
        except Exception as e:
            print(f"Error setting slider value: {e}")
            
    def update(self, dt: float):
        """Update slider state"""
        try:
            if self.is_dragging:
                mouse_pos = pygame.mouse.get_pos()
                self._set_value_from_pos(mouse_pos[0])
                
            # Update hover state
            mouse_pos = pygame.mouse.get_pos()
            self.is_hovered = self.handle_rect.collidepoint(mouse_pos)
            
        except Exception as e:
            print(f"Error updating slider: {e}")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.handle_rect.collidepoint(event.pos):
                        self.is_dragging = True
                        return True
                    elif self.track_rect.collidepoint(event.pos):
                        self._set_value_from_pos(event.pos[0])
                        self.is_dragging = True
                        return True
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.is_dragging = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    self._set_value_from_pos(event.pos[0])
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error handling slider event: {e}")
            return False
            
    def draw(self, surface: pygame.Surface):
        """Draw slider"""
        try:
            # Draw label
            surface.blit(self.label_surface, self.label_rect)
            
            # Draw value
            surface.blit(self.value_surface, self.value_rect)
            
            # Draw track background
            track_color = UI_COLORS['slider_track_hover'] if self.is_hovered else UI_COLORS['slider_track']
            pygame.draw.rect(surface, track_color, self.track_rect, border_radius=2)
            
            # Draw filled portion of track
            filled_rect = self.track_rect.copy()
            filled_rect.width = self.handle_rect.centerx - filled_rect.left
            pygame.draw.rect(surface, UI_COLORS['slider_fill'], filled_rect, border_radius=2)
            
            # Draw handle with effects
            handle_color = UI_COLORS['slider_handle_active'] if self.is_dragging else (
                UI_COLORS['slider_handle_hover'] if self.is_hovered else UI_COLORS['slider_handle']
            )
            
            # Draw handle glow
            if self.is_hovered or self.is_dragging:
                glow_radius = self.handle_rect.width // 2 + 2
                pygame.draw.circle(
                    surface,
                    (*UI_COLORS['glow'][:3], 30),
                    self.handle_rect.center,
                    glow_radius
                )
                
            # Draw handle
            pygame.draw.circle(
                surface,
                handle_color,
                self.handle_rect.center,
                self.handle_rect.width // 2
            )
            
        except Exception as e:
            print(f"Error drawing slider: {e}") 