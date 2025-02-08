import pygame
from ..panel import UIPanel
from ...constants import UI_COLORS
from ...world.entities.human import Human
from ...world.entities.animal import Animal
from ...world.entities.plant import Plant

class StatsPanel(UIPanel):
    def __init__(self, x, y, width, height, title="World Stats", icon="📊"):
        super().__init__(x, y, width, height, title, icon)
        self.font = pygame.font.Font(None, 24)
        self.line_height = 25
        
    def initialize(self, world):
        """Initialize panel with world reference"""
        self.world = world
        
    def draw(self, screen, world=None):
        try:
            if not world:
                return
                
            # Draw panel background
            super().draw(screen)
            
            # Calculate entity counts
            humans = [e for e in world.entities if isinstance(e, Human)]
            animals = [e for e in world.entities if isinstance(e, Animal)]
            plants = [e for e in world.entities if isinstance(e, Plant)]
            
            # Calculate statistics
            total_population = len(humans)
            avg_happiness = sum(h.needs['social'] for h in humans) / total_population if humans else 0
            avg_health = sum(h.health for h in humans) / total_population if humans else 0
            
            # Format stats with proper float handling
            stats = [
                f"Population: {total_population}",
                f"Animals: {len(animals)}",
                f"Plants: {len(plants)}",
                f"Total Entities: {len(world.entities)}",
                f"Avg Happiness: {int(avg_happiness)}%",
                f"Avg Health: {int(avg_health)}%",
                f"Temperature: {int(getattr(world, 'temperature', 20))}°C",
                f"Weather: {world.weather_system.current_weather.capitalize() if hasattr(world, 'weather_system') else 'Clear'}"
            ]
            
            # Draw stats
            y = self.y + 40  # Start below title
            for stat in stats:
                text = self.font.render(stat, True, UI_COLORS['text_normal'])
                screen.blit(text, (self.x + 10, y))
                y += self.line_height
                
            # Draw entity type distribution
            self._draw_distribution_bars(screen, {
                'Humans': len(humans),
                'Animals': len(animals),
                'Plants': len(plants)
            }, y)
                
        except Exception as e:
            print(f"Error drawing stats: {e}")
            import traceback
            traceback.print_exc()
            
    def _draw_distribution_bars(self, screen, data, start_y):
        """Draw distribution bars for entity types"""
        try:
            total = sum(data.values())
            if total == 0:
                return
                
            bar_height = 15
            bar_width = self.width - 40
            y = start_y + 10
            
            # Draw title
            title = self.font.render("Entity Distribution", True, UI_COLORS['text_highlight'])
            screen.blit(title, (self.x + 10, y))
            y += 25
            
            # Colors for different entity types
            colors = {
                'Humans': (255, 200, 150),
                'Animals': (150, 200, 150),
                'Plants': (100, 200, 100)
            }
            
            # Draw bars
            for label, count in data.items():
                # Draw label
                text = self.font.render(f"{label}: {count}", True, UI_COLORS['text_normal'])
                screen.blit(text, (self.x + 10, y))
                
                # Draw bar background
                bar_bg_rect = pygame.Rect(self.x + 10, y + 20, bar_width, bar_height)
                pygame.draw.rect(screen, UI_COLORS['panel_border'], bar_bg_rect)
                
                # Draw filled portion
                if total > 0:
                    fill_width = int((count / total) * bar_width)
                    bar_fill_rect = pygame.Rect(self.x + 10, y + 20, fill_width, bar_height)
                    pygame.draw.rect(screen, colors[label], bar_fill_rect)
                
                y += 45
                
        except Exception as e:
            print(f"Error drawing distribution bars: {e}") 