import pygame
from typing import Optional, Tuple, Dict
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, TIME_SPEEDS, SCREEN_STATES
from src.ui.screen import Screen

class OptionsScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize options screen"""
        super().__init__(screen_manager)
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Settings
        self.settings = {
            'sound_volume': 0.7,
            'music_volume': 0.5,
            'game_speed': 'normal',
            'show_fps': False,
            'fullscreen': False
        }
        
        # Menu options
        self.options = [
            ('Sound Volume', self._adjust_sound),
            ('Music Volume', self._adjust_music),
            ('Game Speed', self._adjust_speed),
            ('Show FPS', self._toggle_fps),
            ('Fullscreen', self._toggle_fullscreen),
            ('Back', self._return_to_previous)
        ]
        
        self.selected_option = 0
        self.adjusting = False
        
        # Store previous screen for return
        self.previous_screen = None
        
    def on_enter(self):
        """Called when entering this screen"""
        self.previous_screen = self.screen_manager.current_screen.__class__.__name__
        
    def update(self, dt: float):
        """Update screen state"""
        pass
        
    def draw(self, screen: pygame.Surface):
        """Draw the options screen"""
        try:
            # Fill background
            screen.fill(UI_COLORS['background'])
            
            # Draw title
            title = "Options"
            title_surface = self.font.render(title, True, UI_COLORS['text_highlight'])
            title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH/2, y=WINDOW_HEIGHT/4)
            screen.blit(title_surface, title_rect)
            
            # Draw options
            option_height = 50
            start_y = WINDOW_HEIGHT/2 - (len(self.options) * option_height)/2
            
            for i, (option_text, _) in enumerate(self.options):
                # Get current value for the option
                value = self._get_option_value(option_text)
                display_text = f"{option_text}: {value}" if value is not None else option_text
                
                # Determine color based on selection and adjustment state
                color = UI_COLORS['text_highlight'] if i == self.selected_option else UI_COLORS['text_normal']
                if i == self.selected_option and self.adjusting:
                    color = UI_COLORS['text_highlight']
                    display_text = f"> {display_text} <"
                
                # Render option
                text_surface = self.font.render(display_text, True, color)
                text_rect = text_surface.get_rect(centerx=WINDOW_WIDTH/2, y=start_y + i * option_height)
                screen.blit(text_surface, text_rect)
                
            # Draw controls help
            help_text = "Use arrow keys to navigate, Enter to select, Escape to return"
            help_surface = self.small_font.render(help_text, True, UI_COLORS['text_dim'])
            help_rect = help_surface.get_rect(centerx=WINDOW_WIDTH/2, bottom=WINDOW_HEIGHT-20)
            screen.blit(help_surface, help_rect)
            
        except Exception as e:
            print(f"Error drawing options screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        try:
            if event.type == pygame.KEYDOWN:
                if self.adjusting:
                    self._handle_adjustment(event)
                else:
                    if event.key == pygame.K_ESCAPE:
                        self._return_to_previous()
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        _, action = self.options[self.selected_option]
                        action()
                    
        except Exception as e:
            print(f"Error handling event: {e}")
            
    def _handle_adjustment(self, event: pygame.event.Event):
        """Handle adjustment of selected option"""
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
            self.adjusting = False
        elif event.key == pygame.K_LEFT:
            self._adjust_value(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_value(1)
            
    def _adjust_value(self, direction: int):
        """Adjust the value of the selected option"""
        option_name = self.options[self.selected_option][0]
        
        if option_name == 'Sound Volume':
            self.settings['sound_volume'] = max(0.0, min(1.0, self.settings['sound_volume'] + direction * 0.1))
        elif option_name == 'Music Volume':
            self.settings['music_volume'] = max(0.0, min(1.0, self.settings['music_volume'] + direction * 0.1))
        elif option_name == 'Game Speed':
            speeds = list(TIME_SPEEDS.keys())
            current_index = speeds.index(self.settings['game_speed'])
            new_index = (current_index + direction) % len(speeds)
            self.settings['game_speed'] = speeds[new_index]
            
    def _get_option_value(self, option_name: str) -> Optional[str]:
        """Get the current value for an option"""
        if option_name == 'Sound Volume':
            return f"{int(self.settings['sound_volume'] * 100)}%"
        elif option_name == 'Music Volume':
            return f"{int(self.settings['music_volume'] * 100)}%"
        elif option_name == 'Game Speed':
            return self.settings['game_speed'].title()
        elif option_name == 'Show FPS':
            return 'On' if self.settings['show_fps'] else 'Off'
        elif option_name == 'Fullscreen':
            return 'On' if self.settings['fullscreen'] else 'Off'
        return None
        
    def _adjust_sound(self):
        """Start adjusting sound volume"""
        self.adjusting = True
        
    def _adjust_music(self):
        """Start adjusting music volume"""
        self.adjusting = True
        
    def _adjust_speed(self):
        """Start adjusting game speed"""
        self.adjusting = True
        
    def _toggle_fps(self):
        """Toggle FPS display"""
        self.settings['show_fps'] = not self.settings['show_fps']
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        pygame.display.toggle_fullscreen()
        
    def _return_to_previous(self):
        """Return to the previous screen"""
        # Save settings before returning
        # TODO: Implement settings save functionality
        
        # Return to previous screen
        if self.previous_screen == 'MainMenuScreen':
            self.screen_manager.switch_to_screen(SCREEN_STATES['MAIN_MENU'])
        elif self.previous_screen == 'PauseScreen':
            self.screen_manager.switch_to_screen(SCREEN_STATES['PAUSE'])
        else:
            self.screen_manager.switch_to_screen(SCREEN_STATES['MAIN_MENU']) 