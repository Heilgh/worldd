import pygame
import random
import math
from typing import Optional
from ...constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS
from ..components.button import Button
from ..components.text import Text
from ..screen import Screen
import traceback

class PauseScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize pause screen"""
        super().__init__(screen_manager)
        
        # Initialize attributes
        self.particles = []
        self.glow_particles = []
        self.buttons = {}
        self.title = None
        
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
                "Game Paused",
                (WINDOW_WIDTH // 2, 120),
                'title',
                UI_COLORS['text_highlight'],
                center=True,
                shadow=True,
                shadow_color=UI_COLORS['shadow'],
                glow=True,
                glow_color=UI_COLORS['glow']
            )
            
            # Create buttons
            button_width = 200
            button_height = 50
            button_margin = 20
            start_y = WINDOW_HEIGHT // 2 - 50
            
            self.buttons = {
                'resume': Button(
                    "Resume",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y),
                    (button_width, button_height),
                    self._on_resume
                ),
                'options': Button(
                    "Options",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + button_height + button_margin),
                    (button_width, button_height),
                    self._on_options
                ),
                'quit': Button(
                    "Quit to Menu",
                    (WINDOW_WIDTH // 2 - button_width // 2, start_y + (button_height + button_margin) * 2),
                    (button_width, button_height),
                    self._on_quit
                )
            }
            
        except Exception as e:
            print(f"Error initializing pause menu UI: {e}")
            
    def update(self, dt: float):
        """Update pause screen state"""
        try:
            # Update particles
            for particle in self.particles[:]:
                particle['pos'][0] += particle['velocity'][0] * dt
                particle['pos'][1] += particle['velocity'][1] * dt
                particle['alpha'] = max(0, particle['alpha'] - dt * 20)
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
                
            # Update buttons
            for button in self.buttons.values():
                button.update(dt)
                
        except Exception as e:
            print(f"Error updating pause screen: {e}")
            
    def draw(self, surface: pygame.Surface):
        """Draw pause screen"""
        try:
            # Draw game screen with blur effect
            if hasattr(self.screen_manager, 'previous_screen'):
                self.screen_manager.previous_screen.draw(surface)
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(128)
                surface.blit(overlay, (0, 0))
                
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
                
            # Draw title
            if self.title:
                self.title.draw(surface)
                
            # Draw buttons
            for button in self.buttons.values():
                button.draw(surface)
                
        except Exception as e:
            print(f"Error drawing pause screen: {e}")
            
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._on_resume()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for button in self.buttons.values():
                        if button.rect.collidepoint(event.pos):
                            button.on_click()
                            break
                            
        except Exception as e:
            print(f"Error handling pause screen event: {e}")
            
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
            
    def _on_resume(self):
        """Resume the game"""
        self.screen_manager.switch_screen('game')
        
    def _on_options(self):
        """Open options screen"""
        self.screen_manager.switch_screen('options')
        
    def _on_quit(self):
        """Quit to main menu"""
        self.screen_manager.switch_screen('main_menu')
        
    def on_enter(self, previous_screen: Optional[Screen] = None):
        """Called when entering pause screen"""
        try:
            super().on_enter(previous_screen)
            self.particles.clear()
            self.glow_particles.clear()
            self._generate_particles(20)
            self._generate_glow_particles(5)
            
            # Set game screen pause state
            if previous_screen and hasattr(previous_screen, 'paused'):
                previous_screen.paused = True
                if hasattr(previous_screen, 'pause_button'):
                    previous_screen.pause_button.text = "▶"
                    previous_screen.pause_button.bg_color = UI_COLORS['button_hover']
                    
        except Exception as e:
            print(f"Error entering pause screen: {e}")
            traceback.print_exc()
            
    def on_exit(self):
        """Called when exiting pause screen"""
        try:
            super().on_exit()
            self.particles.clear()
            self.glow_particles.clear()
            
            # Reset game screen pause state
            if self.screen_manager.current_screen and hasattr(self.screen_manager.current_screen, 'paused'):
                self.screen_manager.current_screen.paused = False
                if hasattr(self.screen_manager.current_screen, 'pause_button'):
                    self.screen_manager.current_screen.pause_button.text = "||"
                    self.screen_manager.current_screen.pause_button.bg_color = UI_COLORS['button_bg']
                    
        except Exception as e:
            print(f"Error exiting pause screen: {e}")
            traceback.print_exc() 