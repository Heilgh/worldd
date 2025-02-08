import pygame
from typing import Optional, Tuple
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, SCREEN_STATES
from src.ui.screen import Screen

class PauseScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize pause screen"""
        super().__init__(screen_manager)
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu options
        self.options = [
            ('Resume', self._resume_game),
            ('Options', self._show_options),
            ('Save Game', self._save_game),
            ('Main Menu', self._return_to_menu),
            ('Quit Game', self._quit_game)
        ]
        
        self.selected_option = 0
        
    def update(self, dt: float):
        """Update screen state"""
        pass
        
    def draw(self, screen: pygame.Surface):
        """Draw the pause screen"""
        try:
            # Draw semi-transparent background
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            # Draw title
            title = "Game Paused"
            title_surface = self.font.render(title, True, UI_COLORS['text_highlight'])
            title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH/2, y=WINDOW_HEIGHT/4)
            screen.blit(title_surface, title_rect)
            
            # Draw menu options
            option_height = 40
            start_y = WINDOW_HEIGHT/2 - (len(self.options) * option_height)/2
            
            for i, (option_text, _) in enumerate(self.options):
                color = UI_COLORS['text_highlight'] if i == self.selected_option else UI_COLORS['text_normal']
                text_surface = self.font.render(option_text, True, color)
                text_rect = text_surface.get_rect(centerx=WINDOW_WIDTH/2, y=start_y + i * option_height)
                screen.blit(text_surface, text_rect)
                
        except Exception as e:
            print(f"Error drawing pause screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._resume_game()
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    _, action = self.options[self.selected_option]
                    action()
                    
        except Exception as e:
            print(f"Error handling event: {e}")
            
    def _resume_game(self):
        """Resume the game"""
        self.screen_manager.switch_to_screen(SCREEN_STATES['GAME'])
        
    def _show_options(self):
        """Show options menu"""
        self.screen_manager.switch_to_screen(SCREEN_STATES['OPTIONS'])
        
    def _save_game(self):
        """Save the current game"""
        # TODO: Implement save game functionality
        pass
        
    def _return_to_menu(self):
        """Return to main menu"""
        self.screen_manager.switch_to_screen(SCREEN_STATES['MAIN_MENU'])
        
    def _quit_game(self):
        """Quit the game"""
        self.screen_manager.quit_game() 