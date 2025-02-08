import pygame
from ..constants import UI_COLORS

class UIPanel:
    def __init__(self, x, y, width, height, title=None, icon=None):
        """Initialize panel"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.icon = icon
        self.visible = True
        self.hover = False
        self.active = False
        self.needs_update = True
        
        # Visual properties
        self.alpha = 230  # Panel transparency
        self.glow_alpha = 30  # Glow effect transparency
        self.glow_size = 10  # Size of glow effect
        self.border_radius = 5  # Rounded corners
        self.padding = 10  # Inner padding
        
        # Create rect for collision detection
        self.rect = pygame.Rect(x, y, width, height)
        
        # Initialize font
        self.font = pygame.font.Font(None, 24)
        
        # Create surfaces
        self.surface = None
        self.background = None
        self.glow_surface = None
        self._create_surfaces()
        
    def _create_surfaces(self):
        """Create panel surfaces"""
        try:
            # Create main surface
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create background surface with glow
            bg_width = self.width + self.glow_size * 2
            bg_height = self.height + self.glow_size * 2
            self.background = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            
            # Create glow surface
            self.glow_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            
            # Draw glow
            glow_rect = pygame.Rect(self.glow_size, self.glow_size, self.width, self.height)
            pygame.draw.rect(self.background, (*UI_COLORS['glow'][:3], self.glow_alpha), 
                           glow_rect, border_radius=self.border_radius)
            
            # Draw panel background with semi-transparency
            pygame.draw.rect(self.surface, (*UI_COLORS['panel_bg'][:3], 180),
                           self.surface.get_rect(), border_radius=self.border_radius)
            
            # Draw border
            pygame.draw.rect(self.surface, UI_COLORS['panel_border'],
                           self.surface.get_rect(), width=2, border_radius=self.border_radius)
            
            # Draw title if present
            if self.title:
                # Draw title background
                title_height = 30
                title_rect = pygame.Rect(0, 0, self.width, title_height)
                pygame.draw.rect(self.surface, (*UI_COLORS['panel_header'][:3], 200),
                               title_rect, border_radius=self.border_radius)
                
                # Draw title text with shadow
                title_text = f"{self.icon} {self.title}" if self.icon else self.title
                # Shadow
                title_shadow = self.font.render(title_text, True, (0, 0, 0))
                shadow_rect = title_shadow.get_rect(centerx=self.width // 2 + 1, centery=title_height // 2 + 1)
                self.surface.blit(title_shadow, shadow_rect)
                # Main text
                title_surface = self.font.render(title_text, True, UI_COLORS['text_highlight'])
                title_rect = title_surface.get_rect(centerx=self.width // 2, centery=title_height // 2)
                self.surface.blit(title_surface, title_rect)
                
        except Exception as e:
            print(f"Error creating panel surfaces: {e}")
            import traceback
            traceback.print_exc()
            
    def update(self, world, mouse_pos):
        """Update panel state"""
        try:
            # Update hover state
            old_hover = self.hover
            self.hover = self.rect.collidepoint(mouse_pos)
            
            # Animate alpha
            if self.hover:
                self.target_alpha = 220  # Reduced max alpha
            else:
                self.target_alpha = 180  # Reduced min alpha
                
            # Smooth alpha transition
            if self.alpha != self.target_alpha:
                diff = self.target_alpha - self.alpha
                self.alpha += int(diff * 0.1)  # Smooth transition
                
        except Exception as e:
            print(f"Error updating panel: {e}")
            
    def draw(self, screen, world=None):
        """Draw panel with visual effects"""
        try:
            if not self.visible:
                return
                
            # Draw glow effect when hovered
            if self.hover:
                glow_color = (*UI_COLORS['panel_glow'][:3], 20)  # Reduced glow opacity
                pygame.draw.rect(self.glow_surface, glow_color,
                               (self.glow_size, self.glow_size, self.width, self.height),
                               border_radius=self.border_radius + self.glow_size)
                screen.blit(self.glow_surface,
                          (self.x - self.glow_size, self.y - self.glow_size))
            
            # Draw panel background
            screen.blit(self.surface, self.rect)
            
            # Draw panel content if available
            if hasattr(self, 'draw_content'):
                self.draw_content(screen, world)
                
        except Exception as e:
            print(f"Error drawing panel: {e}")
            import traceback
            traceback.print_exc()
            
    def handle_event(self, event, world):
        """Handle panel events"""
        try:
            # Default event handling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    return True
            return False
            
        except Exception as e:
            print(f"Error handling panel event: {e}")
            return False
            
    def get_content_rect(self):
        """Get rectangle for content area (excluding title)"""
        if self.title:
            return pygame.Rect(
                self.x + self.padding,
                self.y + 25 + self.padding,  # Reduced title height
                self.width - self.padding * 2,
                self.height - 25 - self.padding * 2
            )
        return pygame.Rect(
            self.x + self.padding,
            self.y + self.padding,
            self.width - self.padding * 2,
            self.height - self.padding * 2
        )

    def update_position(self, x, y, width, height):
        """Update panel position and size"""
        try:
            # Update dimensions
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            
            # Update rect
            self.rect = pygame.Rect(x, y, width, height)
            
            # Recreate surfaces with new dimensions
            self._create_surfaces()
            
        except Exception as e:
            print(f"Error updating panel position: {e}")
            
    def _create_surfaces(self):
        """Create panel surfaces"""
        try:
            # Create main surface
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create background surface with glow
            bg_width = self.width + self.glow_size * 2
            bg_height = self.height + self.glow_size * 2
            self.background = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            
            # Create glow surface
            self.glow_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            
            # Draw glow
            glow_rect = pygame.Rect(self.glow_size, self.glow_size, self.width, self.height)
            pygame.draw.rect(self.background, (*UI_COLORS['glow'][:3], self.glow_alpha), 
                           glow_rect, border_radius=self.border_radius)
            
            # Draw panel background with semi-transparency
            pygame.draw.rect(self.surface, (*UI_COLORS['panel_bg'][:3], 180),
                           self.surface.get_rect(), border_radius=self.border_radius)
            
            # Draw border
            pygame.draw.rect(self.surface, UI_COLORS['panel_border'],
                           self.surface.get_rect(), width=2, border_radius=self.border_radius)
            
            # Draw title if present
            if self.title:
                # Draw title background
                title_height = 30
                title_rect = pygame.Rect(0, 0, self.width, title_height)
                pygame.draw.rect(self.surface, (*UI_COLORS['panel_header'][:3], 200),
                               title_rect, border_radius=self.border_radius)
                
                # Draw title text with shadow
                title_text = f"{self.icon} {self.title}" if self.icon else self.title
                # Shadow
                title_shadow = self.font.render(title_text, True, (0, 0, 0))
                shadow_rect = title_shadow.get_rect(centerx=self.width // 2 + 1, centery=title_height // 2 + 1)
                self.surface.blit(title_shadow, shadow_rect)
                # Main text
                title_surface = self.font.render(title_text, True, UI_COLORS['text_highlight'])
                title_rect = title_surface.get_rect(centerx=self.width // 2, centery=title_height // 2)
                self.surface.blit(title_surface, title_rect)
                
        except Exception as e:
            print(f"Error creating panel surfaces: {e}")
            import traceback
            traceback.print_exc()

    def draw(self, screen, world=None):
        """Draw panel with visual effects"""
        try:
            if not self.visible:
                return
                
            # Draw glow effect when hovered
            if self.hover:
                glow_color = (*UI_COLORS['panel_glow'][:3], 20)  # Reduced glow opacity
                pygame.draw.rect(self.glow_surface, glow_color,
                               (self.glow_size, self.glow_size, self.width, self.height),
                               border_radius=self.border_radius + self.glow_size)
                screen.blit(self.glow_surface,
                          (self.x - self.glow_size, self.y - self.glow_size))
            
            # Draw panel background
            screen.blit(self.surface, self.rect)
            
            # Draw panel content if available
            if hasattr(self, 'draw_content'):
                self.draw_content(screen, world)
                
        except Exception as e:
            print(f"Error drawing panel: {e}")
            import traceback
            traceback.print_exc() 