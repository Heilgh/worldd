import pygame
from typing import Optional, Dict
from ...constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS, GRAPHICS_QUALITY
from ..screen import Screen
from ...world import World
import traceback
from ..components.text import Text
from ..components.button import Button
from ..components.progress_bar import ProgressBar
from ..ui_system import UISystem
from ..panels import InfoPanel, TimePanel, StatsPanel, MinimapPanel, EntityListPanel

class GameScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize game screen"""
        super().__init__(screen_manager)
        self.world = None
        self.paused = False
        self.show_debug = False
        self.initialized = False
        self.graphics_settings = GRAPHICS_QUALITY['ultra']
        self.particles = []
        self.glow_effects = []
        self.weather_effects = []
        self.ui_elements = {}
        self.fonts = {}
        self.ui_system = None
        
        # Initialize resources
        self._init_resources()

    def _init_resources(self):
        """Initialize game screen resources"""
        try:
            print("Initializing game screen resources...")
            
            # Initialize UI system
            self.ui_system = UISystem()
            
            # Create pause button
            self.pause_button = Button(
                text="||",
                position=(WINDOW_WIDTH - 50, 10),
                size=(40, 40),
                callback=self._on_pause,
                text_color=UI_COLORS['button_text'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
            
            # Initialize UI elements
            self._init_ui()
            
            self.initialized = True
            print("Game screen resources initialized successfully")
            
        except Exception as e:
            print(f"Error initializing game screen resources: {e}")
            traceback.print_exc()

    def _init_ui(self):
        """Initialize UI elements"""
        try:
            # Create UI panels
            panel_height = 40
            self.ui_elements = {
                'top_panel': pygame.Rect(0, 0, WINDOW_WIDTH, panel_height),
                'bottom_panel': pygame.Rect(0, WINDOW_HEIGHT - panel_height, WINDOW_WIDTH, panel_height),
                'status_panel': pygame.Rect(10, 50, 200, 150)
            }
            
            # Create FPS counter
            self.fps_text = Text(
                text="FPS: 60",
                pos=(20, 20),
                font_name='small',
                color=UI_COLORS['text_dim'],
                center=False,
                shadow=True
            )
            
            # Create time display
            self.time_text = Text(
                text="Day 1 - 00:00",
                pos=(WINDOW_WIDTH // 2, 20),
                font_name='normal',
                color=UI_COLORS['text_normal'],
                center=True,
                shadow=True
            )
            
            # Create weather info text
            self.weather_text = Text(
                text="Weather: Clear",
                pos=(200, 20),
                font_name='normal',
                color=UI_COLORS['text_normal'],
                center=False,
                shadow=True
            )
            
            print("UI elements initialized successfully")
            
        except Exception as e:
            print(f"Error initializing UI: {e}")
            traceback.print_exc()

    def _on_world_progress(self, progress: float, status: str):
        """Handle world generation progress updates"""
        try:
            if self.ui_elements.get('progress_text'):
                self.ui_elements['progress_text'].set_text(f"Generating world: {status} ({int(progress * 100)}%)")
        except Exception as e:
            print(f"Error updating progress: {e}")
            traceback.print_exc()
            
    def _init_fonts(self):
        """Initialize fonts for UI elements"""
        try:
            # Use built-in pygame default font
            self.fonts = {
                'ui': pygame.font.Font(None, 20),
                'title': pygame.font.Font(None, 36),
                'debug': pygame.font.Font(None, 16),
                'status': pygame.font.Font(None, 24)
            }
            print("Fonts initialized successfully")
            
        except Exception as e:
            print(f"Error initializing fonts: {e}")
            
    def update(self, dt: float):
        """Update game screen state"""
        try:
            if not self.initialized:
                self._init_resources()
                
            # Always update UI elements regardless of pause state
            if hasattr(self, 'pause_button'):
                self.pause_button.update(dt)
                
            # Update world and game logic only if not paused
            if self.world and self.world.initialized and not self.paused:
                # Get input state
                input_state = self._get_input_state()
                
                # Update world with input state
                self.world.update(dt, input_state)
                
                # Update UI system
                if self.ui_system:
                    self.ui_system.update(self.world, dt)
                    
        except Exception as e:
            print(f"Error updating game screen: {e}")
            traceback.print_exc()
            
    def _get_input_state(self) -> Dict:
        """Get current input state"""
        try:
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()
            
            return {
                'camera_left': keys[pygame.K_LEFT] or keys[pygame.K_a],
                'camera_right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
                'camera_up': keys[pygame.K_UP] or keys[pygame.K_w],
                'camera_down': keys[pygame.K_DOWN] or keys[pygame.K_s],
                'zoom_in': keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS],
                'zoom_out': keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS],
                'mouse_pos': mouse_pos,
                'mouse_left': mouse_buttons[0],
                'mouse_right': mouse_buttons[2],
                'pause': keys[pygame.K_ESCAPE],
                'speed_up': keys[pygame.K_PERIOD],
                'speed_down': keys[pygame.K_COMMA],
                'toggle_debug': keys[pygame.K_F3]
            }
            
        except Exception as e:
            print(f"Error getting input state: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface):
        """Draw the game screen"""
        try:
            if not self.initialized:
                self._init_resources()
                
            # Clear screen with sky color
            surface.fill((135, 206, 235))  # Sky blue background
            
            # Draw world if available
            if self.world and self.world.initialized:
                # Draw world terrain and entities
                self.world.draw(surface)
                
                # Draw UI system on top
                if self.ui_system:
                    self.ui_system.draw(surface, self.world)
                
                # Draw pause button on top
                if hasattr(self, 'pause_button'):
                    self.pause_button.draw(surface)
                
                # Draw debug info if enabled
                if self.show_debug:
                    self._draw_debug_info(surface)
            else:
                # Draw loading message if world is not ready
                loading_text = self.ui_system.font.render("Loading World...", True, UI_COLORS['text_highlight'])
                text_rect = loading_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
                # Draw text shadow
                shadow_text = self.ui_system.font.render("Loading World...", True, (0, 0, 0))
                shadow_rect = shadow_text.get_rect(center=(WINDOW_WIDTH/2 + 2, WINDOW_HEIGHT/2 + 2))
                surface.blit(shadow_text, shadow_rect)
                surface.blit(loading_text, text_rect)
                
        except Exception as e:
            print(f"Error drawing game screen: {e}")
            traceback.print_exc()
            
    def _draw_ui(self, surface: pygame.Surface):
        """Draw UI elements"""
        try:
            # Draw panels
            for panel in self.ui_elements.values():
                pygame.draw.rect(surface, UI_COLORS['panel_bg'], panel)
                pygame.draw.rect(surface, UI_COLORS['panel_border'], panel, 1)
                
            # Draw pause button
            if hasattr(self, 'pause_button'):
                self.pause_button.draw(surface)
            
            # Draw FPS counter
            if hasattr(self, 'fps_text'):
                self.fps_text.draw(surface)
            
            # Draw time display
            if hasattr(self, 'time_text'):
                self.time_text.draw(surface)
            
            # Draw weather info
            if hasattr(self, 'weather_text') and self.world and hasattr(self.world, 'weather_system'):
                weather = self.world.weather_system.current_weather.capitalize()
                self.weather_text.set_text(f"Weather: {weather}")
                self.weather_text.draw(surface)
                
        except Exception as e:
            print(f"Error drawing UI: {e}")
            
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information"""
        try:
            if not self.world:
                return
                
            debug_y = 50
            line_height = 20
            
            debug_info = [
                f"FPS: {int(self.screen_manager.game.clock.get_fps())}",
                f"Entities: {len(self.world.entities)}",
                f"Active Chunks: {len(self.world.active_chunks)}",
                f"Camera: ({int(self.world.camera['x'])}, {int(self.world.camera['y'])})",
                f"Zoom: {self.world.camera['zoom']:.2f}",
                f"Active Entities: {len([e for e in self.world.entities if e.active])}"
            ]
            
            # Draw debug panel background
            panel_rect = pygame.Rect(5, 45, 200, len(debug_info) * line_height + 10)
            pygame.draw.rect(surface, (*UI_COLORS['panel_bg'][:3], 200), panel_rect)
            pygame.draw.rect(surface, UI_COLORS['panel_border'], panel_rect, 1)
            
            for text in debug_info:
                # Draw text shadow
                shadow_surface = self.ui_system.font.render(text, True, (0, 0, 0))
                surface.blit(shadow_surface, (11, debug_y + 1))
                # Draw text
                text_surface = self.ui_system.font.render(text, True, UI_COLORS['text_highlight'])
                surface.blit(text_surface, (10, debug_y))
                debug_y += line_height
                
        except Exception as e:
            print(f"Error drawing debug info: {e}")
            traceback.print_exc()
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.paused:
                        self._on_pause()  # Unpause if already paused
                    else:
                        self.screen_manager.switch_screen('pause')  # Switch to pause screen if not paused
                elif event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_SPACE:
                    self._on_pause()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if hasattr(self, 'pause_button') and self.pause_button.rect.collidepoint(event.pos):
                        self._on_pause()
                        return True  # Prevent event from propagating
                        
            # Pass events to world if not paused
            if self.world and not self.paused:
                self.world.handle_event(event)
                
        except Exception as e:
            print(f"Error handling event: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up screen resources"""
        try:
            if self.world:
                self.world.cleanup()
                self.world = None
                
            self.fonts.clear()
            self.ui_elements.clear()
            self.initialized = False
            
        except Exception as e:
            print(f"Error cleaning up game screen: {e}")
            traceback.print_exc()
            
    def on_enter(self, previous_screen: Optional[Screen] = None):
        """Called when entering this screen"""
        try:
            super().on_enter(previous_screen)
            print("Entering game screen...")
            
            # Initialize resources first
            if not self.initialized:
                self._init_resources()
            
            # Get world reference from game
            self.world = self.screen_manager.game.world
            if not self.world or not self.world.initialized:
                print("World not initialized, returning to world gen screen...")
                self.screen_manager.switch_screen('world_gen')
                return
                
            print("Got world reference from game")
            
            # Handle pause state when returning from pause screen
            if previous_screen and previous_screen.__class__.__name__ == 'PauseScreen':
                self.paused = False
                if hasattr(self, 'pause_button'):
                    self.pause_button.text = "||"
                    self.pause_button.bg_color = UI_COLORS['button_bg']
            
            # Initialize time system if needed
            if hasattr(self.world, 'time_system'):
                time_system = self.world.time_system
                if isinstance(time_system, dict):
                    time_system['paused'] = self.paused  # Set time system pause state
                else:
                    time_system.paused = self.paused
            else:
                print("Warning: World has no time system!")
                
        except Exception as e:
            print(f"Error entering game screen: {e}")
            traceback.print_exc()
            
    def on_exit(self):
        """Called when exiting this screen"""
        try:
            super().on_exit()
            if self.world and hasattr(self.world, 'time_system'):
                time_system = self.world.time_system
                if isinstance(time_system, dict):
                    time_system['paused'] = True
                else:
                    time_system.paused = True
                    
        except Exception as e:
            print(f"Error exiting game screen: {e}")
            traceback.print_exc()
        
    def _on_pause(self):
        """Toggle game pause state"""
        try:
            self.paused = not self.paused
            
            # Update pause button appearance
            if hasattr(self, 'pause_button'):
                self.pause_button.text = "▶" if self.paused else "||"
                self.pause_button.bg_color = UI_COLORS['button_hover'] if self.paused else UI_COLORS['button_bg']
            
            # Update time system pause state
            if self.world and hasattr(self.world, 'time_system'):
                time_system = self.world.time_system
                if isinstance(time_system, dict):
                    time_system['paused'] = self.paused
                else:
                    time_system.paused = self.paused
                    
        except Exception as e:
            print(f"Error toggling pause state: {e}")
            traceback.print_exc()
        
    def _update_weather_effects(self, weather: str, dt: float):
        """Update weather visual effects"""
        pass  # Implement weather effects
        
    def _update_particles(self, dt: float):
        """Update particle effects"""
        pass  # Implement particle effects
        
    def _update_glow_effects(self, dt: float):
        """Update glow effects"""
        pass  # Implement glow effects
        
    def _draw_weather_effects(self, surface: pygame.Surface):
        """Draw weather effects"""
        pass  # Implement weather effects drawing
        
    def _draw_particles(self, surface: pygame.Surface):
        """Draw particle effects"""
        pass  # Implement particle drawing
        
    def _draw_glow_effects(self, surface: pygame.Surface):
        """Draw glow effects"""
        pass  # Implement glow effects drawing 