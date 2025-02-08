import pygame
from ..constants import UI_COLORS

class NotificationSystem:
    def __init__(self):
        self.notifications = []
        self.font = pygame.font.Font(None, 24)
        self.notification_lifetime = 3.0
        self.fade_time = 0.5
        
    def add_notification(self, text, type='info'):
        colors = {
            'info': (100, 100, 255),
            'warning': (255, 200, 0),
            'error': (255, 100, 100),
            'success': (100, 255, 100)
        }
        
        self.notifications.append({
            'text': text,
            'type': type,
            'color': colors.get(type, colors['info']),
            'lifetime': self.notification_lifetime,
            'alpha': 255
        })
        
    def update(self, dt):
        for notif in self.notifications[:]:
            notif['lifetime'] -= dt
            if notif['lifetime'] <= 0:
                self.notifications.remove(notif)
            elif notif['lifetime'] < self.fade_time:
                notif['alpha'] = int(255 * (notif['lifetime'] / self.fade_time))
                
    def draw(self, screen):
        y_offset = 10
        for notif in self.notifications:
            text_surface = self.font.render(notif['text'], True, notif['color'])
            text_surface.set_alpha(notif['alpha'])
            x = screen.get_width() - text_surface.get_width() - 10
            screen.blit(text_surface, (x, y_offset))
            y_offset += text_surface.get_height() + 5 