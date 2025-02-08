import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        # Load sound effects
        self.sounds = {}
        self._load_sounds()
        
        # Load music tracks
        self.music = {}
        self._load_music()
        
        # Volume settings
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.current_music = None
        
    def _load_sounds(self):
        """Load all sound effects"""
        sound_dir = os.path.join('assets', 'sounds')
        sound_files = {
            'click': 'ui_click.wav',
            'hover': 'ui_hover.wav',
            'notification': 'notification.wav',
            'ambient_day': 'ambient_day.wav',
            'ambient_night': 'ambient_night.wav',
            'rain': 'rain.wav',
            'thunder': 'thunder.wav',
            'wind': 'wind.wav',
            'wind_soft': 'wind_soft.wav'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                path = os.path.join(sound_dir, filename)
                self.sounds[sound_name] = pygame.mixer.Sound(path)
            except:
                print(f"Could not load sound: {filename}")
                
    def _load_music(self):
        """Load all music tracks"""
        music_dir = os.path.join('assets', 'music')
        music_files = {
            'menu': 'menu_theme.mp3',
            'game_day': 'day_theme.mp3',
            'game_night': 'night_theme.mp3',
            'storm': 'storm_theme.mp3'
        }
        
        for music_name, filename in music_files.items():
            self.music[music_name] = os.path.join(music_dir, filename)
            
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(self.sound_volume)
            self.sounds[sound_name].play()
            
    def play_music(self, music_name, fade_ms=1000):
        """Play a music track"""
        if music_name in self.music and music_name != self.current_music:
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(self.music[music_name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)  # -1 means loop indefinitely
            self.current_music = music_name
            
    def stop_music(self, fade_ms=1000):
        """Stop the current music"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
        
    def set_sound_volume(self, volume):
        """Set sound effects volume"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
            
    def set_music_volume(self, volume):
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume) 