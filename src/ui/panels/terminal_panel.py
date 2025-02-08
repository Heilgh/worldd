import pygame
from ...constants import UI_COLORS, WINDOW_HEIGHT

class TerminalPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.minimap_rect = pygame.Rect(
            x + 10,  # Add padding
            y + 30,  # Space for title
            width - 20,  # Account for padding
            height - 40  # Account for title and padding
        )
        self.title_font = pygame.font.Font(None, 24)
        self.font = pygame.font.Font(None, 16)
        self.messages = []
        self.max_messages = 100
        self.scroll_position = 0
        self.active = True
        
        # Message tracking
        self.last_message = None
        self.last_message_time = 0
        self.generation_complete_shown = False
        
        # Message categories and colors
        self.categories = {
            'system': UI_COLORS['text_highlight'],
            'event': UI_COLORS['text_normal'],
            'interaction': (100, 200, 100),
            'warning': (200, 150, 50),
            'error': (200, 50, 50)
        }
        
        # Add welcome message
        self.add_message("Terminal initialized", 'system')
        
    def add_message(self, text, category='event'):
        """Add a new message to the terminal"""
        current_time = pygame.time.get_ticks() / 1000
        
        # Prevent duplicate messages
        if text == self.last_message and current_time - self.last_message_time < 2.0:
            return
            
        # Special handling for completion message
        if text == "World generation complete!" and self.generation_complete_shown:
            return
            
        self.messages.append({
            'text': text,
            'category': category,
            'timestamp': current_time,
            'color': self.categories.get(category, UI_COLORS['text_normal'])
        })
        
        # Update message tracking
        self.last_message = text
        self.last_message_time = current_time
        
        # Limit number of messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            
        # Auto-scroll to bottom
        self.scroll_to_bottom()
        
    def add_event(self, event_type, details):
        """Add a formatted event message"""
        if event_type == 'world_gen':
            # Special handling for world generation events
            if details.get('status') == 'complete':
                if not self.generation_complete_shown:
                    self.add_message('World generation complete!', 'system')
                    self.generation_complete_shown = True
                return  # Skip any other processing for completion messages
            
            phase = details.get('step', details.get('phase', 'world'))
            substep = details.get('substep', '')
            progress = details.get('progress', 0)
            
            # Format progress message
            if progress > 0:
                msg = f"Generating {phase}"
                if substep:
                    msg += f" - {substep}"
                msg += f" ({int(progress)}%)"
                
                # Show messages at significant progress points
                show_message = (
                    progress % 20 == 0 or  # Show every 20%
                    self.last_message is None or  # First message
                    not self.last_message.startswith(f"Generating {phase}") or  # New phase
                    (substep and not self.last_message.startswith(f"Generating {phase} - {substep}"))  # New substep
                )
                
                if show_message and msg != self.last_message:
                    self.add_message(msg, 'system')
                    self.last_message = msg
            else:
                msg = f"Starting {phase} generation"
                if substep:
                    msg += f" - {substep}"
                msg += "..."
                if msg != self.last_message:
                    self.add_message(msg, 'system')
                    self.last_message = msg
        elif event_type == 'interaction':
            msg = f"{details['actor']} interacts with {details['target']}"
            self.add_message(msg, 'interaction')
        elif event_type == 'birth':
            msg = f"New human born: {details['name']}"
            self.add_message(msg, 'system')
        elif event_type == 'death':
            msg = f"{details['name']} has died"
            self.add_message(msg, 'warning')
        elif event_type == 'discovery':
            msg = f"{details['actor']} discovered {details['what']}"
            self.add_message(msg, 'event')
        elif event_type == 'weather':
            msg = f"Weather changed to {details['condition']}"
            self.add_message(msg, 'system')
        
    def draw(self, screen):
        """Draw the terminal panel"""
        # Draw background
        pygame.draw.rect(screen, UI_COLORS['panel_bg'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['panel_border'], self.rect, 2)
        
        # Draw title
        title = self.font.render("Terminal", True, UI_COLORS['text_highlight'])
        screen.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Calculate visible area
        visible_height = self.rect.height - 40  # Account for padding and title
        line_height = self.font.get_height() + 2
        visible_lines = visible_height // line_height
        
        # Draw messages
        y = self.rect.y + 30  # Start below title
        start_idx = max(0, len(self.messages) - visible_lines - self.scroll_position)
        end_idx = min(len(self.messages), start_idx + visible_lines)
        
        for i in range(start_idx, end_idx):
            msg = self.messages[i]
            time_text = f"[{msg['timestamp']:.1f}] "
            text = time_text + msg['text']
            
            # Render timestamp in gray
            time_surface = self.font.render(time_text, True, (150, 150, 150))
            screen.blit(time_surface, (self.rect.x + 5, y))
            
            # Render message in its category color
            msg_surface = self.font.render(msg['text'], True, msg['color'])
            screen.blit(msg_surface, (self.rect.x + 5 + time_surface.get_width(), y))
            
            y += line_height
            
        # Draw scroll indicators if needed
        if len(self.messages) > visible_lines:
            if self.scroll_position > 0:
                pygame.draw.polygon(screen, UI_COLORS['text_normal'],
                    [(self.rect.right - 15, self.rect.y + 10),
                     (self.rect.right - 10, self.rect.y + 5),
                     (self.rect.right - 5, self.rect.y + 10)])
            
            if self.scroll_position < len(self.messages) - visible_lines:
                pygame.draw.polygon(screen, UI_COLORS['text_normal'],
                    [(self.rect.right - 15, self.rect.bottom - 10),
                     (self.rect.right - 10, self.rect.bottom - 5),
                     (self.rect.right - 5, self.rect.bottom - 10)])
    
    def handle_event(self, event):
        """Handle mouse and keyboard events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.scroll_up()
            elif event.button == 5:  # Mouse wheel down
                self.scroll_down()
                
    def scroll_up(self):
        """Scroll messages up"""
        self.scroll_position = min(
            len(self.messages) - 1,
            self.scroll_position + 1
        )
        
    def scroll_down(self):
        """Scroll messages down"""
        self.scroll_position = max(0, self.scroll_position - 1)
        
    def scroll_to_bottom(self):
        """Scroll to the most recent messages"""
        self.scroll_position = 0 

    def reset(self):
        """Reset terminal state"""
        self.messages.clear()
        self.scroll_position = 0
        self.last_message = None
        self.last_message_time = 0
        self.generation_complete_shown = False
        self.add_message("Terminal initialized", 'system') 