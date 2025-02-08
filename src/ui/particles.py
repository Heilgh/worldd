import pygame
import random
import math

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.particle_types = {
            'thought': {'lifetime': 2.0, 'size': (20, 20), 'alpha_fade': True},
            'emotion': {'lifetime': 1.5, 'size': (25, 25), 'alpha_fade': True},
            'effect': {'lifetime': 1.0, 'size': (15, 15), 'alpha_fade': True}
        }

    def add_particle(self, x, y, particle_type, content, velocity=(0, -1)):
        particle = {
            'pos': [x, y],
            'type': particle_type,
            'content': content,
            'lifetime': self.particle_types[particle_type]['lifetime'],
            'alpha': 255,
            'velocity': velocity,
            'size': self.particle_types[particle_type]['size']
        }
        self.particles.append(particle)

    def update(self, dt):
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
                
            particle['pos'][0] += particle['velocity'][0] * dt * 30
            particle['pos'][1] += particle['velocity'][1] * dt * 30
            
            if self.particle_types[particle['type']]['alpha_fade']:
                particle['alpha'] = int(255 * (particle['lifetime'] / 
                    self.particle_types[particle['type']]['lifetime']))

    def draw(self, screen, camera_x, camera_y):
        for particle in self.particles:
            screen_x = particle['pos'][0] - camera_x
            screen_y = particle['pos'][1] - camera_y
            
            if particle['type'] in ['thought', 'emotion']:
                font = pygame.font.Font(None, 30)
                text = font.render(particle['content'], True, (255, 255, 255))
                text.set_alpha(particle['alpha'])
                screen.blit(text, (screen_x, screen_y))
            else:
                surf = pygame.Surface(particle['size'], pygame.SRCALPHA)
                pygame.draw.circle(surf, (*particle['content'], particle['alpha']),
                                 (particle['size'][0]//2, particle['size'][1]//2),
                                 particle['size'][0]//2)
                screen.blit(surf, (screen_x, screen_y)) 