import pygame
import math
from ..panel import UIPanel
from ..components.button import Button
from ...constants import UI_COLORS, SEASONS, TIME_SPEEDS, SEASON_ORDER, FONTS

class TimePanel(UIPanel):
    def __init__(self, x, y, width, height, title="Time & Weather", icon="⏰"):
        super().__init__(x, y, width, height, title, icon)
        
        # Initialize colors
        self.text_color = UI_COLORS['text_normal']
        self.bg_color = UI_COLORS['panel_bg']
        self.border_color = UI_COLORS['panel_border']
        
        # Initialize time text
        self.time_text = "Day 1 - 00:00"
        self.season_text = "Season: Spring"
        self.weather_text = "Weather: Clear"
        self.temperature_text = "Temperature: 20.0°C"
        
        # Initialize time control buttons
        button_size = 30
        button_margin = 5
        button_y = self.y + 35
        
        self.buttons = {
            'pause': Button(
                text="⏸️",
                position=(self.x + 10, button_y),
                size=(button_size, button_size),
                callback=self._toggle_pause,
                text_color=UI_COLORS['text_normal'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            ),
            'speed_down': Button(
                text="⏪",
                position=(self.x + 10 + button_size + button_margin, button_y),
                size=(button_size, button_size),
                callback=self._decrease_speed,
                text_color=UI_COLORS['text_normal'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            ),
            'speed_up': Button(
                text="⏩",
                position=(self.x + 10 + (button_size + button_margin) * 2, button_y),
                size=(button_size, button_size),
                callback=self._increase_speed,
                text_color=UI_COLORS['text_normal'],
                bg_color=UI_COLORS['button_bg'],
                hover_color=UI_COLORS['button_hover']
            )
        }
        
        # Initialize fonts
        self.font = FONTS['normal']
        self.small_font = FONTS['small']
        
        # World reference
        self.world = None
        
    def initialize(self, world):
        """Initialize panel with world reference"""
        self.world = world
        
    def _toggle_pause(self):
        """Toggle game pause state"""
        if self.world:
            self.world.toggle_pause()
            self.buttons['pause'].text = "▶️" if self.world.time_system.paused else "⏸️"
        
    def _decrease_speed(self):
        """Decrease game speed"""
        if not self.world:
            return
            
        current_speed = self.world.time_system.speed
        speeds = list(TIME_SPEEDS.values())
        current_index = speeds.index(current_speed)
        if current_index > 0:
            speed_name = list(TIME_SPEEDS.keys())[current_index - 1]
            self.world.set_time_speed(speed_name)
        
    def _increase_speed(self):
        """Increase game speed"""
        if not self.world:
            return
            
        current_speed = self.world.time_system.speed
        speeds = list(TIME_SPEEDS.values())
        current_index = speeds.index(current_speed)
        if current_index < len(speeds) - 1:
            speed_name = list(TIME_SPEEDS.keys())[current_index + 1]
            self.world.set_time_speed(speed_name)
        
    def update(self, world, dt: float):
        """Update time panel"""
        try:
            if not world or not hasattr(world, 'time_system'):
                return
                
            time_system = world.time_system
            
            # Update time text
            self.time_text = f"Day {time_system.day} - {time_system.hour:02d}:{time_system.minute:02d}"
            
            # Update season text
            self.season_text = f"Season: {time_system.get_current_season()}"
            
            # Update weather text if available
            if hasattr(world, 'weather_system'):
                self.weather_text = f"Weather: {world.weather_system.current_weather.capitalize()}"
                self.temperature_text = f"Temperature: {getattr(world, 'temperature', 20):.1f}°C"
            
        except Exception as e:
            print(f"Error updating time panel: {e}")
            import traceback
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface, world):
        """Draw time panel"""
        try:
            # Draw panel background
            super().draw(surface)
            
            if not world or not hasattr(world, 'time_system'):
                return
                
            # Calculate text positions
            text_x = self.x + 10
            text_y = self.y + 40  # Start below title
            line_spacing = 25
            
            # Draw time text with shadow for better visibility
            def draw_text_with_shadow(text, y_pos):
                # Draw shadow
                shadow_surface = self.font.render(text, True, (0, 0, 0))
                surface.blit(shadow_surface, (text_x + 1, y_pos + 1))
                # Draw text
                text_surface = self.font.render(text, True, UI_COLORS['text_highlight'])
                surface.blit(text_surface, (text_x, y_pos))
                return y_pos + line_spacing
            
            # Draw each text line
            current_y = text_y
            current_y = draw_text_with_shadow(self.time_text, current_y)
            current_y = draw_text_with_shadow(self.season_text, current_y)
            current_y = draw_text_with_shadow(self.weather_text, current_y)
            current_y = draw_text_with_shadow(self.temperature_text, current_y)
            
            # Draw time control buttons
            for button in self.buttons.values():
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing time panel: {e}")
            import traceback
            traceback.print_exc() 