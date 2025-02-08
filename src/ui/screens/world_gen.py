import pygame
import random
import math
import traceback
from typing import Optional, Dict, Any
from ...constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, FONTS,
    GRAPHICS_QUALITY, SCREEN_STATES, BUTTON_STYLES,
    WORLD_WIDTH, WORLD_HEIGHT, BIOME_COLORS, DAY_LENGTH,
    TILE_SIZE, CHUNK_SIZE, SEASON_ORDER, TIME_SPEEDS
)
import threading
from typing import Optional, Tuple

from ...world import World
from ..components.text import Text
from ..components.progress_bar import ProgressBar
from ..screen import Screen

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
                
                # Create new world instance
                self.world = World()
                
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
            # Create world generator
            from ...world.generation import WorldGenerator
            generator = WorldGenerator(self.world)
            
            # Generate world
            if generator.generate_world(self._update_progress):
                self.world.initialized = True
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
        print(f"Generation progress: {progress:.1f}% - {status}")

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
            
    def _draw_loading_animation(self, surface: pygame.Surface):
        """Draw the loading animation"""
        self.loading_timer += 1
        if self.loading_timer >= 60:  # 1 second delay
            self.loading_timer = 0
            self.loading_dots = "." if len(self.loading_dots) < 3 else ""
        
        loading_text = "Loading" + self.loading_dots
        text_surface = self.small_font.render(loading_text, True, UI_COLORS['text_highlight'])
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.7))
        surface.blit(text_surface, text_rect)
        
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
                'pulse_speed': random.uniform(1, 3),
                'pulse_offset': random.uniform(0, math.pi * 2)
            })
            
    def _update_particles(self, dt: float):
        """Update particle positions and effects"""
        # Update regular particles
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0] * dt
            particle['pos'][1] += particle['velocity'][1] * dt
            
            # Wrap around screen
            particle['pos'][0] = particle['pos'][0] % WINDOW_WIDTH
            particle['pos'][1] = particle['pos'][1] % WINDOW_HEIGHT
            
            # Update alpha
            particle['alpha'] = max(20, particle['alpha'] - dt * 20)
            
            # Regenerate if too faded
            if particle['alpha'] <= 20:
                self.particles.remove(particle)
                
        # Update glow particles
        for particle in self.glow_particles[:]:
            particle['pos'][0] += particle['velocity'][0] * dt
            particle['pos'][1] += particle['velocity'][1] * dt
            
            # Wrap around screen
            particle['pos'][0] = particle['pos'][0] % WINDOW_WIDTH
            particle['pos'][1] = particle['pos'][1] % WINDOW_HEIGHT
            
            # Pulse alpha
            particle['pulse_offset'] += particle['pulse_speed'] * dt
            particle['alpha'] = 20 + abs(math.sin(particle['pulse_offset'])) * 60
            
        # Generate new particles if needed
        if len(self.particles) < 50:
            self._generate_particles(5)
        if len(self.glow_particles) < 10:
            self._generate_glow_particles(2)
            
    def _draw_particles(self, surface: pygame.Surface):
        """Draw all particles"""
        # Draw glow particles first
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

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if self.is_generating:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to main menu on escape
                    self.game.switch_to_screen(SCREEN_STATES['MAIN_MENU'])
                elif event.key == pygame.K_RETURN and self.status.startswith("Error"):
                    # Retry generation on enter if there was an error
                    self.status = "Preparing world generation..."
                    self.progress = 0.0
                    self.is_generating = False
                    self.generation_complete = False
                    self.start_generation()
        else:
            if event.type == pygame.MOUSEMOTION:
                # Check button hover
                mouse_pos = event.pos
                self.button_hover = None
                for button_name, button_rect in self.buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        self.button_hover = button_name
                        break
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle button clicks
                mouse_pos = event.pos
                for button_name, button_rect in self.buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        if button_name == 'start':
                            self.start_generation()
                        elif button_name == 'back':
                            self.game.switch_to_screen(SCREEN_STATES['MAIN_MENU'])
                        break