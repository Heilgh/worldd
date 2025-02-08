import pygame
from typing import Optional, Dict
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS
from src.ui.screen import Screen
from src.ui.components.button import Button
from src.ui.components.text import Text
from src.ui.components.slider import Slider

class SettingsScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize settings screen"""
        super().__init__(screen_manager)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI elements"""
        try:
            # Create title
            self.title = Text(
                "Settings",
                (WINDOW_WIDTH // 2, 80),
                UI_COLORS['text_highlight'],
                center=True,
                font_name='title',
                shadow=True,
                glow=True
            )
            
            # Create sliders and buttons
            slider_width = 300
            slider_height = 20
            start_y = 180
            spacing = 70
            
            self.sliders = {
                'graphics': Slider(
                    "Graphics Quality",
                    (WINDOW_WIDTH // 2 - slider_width // 2, start_y),
                    (slider_width, slider_height),
                    0, 3, 3,  # min, max, default (3 = high)
                    self._on_graphics_change
                ),
                'sound': Slider(
                    "Sound Volume",
                    (WINDOW_WIDTH // 2 - slider_width // 2, start_y + spacing),
                    (slider_width, slider_height),
                    0, 100, 100,
                    self._on_sound_change
                ),
                'music': Slider(
                    "Music Volume",
                    (WINDOW_WIDTH // 2 - slider_width // 2, start_y + spacing * 2),
                    (slider_width, slider_height),
                    0, 100, 100,
                    self._on_music_change
                )
            }
            
            # Create toggle buttons
            button_width = 200
            button_height = 40
            
            self.buttons = {
                'fullscreen': Button(
                    "Fullscreen: Off",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 3),
                    (button_width, button_height),
                    self._toggle_fullscreen
                ),
                'vsync': Button(
                    "VSync: On",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + spacing * 4),
                    (button_width, button_height),
                    self._toggle_vsync
                ),
                'back': Button(
                    "Back",
                    (WINDOW_WIDTH // 2 - button_width // 2, WINDOW_HEIGHT - 100),
                    (button_width, button_height),
                    self._on_back
                )
            }
            
            # Settings state
            self.settings = {
                'graphics_quality': 3,  # 0=low, 1=medium, 2=high, 3=ultra
                'sound_volume': 100,
                'music_volume': 100,
                'fullscreen': False,
                'vsync': True
            }
            
        except Exception as e:
            print(f"Error initializing settings screen UI: {e}")
            
    def update(self, dt: float):
        """Update settings screen"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update sliders
            for slider in self.sliders.values():
                slider.update(dt)
                
            # Update buttons
            for button in self.buttons.values():
                button.update(dt)
                
        except Exception as e:
            print(f"Error updating settings screen: {e}")
            
    def draw(self, surface: pygame.Surface):
        """Draw settings screen"""
        try:
            # Fill background
            surface.fill(UI_COLORS['background'])
            
            # Draw title
            self.title.draw(surface)
            
            # Draw sliders
            for slider in self.sliders.values():
                slider.draw(surface)
                
            # Draw buttons
            for button in self.buttons.values():
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing settings screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._on_back()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle slider clicks
                for slider in self.sliders.values():
                    if slider.handle_click(event.pos):
                        break
                        
                # Handle button clicks
                for button in self.buttons.values():
                    if button.rect.collidepoint(event.pos):
                        button.on_click()
                        break
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle slider release
                for slider in self.sliders.values():
                    slider.handle_release()
                    
            elif event.type == pygame.MOUSEMOTION:
                # Handle slider dragging
                for slider in self.sliders.values():
                    slider.handle_drag(event.pos)
                    
        except Exception as e:
            print(f"Error handling event: {e}")
            
    def _on_graphics_change(self, value: float):
        """Handle graphics quality change"""
        self.settings['graphics_quality'] = int(value)
        
    def _on_sound_change(self, value: float):
        """Handle sound volume change"""
        self.settings['sound_volume'] = int(value)
        
    def _on_music_change(self, value: float):
        """Handle music volume change"""
        self.settings['music_volume'] = int(value)
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        self.buttons['fullscreen'].text = f"Fullscreen: {'On' if self.settings['fullscreen'] else 'Off'}"
        
    def _toggle_vsync(self):
        """Toggle VSync"""
        self.settings['vsync'] = not self.settings['vsync']
        self.buttons['vsync'].text = f"VSync: {'On' if self.settings['vsync'] else 'Off'}"
        
    def _on_back(self):
        """Return to previous screen"""
        self.apply_settings()
        self.screen_manager.return_to_previous_screen()
        
    def apply_settings(self):
        """Apply current settings"""
        try:
            # Apply graphics quality
            quality_names = ['low', 'medium', 'high', 'ultra']
            quality = quality_names[self.settings['graphics_quality']]
            
            # Apply display settings
            if self.settings['fullscreen']:
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            else:
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
                
            # Apply VSync
            if hasattr(pygame, 'GL_SWAP_CONTROL'):
                pygame.GL_SWAP_CONTROL = self.settings['vsync']
                
            # TODO: Apply sound and music volume when audio system is implemented
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            
    def on_enter(self, previous_screen: Optional[Screen] = None):
        """Called when entering this screen"""
        super().on_enter(previous_screen)
        # Load current settings
        # TODO: Implement settings loading
        
    def on_exit(self):
        """Called when exiting this screen"""
        super().on_exit()
        # Save settings
        # TODO: Implement settings saving 