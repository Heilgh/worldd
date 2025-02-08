import pygame
import random
import math
from typing import Optional, List, Dict
from ...constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS
from ..components.button import Button
from ..components.text import Text
from ..screen import Screen
import traceback

class MainMenuScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize main menu screen"""
        super().__init__(screen_manager)
        
        # Initialize attributes
        self.particles = []
        self.glow_particles = []
        self.title_alpha = 0
        self.title_target_alpha = 255
        self.fade_speed = 200  # Alpha per second
        self.buttons = {}  # Initialize empty buttons dict
        self.title = None
        self.subtitle = None
        
        # Create UI elements
        self._init_ui()
        
        # Generate initial particles
        self._generate_particles(20)
        self._generate_glow_particles(5)
        
    def _init_ui(self):
        """Initialize UI elements"""
        try:
            # Create title text
            self.title = Text(
                "World Simulation",
                (WINDOW_WIDTH // 2, 120),
                font_name='title',
                color=UI_COLORS['title_text'],
                center=True,
                shadow=True,
                shadow_color=UI_COLORS['title_shadow'],
                glow=True,
                glow_color=UI_COLORS['title_glow']
            )
            
            # Create subtitle
            self.subtitle = Text(
                "A Living World Awaits",
                (WINDOW_WIDTH // 2, 180),
                font_name='normal',
                color=UI_COLORS['text_normal'],
                center=True,
                shadow=True
            )
            
            # Create buttons
            button_width = 200
            button_height = 50
            button_spacing = 20
            start_y = WINDOW_HEIGHT // 2
            
            self.buttons = {
                'new_game': Button(
                    "New Game",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y),
                    (button_width, button_height),
                    self._on_new_game,
                    text_color=UI_COLORS['button_text'],
                    bg_color=UI_COLORS['button_bg'],
                    hover_color=UI_COLORS['button_hover']
                ),
                'options': Button(
                    "Options",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing),
                    (button_width, button_height),
                    self._on_options,
                    text_color=UI_COLORS['button_text'],
                    bg_color=UI_COLORS['button_bg'],
                    hover_color=UI_COLORS['button_hover']
                ),
                'quit': Button(
                    "Quit",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing)),
                    (button_width, button_height),
                    self._on_quit,
                    text_color=UI_COLORS['button_text'],
                    bg_color=UI_COLORS['button_bg'],
                    hover_color=UI_COLORS['button_hover']
                )
            }
            
            print("Main menu UI initialized successfully")
            
        except Exception as e:
            print(f"Error initializing main menu UI: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update menu state"""
        try:
            # Update particles
            for particle in self.particles[:]:
                particle['pos'][0] += particle['velocity'][0] * dt
                particle['pos'][1] += particle['velocity'][1] * dt
                particle['alpha'] = max(0, particle['alpha'] - dt * 50)
                if particle['alpha'] <= 0:
                    self.particles.remove(particle)
                    
            # Update glow particles
            for particle in self.glow_particles[:]:
                particle['pos'][0] += particle['velocity'][0] * dt
                particle['pos'][1] += particle['velocity'][1] * dt
                particle['alpha'] = max(0, min(255, 128 + math.sin(particle['time']) * 64))
                particle['time'] += dt
                
            # Generate new particles
            if len(self.particles) < 50:
                self._generate_particles(5)
            if len(self.glow_particles) < 10:
                self._generate_glow_particles(2)
                
            # Update title fade
            if self.title_alpha < self.title_target_alpha:
                self.title_alpha = min(self.title_target_alpha,
                                     self.title_alpha + self.fade_speed * dt)
                
            # Update buttons
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons.values():
                button.update(dt)
                
        except Exception as e:
            print(f"Error updating main menu: {e}")
            
    def draw(self, surface: pygame.Surface):
        """Draw menu screen"""
        try:
            # Fill background
            surface.fill(UI_COLORS['background'])
            
            # Draw glow particles
            for particle in self.glow_particles:
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(
                    surface,
                    color,
                    (int(particle['pos'][0]), int(particle['pos'][1])),
                    particle['size']
                )
                
            # Draw regular particles
            for particle in self.particles:
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(
                    surface,
                    color,
                    (int(particle['pos'][0]), int(particle['pos'][1])),
                    particle['size']
                )
                
            # Draw title with fade effect
            if self.title:
                self.title.set_alpha(int(self.title_alpha))
                self.title.draw(surface)
                
            # Draw subtitle
            if self.subtitle:
                self.subtitle.set_alpha(int(self.title_alpha))
                self.subtitle.draw(surface)
                
            # Draw buttons
            for button in self.buttons.values():
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing main menu: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.buttons.values():
                        if button.rect.collidepoint(event.pos):
                            button.on_click()
                            break
                            
        except Exception as e:
            print(f"Error handling main menu event: {e}")
            
    def _generate_particles(self, count: int = 20):
        """Generate background particles"""
        for _ in range(count):
            self.particles.append({
                'pos': [random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)],
                'velocity': [random.uniform(-20, 20), random.uniform(-20, 20)],
                'size': random.randint(2, 4),
                'color': UI_COLORS['text_dim'][:3],
                'alpha': random.randint(50, 150)
            })
            
    def _generate_glow_particles(self, count: int = 5):
        """Generate glowing particles"""
        for _ in range(count):
            self.glow_particles.append({
                'pos': [random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)],
                'velocity': [random.uniform(-10, 10), random.uniform(-10, 10)],
                'size': random.randint(20, 40),
                'color': UI_COLORS['glow'][:3],
                'alpha': random.randint(20, 40),
                'time': random.random() * math.pi * 2
            })
            
    def _on_new_game(self):
        """Handle new game button click"""
        try:
            print("Starting new game...")
            # First transition to world gen screen
            self.screen_manager.switch_screen('world_gen')
        except Exception as e:
            print(f"Error starting new game: {e}")
            traceback.print_exc()
        
    def _on_options(self):
        """Open options screen"""
        self.screen_manager.switch_screen('options')
        
    def _on_quit(self):
        """Quit the game"""
        self.screen_manager.quit_game()
        
    def on_enter(self, previous_screen: Optional[Screen] = None):
        """Called when entering main menu"""
        super().on_enter(previous_screen)
        self.title_alpha = 0
        self.particles.clear()
        self.glow_particles.clear()
        self._generate_particles(20)
        self._generate_glow_particles(5)
        
    def on_exit(self):
        """Called when exiting main menu"""
        super().on_exit()
        self.particles.clear()
        self.glow_particles.clear()