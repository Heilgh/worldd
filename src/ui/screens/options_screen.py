import pygame
from typing import Optional, Dict
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, TIME_SPEEDS, SCREEN_STATES
from src.ui.screen import Screen
from src.ui.components.button import Button
from src.ui.components.text import Text

class OptionsScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize options screen"""
        super().__init__(screen_manager)
        self.settings = {
            'graphics_quality': 'high',
            'fullscreen': False,
            'sound_volume': 100,
            'music_volume': 100,
            'game_speed': 'normal',
            'show_thoughts': True,
            'show_debug': False
        }
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI elements"""
        try:
            # Create title
            self.title = Text(
                text="Options",
                pos=(WINDOW_WIDTH // 2, 80),
                font_name='title',
                color=UI_COLORS['text_highlight'],
                center=True,
                shadow=True,
                glow=True,
                glow_color=UI_COLORS['glow']
            )
            
            # Create buttons
            button_width = 400
            button_height = 50
            start_y = 180
            spacing = 70
            
            self.buttons = {}
            
            # Graphics Quality Button
            self.buttons['graphics'] = Button(
                text="Graphics Quality: High",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y),
                size=(button_width, button_height),
                callback=self._toggle_graphics,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Fullscreen Button
            self.buttons['fullscreen'] = Button(
                text="Fullscreen: Off",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing),
                size=(button_width, button_height),
                callback=self._toggle_fullscreen,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Sound Volume Button
            self.buttons['sound'] = Button(
                text="Sound Volume: 100%",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 2),
                size=(button_width, button_height),
                callback=self._toggle_sound,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Music Volume Button
            self.buttons['music'] = Button(
                text="Music Volume: 100%",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 3),
                size=(button_width, button_height),
                callback=self._toggle_music,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Game Speed Button
            self.buttons['speed'] = Button(
                text="Game Speed: Normal",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 4),
                size=(button_width, button_height),
                callback=self._toggle_speed,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Show Thoughts Button
            self.buttons['thoughts'] = Button(
                text="Show Thoughts: On",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 5),
                size=(button_width, button_height),
                callback=self._toggle_thoughts,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Show Debug Button
            self.buttons['debug'] = Button(
                text="Show Debug: Off",
                position=(WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 6),
                size=(button_width, button_height),
                callback=self._toggle_debug,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Apply Button
            self.buttons['apply'] = Button(
                text="Apply Changes",
                position=(WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT - 160),
                size=(button_width, button_height),
                callback=self._apply_settings,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Back Button
            self.buttons['back'] = Button(
                text="Back",
                position=(WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT - 80),
                size=(button_width, button_height),
                callback=self._on_back,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Load current settings
            self._load_current_settings()
            
        except Exception as e:
            print(f"Error initializing options screen UI: {e}")
            import traceback
            traceback.print_exc()
            
    def _load_current_settings(self):
        """Load current settings from game state"""
        try:
            if hasattr(self.screen_manager, 'game'):
                game = self.screen_manager.game
                
                # Load UI settings
                if hasattr(game, 'ui_system'):
                    self.settings['fullscreen'] = game.ui_system.fullscreen
                    self._update_button_text('fullscreen')
                
                # Load game settings
                if hasattr(game, 'settings'):
                    for key in self.settings:
                        if key in game.settings:
                            self.settings[key] = game.settings[key]
                            if key in self.buttons:
                                self._update_button_text(key)
                                
        except Exception as e:
            print(f"Error loading current settings: {e}")
            
    def _update_button_text(self, setting_key: str):
        """Update button text based on setting value"""
        try:
            if setting_key not in self.buttons:
                return
                
            if setting_key == 'graphics_quality':
                self.buttons[setting_key].text_str = f"Graphics Quality: {self.settings[setting_key].title()}"
            elif setting_key == 'fullscreen':
                self.buttons[setting_key].text_str = f"Fullscreen: {'On' if self.settings[setting_key] else 'Off'}"
            elif setting_key in ['sound_volume', 'music_volume']:
                self.buttons[setting_key].text_str = f"{setting_key.replace('_', ' ').title()}: {self.settings[setting_key]}%"
            elif setting_key == 'game_speed':
                self.buttons[setting_key].text_str = f"Game Speed: {self.settings[setting_key].title()}"
            elif setting_key in ['show_thoughts', 'show_debug']:
                self.buttons[setting_key].text_str = f"{setting_key.replace('_', ' ').title()}: {'On' if self.settings[setting_key] else 'Off'}"
                
            # Recreate button text
            self.buttons[setting_key]._create_text()
            
        except Exception as e:
            print(f"Error updating button text for {setting_key}: {e}")
            
    def _toggle_graphics(self):
        """Toggle graphics quality"""
        qualities = ['low', 'medium', 'high', 'ultra']
        current_index = qualities.index(self.settings['graphics_quality'])
        self.settings['graphics_quality'] = qualities[(current_index + 1) % len(qualities)]
        self._update_button_text('graphics_quality')
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self._update_button_text('fullscreen')
        
    def _toggle_sound(self):
        """Toggle sound volume"""
        self.settings['sound_volume'] = (self.settings['sound_volume'] + 10) % 110
        self._update_button_text('sound')
        
    def _toggle_music(self):
        """Toggle music volume"""
        self.settings['music_volume'] = (self.settings['music_volume'] + 10) % 110
        self._update_button_text('music')
        
    def _toggle_speed(self):
        """Toggle game speed"""
        speeds = list(TIME_SPEEDS.keys())
        current_index = speeds.index(self.settings['game_speed'])
        self.settings['game_speed'] = speeds[(current_index + 1) % len(speeds)]
        self._update_button_text('speed')
        
    def _toggle_thoughts(self):
        """Toggle thought bubbles display"""
        self.settings['show_thoughts'] = not self.settings['show_thoughts']
        self._update_button_text('thoughts')
        
    def _toggle_debug(self):
        """Toggle debug information"""
        self.settings['show_debug'] = not self.settings['show_debug']
        self._update_button_text('debug')
        
    def _apply_settings(self):
        """Apply current settings to game"""
        try:
            if hasattr(self.screen_manager, 'game'):
                game = self.screen_manager.game
                
                # Apply UI settings
                if hasattr(game, 'ui_system'):
                    if game.ui_system.fullscreen != self.settings['fullscreen']:
                        game.ui_system.toggle_fullscreen()
                
                # Apply game settings
                if not hasattr(game, 'settings'):
                    game.settings = {}
                    
                game.settings.update(self.settings)
                
                # Apply specific settings
                if hasattr(game, 'set_game_speed'):
                    game.set_game_speed(self.settings['game_speed'])
                    
                # Show confirmation
                game.ui_system.add_notification("Settings applied successfully", duration=2.0, type='success')
                    
        except Exception as e:
            print(f"Error applying settings: {e}")
            if hasattr(self.screen_manager.game, 'ui_system'):
                self.screen_manager.game.ui_system.add_notification("Error applying settings", duration=2.0, type='error')
        
    def _on_back(self):
        """Return to previous screen"""
        self.screen_manager.return_to_previous_screen()
        
    def update(self, dt: float):
        """Update options screen"""
        try:
            for button in self.buttons.values():
                button.update(dt)
                
        except Exception as e:
            print(f"Error updating options screen: {e}")
            
    def draw(self, surface: pygame.Surface):
        """Draw options screen"""
        try:
            # Fill background
            surface.fill(UI_COLORS['background'])
            
            # Draw title
            self.title.draw(surface)
            
            # Draw buttons
            for button in self.buttons.values():
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing options screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._on_back()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.buttons.values():
                        if button.rect.collidepoint(event.pos):
                            button.on_click()
                            break
                            
        except Exception as e:
            print(f"Error handling event: {e}") 