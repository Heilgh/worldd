class Entity:
    """Base class for all entities in the game world"""
    
    def __init__(self, x: float, y: float, width: int = 32, height: int = 32):
        # Position and dimensions
        self.x = x
        self.y = y
        self.last_x = x  # Track last position for chunk updates
        self.last_y = y
        self.width = width
        self.height = height
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 2.0
        
        # State
        self.active = True
        self.selected = False
        self.visible = True
        self.health = 100
        self.max_health = 100
        
        # Visual properties
        self.color = (255, 255, 255)  # Default white
        self.surface = None
        self.scale = 1.0
        self.alpha = 255
        self.effects = []  # Visual effects
        self.status_effects = []  # Status effects (buffs/debuffs)
        
        # Systems
        self.systems = {}
        self.thought_system = None
        self.current_thought = None
        self.thought_timer = 0
        self.thought_duration = 3.0  # How long thoughts are displayed
        
        # Debug
        self.debug_info = {}
        
    def update(self, world, dt: float):
        """Update entity state"""
        try:
            # Update position based on velocity
            self.x += self.velocity_x * self.speed * dt
            self.y += self.velocity_y * self.speed * dt
            
            # Update systems
            for system in self.systems.values():
                if hasattr(system, 'update'):
                    system.update(world, dt)
                    
            # Update thought system
            if self.thought_system:
                context = world._generate_entity_context(self)
                thought = self.thought_system.process(context)
                if thought:
                    self.current_thought = thought
                    self.thought_timer = self.thought_duration
                    world._process_entity_action(self, thought)
                    
            # Update thought timer
            if self.thought_timer > 0:
                self.thought_timer -= dt
                if self.thought_timer <= 0:
                    self.current_thought = None
                    
            # Update effects
            self.effects = [effect for effect in self.effects if effect.update(dt)]
            self.status_effects = [effect for effect in self.status_effects if effect.update(dt)]
            
        except Exception as e:
            print(f"Error updating entity {self}: {e}")
            traceback.print_exc()
            
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float, zoom: float = 1.0):
        """Draw entity on screen"""
        try:
            if not self.visible:
                return
                
            # Calculate screen position
            screen_x = int((self.x - camera_x) * zoom + WINDOW_WIDTH / 2)
            screen_y = int((self.y - camera_y) * zoom + WINDOW_HEIGHT / 2)
            
            # Skip if off screen (with padding)
            padding = 100
            if (screen_x + self.width * zoom < -padding or 
                screen_x > WINDOW_WIDTH + padding or
                screen_y + self.height * zoom < -padding or
                screen_y > WINDOW_HEIGHT + padding):
                return
                
            # Draw entity surface or rectangle
            if self.surface:
                # Scale surface
                scaled_width = int(self.width * zoom * self.scale)
                scaled_height = int(self.height * zoom * self.scale)
                if scaled_width > 0 and scaled_height > 0:
                    scaled_surface = pygame.transform.scale(self.surface, (scaled_width, scaled_height))
                    
                    # Apply alpha
                    if self.alpha < 255:
                        scaled_surface.set_alpha(self.alpha)
                        
                    # Draw centered
                    screen.blit(scaled_surface, 
                              (screen_x - scaled_width // 2,
                               screen_y - scaled_height // 2))
            else:
                # Draw colored rectangle
                pygame.draw.rect(screen, self.color,
                               (screen_x - self.width * zoom * self.scale // 2,
                                screen_y - self.height * zoom * self.scale // 2,
                                self.width * zoom * self.scale,
                                self.height * zoom * self.scale))
                                
            # Draw health bar if damaged
            if self.health < self.max_health:
                bar_width = 40 * zoom
                bar_height = 5 * zoom
                bar_x = screen_x - bar_width / 2
                bar_y = screen_y - self.height * zoom * self.scale / 2 - bar_height - 5
                
                # Background
                pygame.draw.rect(screen, (255, 0, 0),
                               (bar_x, bar_y, bar_width, bar_height))
                               
                # Health
                health_width = (self.health / self.max_health) * bar_width
                if health_width > 0:
                    pygame.draw.rect(screen, (0, 255, 0),
                                   (bar_x, bar_y, health_width, bar_height))
                                   
            # Draw status effects
            effect_y = screen_y - self.height * zoom * self.scale / 2 - 25
            for effect in self.status_effects:
                effect.draw(screen, screen_x, effect_y, zoom)
                effect_y -= 20 * zoom
                
            # Draw thought bubble if thinking
            if self.current_thought:
                font = pygame.font.Font(None, int(24 * zoom))
                text = font.render(self.current_thought, True, (0, 0, 0))
                bubble_width = text.get_width() + 20
                bubble_height = text.get_height() + 10
                bubble_x = screen_x - bubble_width / 2
                bubble_y = screen_y - self.height * zoom * self.scale / 2 - bubble_height - 30
                
                # Draw bubble
                pygame.draw.ellipse(screen, (255, 255, 255),
                                  (bubble_x, bubble_y, bubble_width, bubble_height))
                pygame.draw.ellipse(screen, (0, 0, 0),
                                  (bubble_x, bubble_y, bubble_width, bubble_height), 2)
                                  
                # Draw text
                screen.blit(text, (bubble_x + 10, bubble_y + 5))
                
            # Draw selection highlight
            if self.selected:
                pygame.draw.circle(screen, (255, 255, 0),
                                 (screen_x, screen_y),
                                 self.width * zoom * self.scale / 2 + 5,
                                 3)
                                 
            # Draw effects
            for effect in self.effects:
                effect.draw(screen, screen_x, screen_y, zoom)
                
            # Draw debug info
            if DEBUG:
                debug_y = screen_y + self.height * zoom * self.scale / 2 + 5
                font = pygame.font.Font(None, int(20 * zoom))
                for key, value in self.debug_info.items():
                    text = font.render(f"{key}: {value}", True, (255, 255, 255))
                    screen.blit(text, (screen_x - text.get_width() / 2, debug_y))
                    debug_y += 20 * zoom
                    
        except Exception as e:
            print(f"Error drawing entity {self}: {e}")
            traceback.print_exc()
            
    def add_effect(self, effect):
        """Add a visual effect to the entity"""
        self.effects.append(effect)
        
    def add_status_effect(self, effect):
        """Add a status effect to the entity"""
        self.status_effects.append(effect)
        
    def set_thought(self, thought: str):
        """Set the current thought and reset timer"""
        self.current_thought = thought
        self.thought_timer = self.thought_duration 