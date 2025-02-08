import pygame
import math
from ...constants import (
    ENTITY_TYPES, UI_COLORS, TILE_SIZE,
    ANIMAL_TYPES  # Add ANIMAL_TYPES import
)
import random
from typing import Dict, Optional, Tuple
import traceback

class Entity:
    def __init__(self, world, x: float, y: float):
        """Initialize entity"""
        self.world = world
        self.x = float(x)
        self.y = float(y)
        self.id = f"entity_{id(self)}"
        self.type = 'entity'
        self.subtype = None
        
        # Basic attributes
        self.size = TILE_SIZE
        self.speed = 0
        self.active = True
        self.needs_update = True
        
        # Visual properties
        self.sprite = '❓'  # Default unknown entity sprite
        self.color = (100, 100, 100)
        self.outline_color = (50, 50, 50)
        self.scale = 1.0
        self.alpha = 255
        
        # State tracking
        self.state = 'idle'
        self.velocity = [0, 0]
        self.target = None
        self.path = []
        
        # Position tracking for chunk updates
        self.last_x = self.x
        self.last_y = self.y
        
        # Initialize surface
        self.surface = None
        self._init_surface()
        
    def _init_surface(self):
        """Initialize entity surface with sprite"""
        try:
            # Get sprite based on type/subtype
            if hasattr(self, 'type') and self.type in ENTITY_TYPES:
                self.sprite = ENTITY_TYPES[self.type].get('sprite', '❓')
            elif hasattr(self, 'subtype') and self.subtype in ANIMAL_TYPES:
                self.sprite = ANIMAL_TYPES[self.subtype].get('sprite', '🐾')
                
            # Create surface for sprite
            font_size = int(self.size * 0.8)  # Slightly smaller than entity size
            try:
                font = pygame.font.SysFont('segoe ui emoji', font_size)
            except:
                font = pygame.font.Font(None, font_size)  # Fallback to default font
                
            # Render sprite
            text_surface = font.render(self.sprite, True, (0, 0, 0))
            
            # Create entity surface with alpha
            self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Center sprite on surface
            x = (self.size - text_surface.get_width()) // 2
            y = (self.size - text_surface.get_height()) // 2
            
            # Draw background circle
            pygame.draw.circle(self.surface, self.color,
                             (self.size // 2, self.size // 2),
                             self.size // 2)
            pygame.draw.circle(self.surface, self.outline_color,
                             (self.size // 2, self.size // 2),
                             self.size // 2, 2)
                             
            # Draw sprite
            self.surface.blit(text_surface, (x, y))
            
            self.needs_update = False
            print(f"Initialized surface for entity {self.id} with sprite {self.sprite}")
            
        except Exception as e:
            print(f"Error initializing entity surface: {e}")
            traceback.print_exc()
            
    def update(self, world, dt: float):
        """Update entity state"""
        try:
            # Update position based on velocity
            self.x += self.velocity[0] * self.speed * dt
            self.y += self.velocity[1] * self.speed * dt
            
            # Update surface if needed
            if self.needs_update:
                self._init_surface()
                
        except Exception as e:
            print(f"Error updating entity: {e}")
            traceback.print_exc()
            
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw entity on screen"""
        try:
            # Calculate screen position
            screen_x = int((self.x - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Skip if off screen (with padding)
            padding = max(100, self.size * zoom)
            if (screen_x + padding < 0 or 
                screen_x - padding > WINDOW_WIDTH or
                screen_y + padding < 0 or 
                screen_y - padding > WINDOW_HEIGHT):
                return
                
            # Draw entity surface
            if self.surface:
                try:
                    # Scale surface based on zoom and entity scale
                    scaled_size = int(self.size * zoom * self.scale)
                    if scaled_size > 0:
                        scaled_surface = pygame.transform.scale(self.surface, (scaled_size, scaled_size))
                        
                        # Apply alpha if needed
                        if self.alpha < 255:
                            scaled_surface.set_alpha(self.alpha)
                        
                        # Draw centered at screen position
                        screen.blit(scaled_surface, 
                                  (screen_x - scaled_size // 2,
                                   screen_y - scaled_size // 2))
                        
                        # Draw health bar if entity has health
                        if hasattr(self, 'health') and hasattr(self, 'max_health'):
                            self._draw_health_bar(screen, screen_x, screen_y, scaled_size)
                        
                        # Draw status effects
                        if hasattr(self, 'status_effects'):
                            self._draw_status_effects(screen, screen_x, screen_y, scaled_size)
                        
                        # Draw selection highlight if selected
                        if hasattr(self, 'selected') and self.selected:
                            pygame.draw.circle(screen, (255, 255, 0),
                                            (screen_x, screen_y),
                                            int(scaled_size / 2 + 4), 2)
                                            
                except Exception as e:
                    print(f"Error scaling/drawing entity surface: {e}")
                    traceback.print_exc()
                
        except Exception as e:
            print(f"Error drawing entity: {e}")
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up entity resources"""
        try:
            if self.surface:
                self.surface = None
        except Exception as e:
            print(f"Error cleaning up entity: {e}")
            import traceback
            traceback.print_exc()
            
    def _update_physics(self, dt):
        """Update position based on physics"""
        # Apply acceleration
        self.velocity['x'] += self.acceleration['x'] * dt
        self.velocity['y'] += self.acceleration['y'] * dt
        
        # Apply friction
        self.velocity['x'] *= self.friction
        self.velocity['y'] *= self.friction
        
        # Limit speed
        speed = (self.velocity['x']**2 + self.velocity['y']**2)**0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.velocity['x'] *= scale
            self.velocity['y'] *= scale
            
        # Update position
        self.x += self.velocity['x'] * dt
        self.y += self.velocity['y'] * dt
        
    def _constrain_to_world(self):
        """Keep entity within world bounds"""
        if self.world:
            world_width = getattr(self.world, 'width', 1000)
            world_height = getattr(self.world, 'height', 1000)
            
            # Keep x position in bounds
            self.x = max(0, min(self.x, world_width - self.size))
            
            # Keep y position in bounds
            self.y = max(0, min(self.y, world_height - self.size))
            
    def draw(self, surface, position, size):
        """Draw the entity on the given surface"""
        try:
            if not self.surface:
                self._init_surface()
                
            # Draw entity shape
            if self.type == 'circle':
                pygame.draw.circle(
                    surface,
                    self.color,
                    position,
                    size // 2
                )
                # Draw outline
                pygame.draw.circle(
                    surface,
                    self.outline_color,
                    position,
                    size // 2,
                    max(1, int(size * 0.1))  # Outline thickness scales with size
                )
            elif self.type == 'rect':
                rect = pygame.Rect(
                    position[0] - size // 2,
                    position[1] - size // 2,
                    size,
                    size
                )
                pygame.draw.rect(surface, self.color, rect)
                # Draw outline
                pygame.draw.rect(
                    surface,
                    self.outline_color,
                    rect,
                    max(1, int(size * 0.1))  # Outline thickness scales with size
                )
                
            # Draw health bar if entity has health
            if hasattr(self, 'health') and hasattr(self, 'specs') and 'max_health' in self.specs:
                health_pct = self.health / self.specs['max_health']
                bar_width = size
                bar_height = max(2, size // 8)
                bar_y_offset = size // 2 + bar_height
                
                # Background
                pygame.draw.rect(
                    surface,
                    (200, 0, 0),  # Dark red
                    (position[0] - bar_width//2,
                     position[1] + bar_y_offset,
                     bar_width,
                     bar_height)
                )
                
                # Health bar
                if health_pct > 0:
                    pygame.draw.rect(
                        surface,
                        (0, 200, 0),  # Green
                        (position[0] - bar_width//2,
                         position[1] + bar_y_offset,
                         int(bar_width * health_pct),
                         bar_height)
                    )
                    
            # Draw status effects
            if hasattr(self, 'status_effects'):
                effect_size = max(4, size // 4)
                spacing = effect_size + 2
                start_x = position[0] - (len(self.status_effects) * spacing) // 2
                
                for i, effect in enumerate(self.status_effects):
                    effect_x = start_x + i * spacing
                    effect_y = position[1] - size // 2 - effect_size - 2
                    
                    # Draw effect indicator
                    pygame.draw.circle(
                        surface,
                        self._get_effect_color(effect),
                        (effect_x, effect_y),
                        effect_size // 2
                    )
                    
            # Draw thought bubble if entity is thinking
            if hasattr(self, 'current_thought') and self.current_thought:
                self._draw_thought_bubble(surface, position, size)
                
        except Exception as e:
            print(f"Error drawing entity: {e}")
            traceback.print_exc()
            
    def _draw_thought_bubble(self, surface, position, size):
        """Draw a thought bubble with the current thought"""
        try:
            # Only draw if we have a thought
            if not self.current_thought:
                return
                
            # Set up font
            font_size = max(10, size // 3)
            font = pygame.font.Font(None, font_size)
            
            # Render thought text
            text = font.render(self.current_thought[:20] + "..." if len(self.current_thought) > 20 else self.current_thought,
                             True, (0, 0, 0))
            
            # Calculate bubble dimensions
            padding = 5
            bubble_width = text.get_width() + padding * 2
            bubble_height = text.get_height() + padding * 2
            
            # Calculate bubble position
            bubble_x = position[0] - bubble_width // 2
            bubble_y = position[1] - size - bubble_height - 10
            
            # Draw bubble background
            pygame.draw.ellipse(surface, (255, 255, 255),
                              (bubble_x, bubble_y, bubble_width, bubble_height))
            pygame.draw.ellipse(surface, (100, 100, 100),
                              (bubble_x, bubble_y, bubble_width, bubble_height), 1)
            
            # Draw connecting circles
            circle_spacing = 3
            circle_sizes = [6, 4, 2]
            for i, circle_size in enumerate(circle_sizes):
                circle_y = bubble_y + bubble_height + i * circle_spacing
                pygame.draw.circle(surface, (255, 255, 255),
                                (position[0], circle_y), circle_size)
                pygame.draw.circle(surface, (100, 100, 100),
                                (position[0], circle_y), circle_size, 1)
            
            # Draw text
            text_x = bubble_x + padding
            text_y = bubble_y + padding
            surface.blit(text, (text_x, text_y))
            
        except Exception as e:
            print(f"Error drawing thought bubble: {e}")
            traceback.print_exc()

    def is_visible(self, camera) -> bool:
        """Check if entity is visible in camera view"""
        screen_x = int(camera['width']/2 + (self.x - camera['x']) * camera['zoom'])
        screen_y = int(camera['height']/2 + (self.y - camera['y']) * camera['zoom'])
        
        # Add padding to account for entity size
        padding = int(self.size * camera['zoom'])
        
        return (-padding <= screen_x <= camera['width'] + padding and 
                -padding <= screen_y <= camera['height'] + padding)
                
    def distance_to(self, other) -> float:
        """Calculate distance to another entity"""
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx*dx + dy*dy)
        
    def get_state(self) -> Dict:
        """Get current state for saving"""
        return {
            'type': self.type,
            'subtype': self.subtype,
            'x': self.x,
            'y': self.y,
            'health': self.health,
            'energy': self.energy,
            'state': self.state
        }
        
    def load_state(self, state: Dict) -> None:
        """Load state from saved data"""
        self.type = state.get('type', self.type)
        self.subtype = state.get('subtype', self.subtype)
        self.x = state.get('x', self.x)
        self.y = state.get('y', self.y)
        self.health = state.get('health', self.health)
        self.energy = state.get('energy', self.energy)
        self.state = state.get('state', self.state)
        
    def get_position(self):
        """Get entity position as tuple"""
        return (self.x, self.y)
        
    def set_position(self, x, y):
        """Set entity position"""
        try:
            self.x = float(x)
            self.y = float(y)
        except (TypeError, ValueError) as e:
            print(f"Error setting position: {e}")
            
    def get_bounds(self):
        """Get entity bounds as rect"""
        return (self.x, self.y, self.size, self.size)
        
    def intersects(self, other):
        """Check if this entity intersects with another"""
        if not other:
            return False
            
        # Get bounds
        r1 = self.get_bounds()
        r2 = other.get_bounds()
        
        # Check intersection
        return (r1[0] < r2[0] + r2[2] and
                r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and
                r1[1] + r1[3] > r2[1])

    def _draw_visual_effect(self, surface, effect, x, y, zoom):
        """Draw a visual effect"""
        if effect['type'] == 'particle':
            color = effect['color']
            size = max(1, int(effect['size'] * zoom))  # Ensure minimum size of 1
            pos_x = int(x + effect['offset_x'] * zoom)
            pos_y = int(y + effect['offset_y'] * zoom)
            pygame.draw.circle(surface, color, (pos_x, pos_y), size)
            
        elif effect['type'] == 'text':
            font = pygame.font.Font(None, max(1, int(effect['font_size'] * zoom)))  # Ensure minimum size of 1
            text_surface = font.render(effect['text'], True, effect['color'])
            pos_x = int(x + effect['offset_x'] * zoom)
            pos_y = int(y + effect['offset_y'] * zoom)
            surface.blit(text_surface, (pos_x, pos_y))
            
    def _update_visual_effects(self, dt):
        """Update visual effects"""
        # Update existing effects
        for effect in self.visual_effects[:]:
            effect['lifetime'] -= dt
            if effect['lifetime'] <= 0:
                self.visual_effects.remove(effect)
            else:
                # Update effect properties
                effect['offset_y'] -= effect.get('rise_speed', 0) * dt
                effect['size'] *= effect.get('size_fade', 1.0)
                
    def add_visual_effect(self, effect_type, **kwargs):
        """Add a new visual effect"""
        effect = {
            'type': effect_type,
            'lifetime': kwargs.get('lifetime', 1.0),
            'offset_x': kwargs.get('offset_x', random.uniform(-10, 10)),
            'offset_y': kwargs.get('offset_y', -20),
            'size': kwargs.get('size', 5),
            'color': kwargs.get('color', (255, 255, 255)),
            'rise_speed': kwargs.get('rise_speed', 10),
            'size_fade': kwargs.get('size_fade', 0.95)
        }
        
        if effect_type == 'text':
            effect.update({
                'text': kwargs['text'],
                'font_size': kwargs.get('font_size', 20)
            })
            
        self.visual_effects.append(effect)
        
    def set_glow(self, color=None):
        """Set entity glow effect"""
        self.glow_color = color
        
    def set_outline(self, color=None):
        """Set entity outline effect"""
        self.outline_color = color

    def update_visual_effects(self):
        """Update and clean up visual effects"""
        current_time = pygame.time.get_ticks() / 1000
        
        # Remove expired effects
        self.visual_effects = [
            effect for effect in self.visual_effects
            if current_time - effect['creation_time'] < effect['lifetime']
        ]
        
    def draw_visual_effects(self, surface, camera_x=0, camera_y=0, zoom=1):
        """Draw all visual effects"""
        current_time = pygame.time.get_ticks() / 1000
        
        for effect in self.visual_effects:
            # Calculate screen position
            screen_x = surface.get_width()/2 + (self.x - camera_x) * zoom
            screen_y = surface.get_height()/2 + (self.y - camera_y) * zoom
            
            # Calculate alpha based on lifetime
            time_alive = current_time - effect['creation_time']
            alpha = 255
            if time_alive > effect['lifetime'] - 0.5:  # Fade out in last 0.5 seconds
                alpha = max(0, int(255 * (effect['lifetime'] - time_alive) * 2))
                
            # Create font
            font = pygame.font.Font(None, int(effect['font_size'] * max(1, zoom)))
            
            # Split text into lines
            lines = effect['text'].split('\n')
            
            # Calculate total height
            line_height = font.get_height()
            total_height = line_height * len(lines)
            
            # Calculate positions - adjust for zoom
            offset_x = effect['offset_x'] * zoom
            offset_y = effect['offset_y'] * zoom
            x = screen_x + offset_x
            y = screen_y + offset_y - total_height * zoom
            
            for line in lines:
                # Render text
                text_surface = font.render(line, True, effect['text_color'])
                text_rect = text_surface.get_rect()
                text_rect.centerx = int(x)
                text_rect.y = int(y)
                
                # Draw background if specified
                if effect['background_color']:
                    padding = effect['padding'] * zoom
                    bg_rect = text_rect.inflate(padding * 2, padding * 2)
                    bg_color = list(effect['background_color'])
                    if len(bg_color) == 3:
                        bg_color.append(alpha)
                    else:
                        bg_color[3] = min(bg_color[3], alpha)
                    
                    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=int(5 * zoom))
                
                # Apply alpha to text
                text_surface.set_alpha(alpha)
                
                # Draw text
                surface.blit(text_surface, text_rect)
                
                # Move to next line
                y += line_height

    def get_tooltip_text(self):
        """Default tooltip text"""
        return f"Entity at ({int(self.x)}, {int(self.y)})"

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

    def _draw_health_bar(self, screen, screen_x, screen_y, scaled_size):
        """Draw health bar above entity"""
        try:
            # Calculate bar dimensions
            bar_width = scaled_size
            bar_height = max(2, int(scaled_size * 0.1))
            bar_y_offset = -scaled_size//2 - bar_height - 2
            
            # Draw background
            pygame.draw.rect(
                screen,
                (100, 0, 0),  # Dark red
                (screen_x - bar_width//2,
                 screen_y + bar_y_offset,
                 bar_width,
                 bar_height)
            )
            
            # Draw health
            health_width = int(bar_width * (self.health / self.max_health))
            if health_width > 0:
                pygame.draw.rect(
                    screen,
                    (0, 200, 0),  # Green
                    (screen_x - bar_width//2,
                     screen_y + bar_y_offset,
                     health_width,
                     bar_height)
                )
                
        except Exception as e:
            print(f"Error drawing health bar: {e}")
            traceback.print_exc()
            
    def _draw_status_effects(self, screen, screen_x, screen_y, scaled_size):
        """Draw status effects above entity"""
        try:
            if not hasattr(self, 'status_effects') or not self.status_effects:
                return
                
            # Calculate dimensions
            effect_size = max(4, int(scaled_size * 0.2))
            spacing = effect_size + 2
            start_x = screen_x - (len(self.status_effects) * spacing) // 2
            effect_y = screen_y - scaled_size//2 - effect_size - 2
            
            # Draw each effect
            for i, effect in enumerate(self.status_effects):
                effect_x = start_x + i * spacing
                
                # Draw effect indicator
                pygame.draw.circle(
                    screen,
                    self._get_effect_color(effect),
                    (int(effect_x), int(effect_y)),
                    effect_size // 2
                )
                
        except Exception as e:
            print(f"Error drawing status effects: {e}")
            traceback.print_exc()
            
    def _get_effect_color(self, effect):
        """Get color for status effect"""
        effect_colors = {
            'poisoned': (0, 255, 0),
            'burning': (255, 100, 0),
            'frozen': (0, 200, 255),
            'stunned': (255, 255, 0),
            'healing': (0, 255, 100),
            'buffed': (200, 100, 255),
            'debuffed': (100, 0, 0)
        }
        return effect_colors.get(effect['type'], (200, 200, 200)) 