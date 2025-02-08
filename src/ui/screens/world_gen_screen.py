import pygame
import random
import math
import traceback
from typing import Optional, Dict, Any
from ...constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS,
    GRAPHICS_QUALITY, SCREEN_STATES
)
from ..components.text import Text
from ..components.progress_bar import ProgressBar
from ..screen import Screen
from ...world import World

class WorldGenScreen(Screen):
    def __init__(self, screen_manager):
        """Initialize the world generation screen"""
        super().__init__(screen_manager)
        self.world = None
        self.is_generating = False
        self.progress = 0.0
        self.status = "Preparing world generation..."
        self.generation_complete = False
        
        # Initialize progress bar with glow and shine effects
        bar_width = 400
        bar_height = 30
        self.progress_bar = ProgressBar(
            position=((WINDOW_WIDTH - bar_width) // 2, WINDOW_HEIGHT // 2),
            size=(bar_width, bar_height),
            show_percentage=True,
            show_glow=True,
            show_shine=True,
            show_pulse=True
        )
        
        # Initialize visual effects
        self.particles = []
        self.glow_intensity = 0.0
        self.glow_direction = 1
        
        # Create UI elements
        title_y = WINDOW_HEIGHT * 0.3
        
        # Title
        self.title = Text(
            text="Generating World",
            pos=(WINDOW_WIDTH // 2, title_y),
            font_name='title',
            color=UI_COLORS['text_highlight'],
            center=True,
            shadow=True,
            shadow_color=UI_COLORS['shadow'],
            glow=True,
            glow_color=UI_COLORS['glow']
        )
        
        # Status text
        self.status_text = Text(
            text=self.status,
            pos=(WINDOW_WIDTH // 2, title_y + 100),
            font_name='normal',
            color=UI_COLORS['text_normal'],
            center=True,
            shadow=True,
            shadow_color=UI_COLORS['shadow']
        )
        
        # Loading animation
        self.loading_dots = ""
        self.loading_timer = 0
        
        # Background effects
        self.glow_particles = []
        self._generate_particles(100)
        self._generate_glow_particles(20)
        
        # Generation steps
        self.generation_steps = [
            "Initializing world...",
            "Generating terrain...",
            "Creating biomes...",
            "Spawning entities...",
            "Initializing systems...",
            "Finalizing world..."
        ]
        self.current_step = 0

    def update(self, dt: float):
        """Update world generation progress"""
        try:
            if not self.is_generating and not self.generation_complete:
                self.start_generation()
                
            # Update progress bar and effects
            self.progress_bar.progress = self.progress
            self._update_effects(dt)
            
            # Check if generation is complete
            if self.generation_complete and not self.is_generating:
                # Ensure world is properly initialized
                if self.world and self.world.initialized:
                    # Set the world reference in the game
                    self.screen_manager.game.world = self.world
                    print("World generation complete, switching to game screen...")
                    self.screen_manager.switch_screen('game')
                    
        except Exception as e:
            print(f"Error updating world generation: {e}")
            traceback.print_exc()

    def start_generation(self):
        """Start world generation process"""
        try:
            if not self.is_generating:
                print("Starting world generation...")
                self.is_generating = True
                self.world = World()  # Create new world instance
                
                # Start generation in a separate thread
                import threading
                self.generation_thread = threading.Thread(
                    target=self._generate_world,
                    daemon=True
                )
                self.generation_thread.start()
                
        except Exception as e:
            print(f"Error starting world generation: {e}")
            traceback.print_exc()

    def _generate_world(self):
        """Generate world in separate thread"""
        try:
            if self.world.initialize_world(self._update_progress):
                self.generation_complete = True
                self.is_generating = False
                print("World generation completed successfully")
            else:
                print("World generation failed!")
                self.is_generating = False
                
        except Exception as e:
            print(f"Error during world generation: {e}")
            traceback.print_exc()
            self.is_generating = False

    def _update_progress(self, progress: float, status: str):
        """Update generation progress"""
        self.progress = progress
        self.status = status
        self.status_text.set_text(status)

    def on_enter(self, previous_screen: Optional[Screen] = None):
        """Called when entering this screen"""
        try:
            super().on_enter(previous_screen)
            print("Entering world generation screen...")
            
            # Reset progress
            self.progress = 0
            self.status = "Initializing..."
            self.generation_complete = False
            self.is_generating = False
            self.world = None
            
        except Exception as e:
            print(f"Error entering world gen screen: {e}")
            traceback.print_exc()

    def on_exit(self):
        """Called when exiting this screen"""
        try:
            super().on_exit()
            self.particles.clear()
            self.glow_particles.clear()
            
            # Ensure world reference is properly set
            if self.world and self.world.initialized:
                self.screen_manager.game.world = self.world
                
        except Exception as e:
            print(f"Error exiting world gen screen: {e}")
            traceback.print_exc()

    def draw(self, surface: pygame.Surface):
        """Draw generation screen"""
        try:
            # Fill background
            surface.fill(UI_COLORS['background'])
            
            # Draw glow particles
            for particle in self.glow_particles:
                color = (*particle['color'], int(particle['alpha']))
                pos = (
                    particle['x'] + math.cos(particle['angle']) * particle['radius'],
                    particle['y'] + math.sin(particle['angle']) * particle['radius']
                )
                pygame.draw.circle(
                    surface,
                    color,
                    (int(pos[0]), int(pos[1])),
                    particle['size']
                )
                
            # Draw regular particles
            for particle in self.particles:
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(
                    surface,
                    color,
                    (int(particle['x']), int(particle['y'])),
                    particle['size']
                )
                
            # Draw title with glow effect
            self.title.draw(surface)
            
            # Draw status
            self.status_text.draw(surface)
            
            # Draw progress bar with glow effect
            if self.progress > 0:
                self.progress_bar.set_progress(self.progress)
                self.progress_bar.draw(surface)
                
        except Exception as e:
            print(f"Error drawing generation screen: {e}")
            traceback.print_exc()

    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        try:
            if event.type == pygame.USEREVENT:
                if self.generation_complete:
                    self.screen_manager.switch_screen('game')
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.is_generating:
                        self.screen_manager.switch_screen('main_menu')
                        
        except Exception as e:
            print(f"Error handling event in world gen screen: {e}")
            traceback.print_exc()
            
    def update_progress(self, progress: float, status: str):
        """Update generation progress"""
        try:
            self.progress = progress
            self.status = status
            if hasattr(self, 'progress_bar'):
                self.progress_bar.set_progress(progress)
            if hasattr(self, 'status_text'):
                self.status_text.set_text(status)
                
            # Update current step based on progress
            step_size = 1.0 / len(self.generation_steps)
            self.current_step = min(len(self.generation_steps) - 1,
                                  int(progress / step_size))
                
            # Check for completion
            if progress >= 1.0 and not self.generation_complete:
                self.generation_complete = True
                self.status = "Generation Complete!"
                pygame.time.set_timer(pygame.USEREVENT, 1000)  # 1 second delay before transition
                
        except Exception as e:
            print(f"Error updating progress: {e}")
            traceback.print_exc()

    def _generate_particles(self, count: int = 20):
        """Generate background particles"""
        for _ in range(count):
            self.particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.randint(2, 5),
                'speed': random.randint(20, 50),
                'color': UI_COLORS['text_dim'][:3],
                'alpha': 255
            })
            
    def _generate_glow_particles(self, count: int = 5):
        """Generate glowing orbital particles"""
        for _ in range(count):
            self.glow_particles.append({
                'x': WINDOW_WIDTH // 2 + random.randint(-200, 200),
                'y': WINDOW_HEIGHT // 3 + random.randint(-100, 100),
                'size': random.randint(2, 4),
                'angle': random.random() * math.pi * 2,
                'speed': random.random() * 2 + 1,
                'base_radius': random.randint(20, 60),
                'radius': 0,
                'color': UI_COLORS['glow'][:3],
                'alpha': 255
            })

    def _update_effects(self, dt: float):
        """Update background effects"""
        # Update loading animation
        self.loading_timer += dt
        if self.loading_timer >= 0.5:
            self.loading_timer = 0
            self.loading_dots = "." * ((len(self.loading_dots) + 1) % 4)
            
        # Update particles
        for particle in self.particles[:]:
            particle['y'] += particle['speed'] * dt
            particle['alpha'] = max(0, particle['alpha'] - dt * 20)
            if particle['alpha'] <= 0:
                self.particles.remove(particle)
                
        # Update glow particles
        for particle in self.glow_particles[:]:
            particle['angle'] += particle['speed'] * dt
            particle['radius'] = particle['base_radius'] + math.sin(particle['angle']) * 20
            particle['alpha'] = max(0, min(255, 128 + math.sin(particle['angle']) * 64))
            
        # Generate new particles
        if len(self.particles) < 50:
            self._generate_particles(5)
        if len(self.glow_particles) < 10:
            self._generate_glow_particles(2)