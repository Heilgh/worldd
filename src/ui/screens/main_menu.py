import pygame
import random
import math
import traceback
from typing import List, Tuple
from src.ui.screens.screen import Screen
from src.ui.components.button import Button
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS

class MainMenuScreen(Screen):
    def __init__(self, game):
        """Initialize the main menu screen"""
        super().__init__(game)
        
        try:
            print("Initializing main menu screen...")
            
            # Initialize fonts
            self._init_fonts()
            
            # Create buttons
            self._init_buttons()
            
            # Initialize particles for background effect
            self._init_particles()
            
            print("Main menu screen initialized")
            
        except Exception as e:
            print(f"Error initializing main menu screen: {e}")
            traceback.print_exc()
            
    def _init_fonts(self):
        """Initialize fonts"""
        try:
            # Title font
            self.title_font = pygame.font.Font(FONTS['title'], 72)
            
            # Button font
            self.button_font = pygame.font.Font(FONTS['ui'], 32)
            
        except Exception as e:
            print(f"Error initializing fonts: {e}")
            traceback.print_exc()
            
    def _init_buttons(self):
        """Initialize menu buttons"""
        try:
            # Calculate button dimensions and positions
            button_width = 300
            button_height = 60
            button_spacing = 20
            start_y = WINDOW_HEIGHT // 2
            
            # Create buttons
            self.buttons = [
                Button(
                    WINDOW_WIDTH // 2 - button_width // 2,
                    start_y,
                    button_width,
                    button_height,
                    "New Game",
                    self.button_font,
                    UI_COLORS['button'],
                    UI_COLORS['button_hover'],
                    UI_COLORS['text'],
                    self._on_new_game_click
                ),
                Button(
                    WINDOW_WIDTH // 2 - button_width // 2,
                    start_y + button_height + button_spacing,
                    button_width,
                    button_height,
                    "Options",
                    self.button_font,
                    UI_COLORS['button'],
                    UI_COLORS['button_hover'],
                    UI_COLORS['text'],
                    self._on_options_click
                ),
                Button(
                    WINDOW_WIDTH // 2 - button_width // 2,
                    start_y + (button_height + button_spacing) * 2,
                    button_width,
                    button_height,
                    "Quit",
                    self.button_font,
                    UI_COLORS['button'],
                    UI_COLORS['button_hover'],
                    UI_COLORS['text'],
                    self._on_quit_click
                )
            ]
            
        except Exception as e:
            print(f"Error initializing buttons: {e}")
            traceback.print_exc()
            
    def _init_particles(self):
        """Initialize background particles"""
        try:
            self.particles = []
            for _ in range(100):
                self.particles.append({
                    'x': random.randint(0, WINDOW_WIDTH),
                    'y': random.randint(0, WINDOW_HEIGHT),
                    'speed': random.uniform(20, 50),
                    'angle': random.uniform(0, 2 * math.pi),
                    'size': random.randint(2, 4),
                    'color': random.choice([
                        UI_COLORS['particle1'],
                        UI_COLORS['particle2'],
                        UI_COLORS['particle3']
                    ])
                })
                
        except Exception as e:
            print(f"Error initializing particles: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update the menu state"""
        try:
            # Update particles
            for particle in self.particles:
                # Move particle
                particle['x'] += math.cos(particle['angle']) * particle['speed'] * dt
                particle['y'] += math.sin(particle['angle']) * particle['speed'] * dt
                
                # Wrap around screen
                if particle['x'] < 0:
                    particle['x'] = WINDOW_WIDTH
                elif particle['x'] > WINDOW_WIDTH:
                    particle['x'] = 0
                    
                if particle['y'] < 0:
                    particle['y'] = WINDOW_HEIGHT
                elif particle['y'] > WINDOW_HEIGHT:
                    particle['y'] = 0
                    
                # Randomly change angle
                if random.random() < 0.01:
                    particle['angle'] += random.uniform(-0.5, 0.5)
                    
            # Update buttons
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                button.update(mouse_pos)
                
        except Exception as e:
            print(f"Error updating main menu: {e}")
            traceback.print_exc()
            
    def draw(self, surface: pygame.Surface):
        """Draw the menu"""
        try:
            # Fill background
            surface.fill(UI_COLORS['background'])
            
            # Draw particles
            for particle in self.particles:
                pygame.draw.circle(
                    surface,
                    particle['color'],
                    (int(particle['x']), int(particle['y'])),
                    particle['size']
                )
                
            # Draw title
            title_text = self.title_font.render("World Simulation", True, UI_COLORS['text'])
            title_rect = title_text.get_rect(centerx=WINDOW_WIDTH // 2, y=100)
            
            # Add shadow effect to title
            shadow_offset = 3
            title_shadow = self.title_font.render("World Simulation", True, UI_COLORS['text_shadow'])
            shadow_rect = title_rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            surface.blit(title_shadow, shadow_rect)
            surface.blit(title_text, title_rect)
            
            # Draw buttons
            for button in self.buttons:
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing main menu: {e}")
            traceback.print_exc()
            
    def handle_event(self, event: pygame.event.Event):
        """Handle an event"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button.is_clicked(mouse_pos):
                            button.click()
                            break
                            
        except Exception as e:
            print(f"Error handling event in main menu: {e}")
            traceback.print_exc()
            
    def _on_new_game_click(self):
        """Handle new game button click"""
        try:
            print("Starting new game...")
            self.game.start_new_game()
            
        except Exception as e:
            print(f"Error starting new game: {e}")
            traceback.print_exc()
            
    def _on_options_click(self):
        """Handle options button click"""
        try:
            print("Opening options menu...")
            # TODO: Implement options menu
            pass
            
        except Exception as e:
            print(f"Error opening options menu: {e}")
            traceback.print_exc()
            
    def _on_quit_click(self):
        """Handle quit button click"""
        try:
            print("Quitting game...")
            self.game.running = False
            
        except Exception as e:
            print(f"Error quitting game: {e}")
            traceback.print_exc() 