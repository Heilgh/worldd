import pygame
from ..panel import UIPanel
from ...constants import UI_COLORS
from ...world.entities.human import Human
from ...world.entities.animal import Animal
from ...world.entities.plant import Plant

class InfoPanel(UIPanel):
    def __init__(self, x, y, width, height, title="Entity Info", icon="ℹ️"):
        super().__init__(x, y, width, height, title, icon)
        self.selected_entity = None
        self.background_alpha = 200
        self.line_height = 25
        
    def initialize(self, world):
        """Initialize panel with world reference"""
        self.world = world
        
    def set_selected_entity(self, entity):
        """Set the currently selected entity"""
        self.selected_entity = entity
        
    def draw(self, screen, world=None):
        try:
            if not self.visible:
                return
                
            # Draw panel background
            pygame.draw.rect(screen, (*UI_COLORS['panel_bg'][:3], self.background_alpha), self.rect)
            pygame.draw.rect(screen, UI_COLORS['panel_border'], self.rect, 1)
            
            # Draw title
            title_text = self.font.render(f"{self.icon} {self.title}", True, UI_COLORS['text_highlight'])
            screen.blit(title_text, (self.x + 10, self.y + 5))
            
            # Draw content
            if self.selected_entity:
                y = self.y + 40
                
                # Draw entity type icon and name
                if isinstance(self.selected_entity, Human):
                    icon = "👤"
                    type_name = "Human"
                elif isinstance(self.selected_entity, Animal):
                    icon = "🐾"
                    type_name = f"Animal ({self.selected_entity.subtype})"
                elif isinstance(self.selected_entity, Plant):
                    icon = "🌱"
                    type_name = f"Plant ({self.selected_entity.subtype})"
                else:
                    icon = "❓"
                    type_name = "Unknown"
                
                # Draw type header
                header = self.emoji_font.render(f"{icon} {type_name}", True, UI_COLORS['text_highlight'])
                screen.blit(header, (self.x + 10, y))
                y += self.line_height + 5
                
                # Draw basic info
                info_lines = [
                    f"Position: ({int(self.selected_entity.x)}, {int(self.selected_entity.y)})",
                    f"Health: {int(self.selected_entity.health)}%"
                ]
                
                # Add entity-specific info
                if isinstance(self.selected_entity, Human):
                    info_lines.extend([
                        f"Energy: {int(self.selected_entity.needs['energy'])}%",
                        f"Hunger: {int(self.selected_entity.needs['hunger'])}%",
                        f"Social: {int(self.selected_entity.needs['social'])}%",
                        f"Mood: {self.selected_entity.state['mood'].capitalize()}",
                        f"Action: {self.selected_entity.state['action'].capitalize()}"
                    ])
                elif isinstance(self.selected_entity, Animal):
                    info_lines.extend([
                        f"Energy: {int(self.selected_entity.energy)}%",
                        f"State: {self.selected_entity.state['action'].capitalize()}"
                    ])
                elif isinstance(self.selected_entity, Plant):
                    info_lines.extend([
                        f"Growth: {int(self.selected_entity.growth * 100)}%",
                        f"State: {self.selected_entity.state.capitalize()}"
                    ])
                
                # Draw all info lines
                for line in info_lines:
                    text = self.font.render(line, True, UI_COLORS['text_normal'])
                    screen.blit(text, (self.x + 10, y))
                    y += self.line_height
                    
                # Draw status effects if any
                if hasattr(self.selected_entity, 'status_effects') and self.selected_entity.status_effects:
                    y += 10
                    status_title = self.font.render("Status Effects:", True, UI_COLORS['text_highlight'])
                    screen.blit(status_title, (self.x + 10, y))
                    y += self.line_height
                    
                    for effect in self.selected_entity.status_effects:
                        effect_text = self.font.render(f"• {effect['name'].capitalize()}", True, UI_COLORS['text_normal'])
                        screen.blit(effect_text, (self.x + 20, y))
                        y += self.line_height
                        
            else:
                # Draw "No selection" message
                text = self.font.render("No entity selected", True, UI_COLORS['text_dark'])
                text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
                screen.blit(text, text_rect)
                
        except Exception as e:
            print(f"Error drawing info panel: {e}") 