import pygame
from .panels import InfoPanel, TimePanel, StatsPanel, MinimapPanel, EntityListPanel
from .panels.selection_panel import SelectionPanel
from .notifications import NotificationSystem
from .particles import ParticleSystem
from ..world.entities.human import Human
from ..constants import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS, TILE_SIZE, FONTS

class UISystem:
    def __init__(self):
        try:
            # Core UI components
            self.panels = {}
            self.active_panel = None
            self.needs_update = True
            self.last_mouse_pos = (0, 0)
            
            # Additional systems
            self.notifications = NotificationSystem()
            self.particles = ParticleSystem()
            
            # Selection system
            self.selection = SelectionPanel()
            
            # Font settings - use FONTS from constants
            self.font = FONTS['normal']
            self.tooltip_font = FONTS['small']
            if not self.font or not self.tooltip_font:
                print("Warning: Could not load fonts, using system default")
                self.font = pygame.font.Font(None, 24)
                self.tooltip_font = pygame.font.Font(None, 20)
            
            # Display settings
            self.fullscreen = False
            self.screen_width = WINDOW_WIDTH
            self.screen_height = WINDOW_HEIGHT
            
            # Tooltip system
            self.current_tooltip = None
            self.tooltip_delay = 0.5
            self.tooltip_timer = 0
            
            # Initialize panels
            self._init_panels()
            
        except Exception as e:
            print(f"Error initializing UI system: {e}")
            import traceback
            traceback.print_exc()
            # Set fallback values
            self.font = pygame.font.Font(None, 24)
            self.tooltip_font = pygame.font.Font(None, 20)
    
    def initialize(self, world):
        """Initialize UI with world reference"""
        try:
            # Initialize each panel with world reference
            for panel in self.panels.values():
                if hasattr(panel, 'initialize'):
                    panel.initialize(world)
                    
            # Initialize notification system
            self.notifications.initialize()
            
            # Initialize particle system
            self.particles.initialize()
            
            # Initialize selection panel
            if hasattr(self.selection, 'initialize'):
                self.selection.initialize(world)
                
            print("UI system initialized successfully")
            
        except Exception as e:
            print(f"Error initializing UI components: {e}")
            traceback.print_exc()
    
    def handle_event(self, event, world):
        """Handle UI events"""
        try:
            # Get mouse position safely
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle fullscreen toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    return True
            
            # Handle panel events
            for panel in self.panels.values():
                if panel.visible:
                    # Handle panel events
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if panel.rect.collidepoint(mouse_pos):
                            panel.handle_event(event, world)
                            return True
            
            # Handle selection events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.selection, 'handle_click'):
                    if self.selection.handle_click(mouse_pos):
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error in UI event handling: {e}")
            return False
    
    def update(self, world, dt):
        """Update UI elements"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update panels
            for panel in self.panels.values():
                if panel.visible:
                    panel.update(world, mouse_pos)
                    
                    # Update hover state
                    panel.hover = panel.rect.collidepoint(mouse_pos)
                    
                    # Update panel if needed
                    if panel.needs_update:
                        panel._create_surfaces()
                        panel.needs_update = False
            
            # Update tooltip system
            self._update_tooltips(mouse_pos, dt)
            
            # Update other systems
            if world:  # Only update if world exists
                self.selection.update(world, mouse_pos)
                self.notifications.update(dt)
                self.particles.update(dt)
                
        except Exception as e:
            print(f"Error in UI update: {e}")
            traceback.print_exc()
    
    def draw(self, screen, world=None):
        """Draw UI elements"""
        try:
            # Draw all panels
            for panel in self.panels.values():
                if panel.visible:
                    # Draw panel background with glow if hovered
                    if panel.hover:
                        screen.blit(panel.background, 
                                  (panel.x - panel.glow_size, 
                                   panel.y - panel.glow_size))
                    
                    # Draw main panel surface
                    screen.blit(panel.surface, panel.rect)
                    
                    # Draw panel content
                    if hasattr(panel, 'draw_content'):
                        panel.draw_content(screen, world)
            
            # Draw additional UI elements
            if world:  # Only draw if world exists
                self.particles.draw(screen, world.camera['x'], world.camera['y'])
                self.selection.draw(screen, world)
            
            # Draw tooltips
            if self.current_tooltip:
                self._draw_tooltip(screen, self.current_tooltip)
            
            # Draw notifications last (on top)
            self.notifications.draw(screen)
            
        except Exception as e:
            print(f"Error in UI draw: {e}")
            traceback.print_exc()
    
    def _update_tooltips(self, mouse_pos, dt):
        """Update tooltip system"""
        try:
            # Check for hoverable elements
            hovering = False
            for panel in self.panels.values():
                if panel.visible and panel.rect.collidepoint(mouse_pos):
                    if hasattr(panel, 'get_tooltip'):
                        tooltip_text = panel.get_tooltip()
                        if tooltip_text:
                            hovering = True
                            if self.tooltip_timer >= self.tooltip_delay:
                                self.current_tooltip = {
                                    'text': tooltip_text,
                                    'pos': mouse_pos
                                }
                            break
            
            if hovering:
                self.tooltip_timer += dt
            else:
                self.tooltip_timer = 0
                self.current_tooltip = None
                
        except Exception as e:
            print(f"Error updating tooltips: {e}")
            
    def _draw_tooltip(self, screen, tooltip):
        """Draw tooltip at mouse position"""
        try:
            if not tooltip or not tooltip['text']:
                return
                
            padding = 5
            max_width = 200
            
            # Render text with wrapping
            words = tooltip['text'].split()
            lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                word_surface = self.tooltip_font.render(word + ' ', True, UI_COLORS['text_normal'])
                word_width = word_surface.get_width()
                
                if current_width + word_width > max_width:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width
                    
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate tooltip dimensions
            line_height = self.tooltip_font.get_height()
            tooltip_height = len(lines) * line_height + padding * 2
            tooltip_width = max(self.tooltip_font.render(line, True, UI_COLORS['text_normal']).get_width() 
                              for line in lines) + padding * 2
            
            # Create tooltip surface
            tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
            pygame.draw.rect(tooltip_surface, (*UI_COLORS['tooltip_bg'][:3], 220),
                           tooltip_surface.get_rect(), border_radius=3)
            
            # Draw text
            for i, line in enumerate(lines):
                text_surface = self.tooltip_font.render(line, True, UI_COLORS['text_normal'])
                tooltip_surface.blit(text_surface, (padding, padding + i * line_height))
            
            # Position tooltip near mouse
            x = tooltip['pos'][0] + 15
            y = tooltip['pos'][1] + 15
            
            # Keep tooltip on screen
            if x + tooltip_width > self.screen_width:
                x = self.screen_width - tooltip_width
            if y + tooltip_height > self.screen_height:
                y = self.screen_height - tooltip_height
            
            screen.blit(tooltip_surface, (x, y))
            
        except Exception as e:
            print(f"Error drawing tooltip: {e}")
            
    def add_element(self, element):
        """Add UI element"""
        self.panels[element.name] = element
        element.visible = True
        
    def remove_element(self, element):
        """Remove UI element"""
        if element.name in self.panels:
            del self.panels[element.name]
            
    def clear_elements(self):
        """Remove all UI elements"""
        self.panels.clear()
        
    def draw_text(self, screen, text, pos, color=None, centered=False):
        """Draw text on screen"""
        try:
            if color is None:
                color = UI_COLORS['text_normal']
            
            text_surface = self.font.render(str(text), True, color)
            if centered:
                text_rect = text_surface.get_rect(center=pos)
            else:
                text_rect = text_surface.get_rect(topleft=pos)
            screen.blit(text_surface, text_rect)
            
        except Exception as e:
            print(f"Error drawing text: {e}")
        
    def draw_progress_bar(self, screen, rect, progress, text=None):
        """Draw a progress bar"""
        # Draw background
        pygame.draw.rect(screen, self.colors['progress_bar_bg'], rect)
        
        # Draw progress
        progress_width = int(rect.width * max(0, min(1, progress)))
        if progress_width > 0:
            progress_rect = pygame.Rect(rect.x, rect.y, progress_width, rect.height)
            pygame.draw.rect(screen, self.colors['progress_bar'], progress_rect)
            
        # Draw text
        if text:
            self.draw_text(screen, text, rect.center, centered=True)
            
    def draw_button(self, screen, rect, text, color=None, hover=False, disabled=False):
        """Draw a button"""
        if disabled:
            button_color = self.colors['button_disabled']
        elif hover:
            button_color = self.colors['button_hover']
        else:
            button_color = color or self.colors['button']
            
        pygame.draw.rect(screen, button_color, rect)
        self.draw_text(screen, text, rect.center, centered=True)

    def _init_panels(self):
        """Initialize UI panels with proper layout"""
        try:
            # Calculate screen dimensions and margins
            margin = 20
            panel_spacing = 20
            
            # Left column width (20% of screen width)
            left_width = int(WINDOW_WIDTH * 0.2)
            
            # Right column width (20% of screen width)
            right_width = int(WINDOW_WIDTH * 0.2)
            
            # Center panel width (50% of screen width)
            center_width = int(WINDOW_WIDTH * 0.5)
            
            # Calculate heights
            top_height = int(WINDOW_HEIGHT * 0.2)  # 20% of screen height
            middle_height = int(WINDOW_HEIGHT * 0.3)  # 30% of screen height
            
            # Calculate positions
            left_x = margin
            center_x = left_x + left_width + panel_spacing
            right_x = center_x + center_width + panel_spacing
            
            # Main panels layout
            self.panels = {
                # Left column
                'time': TimePanel(
                    left_x, 
                    margin, 
                    left_width, 
                    top_height,
                    title="Time & Weather",
                    icon="⏰"
                ),
                'stats': StatsPanel(
                    left_x, 
                    margin + top_height + panel_spacing, 
                    left_width, 
                    middle_height,
                    title="World Stats",
                    icon="📊"
                ),
                
                # Center panel (entity list)
                'entities': EntityListPanel(
                    center_x,
                    margin,
                    center_width,
                    WINDOW_HEIGHT - (margin * 2),
                    title="Entities",
                    icon="👥"
                ),
                
                # Right column
                'minimap': MinimapPanel(
                    right_x,
                    margin,
                    right_width,
                    top_height,
                    title="World Map",
                    icon="🗺️"
                ),
                'info': InfoPanel(
                    right_x,
                    margin + top_height + panel_spacing,
                    right_width,
                    middle_height,
                    title="Entity Info",
                    icon="ℹ️"
                )
            }
            
            # Initialize each panel
            for panel_id, panel in self.panels.items():
                panel.visible = True
                panel.needs_update = True
                # Initialize world reference if panel has initialize method
                if hasattr(panel, 'initialize') and hasattr(self, 'world'):
                    panel.initialize(self.world)
                print(f"Initialized panel: {panel_id} at position ({panel.x}, {panel.y}) with size ({panel.width}, {panel.height})")
                
        except Exception as e:
            print(f"Error initializing panels: {e}")
            import traceback
            traceback.print_exc()
            self.panels = {}

    def add_panel(self, panel_id: str, panel):
        """Add a panel to the UI system"""
        self.panels[panel_id] = panel
        
    def cleanup(self):
        """Clean up UI system resources"""
        try:
            for panel in self.panels.values():
                if hasattr(panel, 'cleanup'):
                    panel.cleanup()
            self.panels.clear()
            self.notifications.cleanup()
            self.particles.cleanup()
            self.selection.cleanup()
            
        except Exception as e:
            print(f"Error cleaning up UI system: {e}")
            traceback.print_exc()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        try:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.screen_width = screen.get_width()
                self.screen_height = screen.get_height()
            else:
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                self.screen_width = WINDOW_WIDTH
                self.screen_height = WINDOW_HEIGHT
            
            # Update panel positions based on new screen size
            self._update_panel_positions()
            
            # Add notification
            self.add_notification(f"Fullscreen mode: {'On' if self.fullscreen else 'Off'}", duration=2.0, type='info')
            
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
            self.add_notification("Failed to toggle fullscreen mode", duration=2.0, type='error')
    
    def _update_panel_positions(self):
        """Update panel positions based on current screen size"""
        try:
            # Calculate screen dimensions and margins
            margin = 5
            panel_spacing = 5
            
            # Calculate panel sizes
            left_width = min(220, self.screen_width * 0.15)
            right_width = min(220, self.screen_width * 0.15)
            
            # Calculate heights
            top_height = min(120, self.screen_height * 0.15)
            middle_height = min(250, self.screen_height * 0.3)
            
            # Calculate positions
            left_x = margin
            right_x = self.screen_width - right_width - margin
            
            # Update panel positions and sizes
            if 'time' in self.panels:
                self.panels['time'].update_position(left_x, margin, left_width, top_height)
            
            if 'stats' in self.panels:
                self.panels['stats'].update_position(left_x, margin + top_height + panel_spacing, 
                                                   left_width, middle_height)
            
            if 'minimap' in self.panels:
                self.panels['minimap'].update_position(right_x, margin, right_width, top_height)
            
            if 'info' in self.panels:
                self.panels['info'].update_position(right_x, margin + top_height + panel_spacing,
                                                  right_width, middle_height)
            
            if 'entities' in self.panels:
                entities_width = self.screen_width - left_width - right_width - (margin * 3) - (panel_spacing * 2)
                self.panels['entities'].update_position(left_x + left_width + panel_spacing,
                                                      margin,
                                                      entities_width,
                                                      self.screen_height - (margin * 2))
            
            # Mark UI for update
            self.needs_update = True
            
        except Exception as e:
            print(f"Error updating panel positions: {e}")
            
    def add_notification(self, message, duration=2.0, type='info'):
        """Add a notification message"""
        try:
            if hasattr(self.notifications, 'add_notification'):
                self.notifications.add_notification(message, duration, type)
        except Exception as e:
            print(f"Error adding notification: {e}")