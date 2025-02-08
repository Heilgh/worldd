import pygame
from ...constants import UI_COLORS

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x, y, 20, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.text = text
        self.font = pygame.font.Font(None, 24)
        self.dragging = False
        
        # Update handle position
        self._update_handle()
        
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, UI_COLORS['slider_bg'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['panel_border'], self.rect, 2)
        
        # Draw filled portion
        fill_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.handle_rect.centerx - self.rect.x,
            self.rect.height
        )
        pygame.draw.rect(screen, UI_COLORS['slider_fill'], fill_rect)
        
        # Draw handle with hover effect
        handle_color = UI_COLORS['slider_handle']
        if self.dragging:
            handle_color = UI_COLORS['button_active']
        elif self.handle_rect.collidepoint(pygame.mouse.get_pos()):
            handle_color = UI_COLORS['button_hover']
            
        pygame.draw.rect(screen, handle_color, self.handle_rect)
        pygame.draw.rect(screen, UI_COLORS['panel_border'], self.handle_rect, 2)
        
        # Draw value label with shadow for better visibility
        value_text = f"{self.text}: {self.value:.1f}"
        # Draw shadow
        shadow = self.font.render(value_text, True, (0, 0, 0))
        screen.blit(shadow, (self.rect.x + 1, self.rect.y - 24))
        # Draw text
        label = self.font.render(value_text, True, UI_COLORS['text_highlight'])
        screen.blit(label, (self.rect.x, self.rect.y - 25))
        
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.dragging = True
            self._update_value(pos[0])
            return True
        return False
        
    def handle_release(self):
        self.dragging = False
        
    def handle_motion(self, pos):
        if self.dragging:
            self._update_value(pos[0])
            
    def get_value(self):
        return self.value
        
    def _update_value(self, x):
        # Calculate value based on position
        relative_x = max(self.rect.left, min(x, self.rect.right))
        percentage = (relative_x - self.rect.left) / self.rect.width
        self.value = round(self.min_value + (self.max_value - self.min_value) * percentage, 1)
        self._update_handle()
        
    def _update_handle(self):
        # Update handle position based on value
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        self.handle_rect.centerx = self.rect.left + (self.rect.width * percentage)
        self.handle_rect.centery = self.rect.centery 