import os
import pygame # type: ignore
from constants import SOUND_ENABLED, MUSIC_VOLUME, SFX_VOLUME

class SoundManager:
    """Manages all game sounds and music"""
    
    def __init__(self):
        """Initialize the sound manager"""
        self.enabled = SOUND_ENABLED
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        
        # Ensure pygame mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        # Create sound directories if they don't exist
        self._create_sound_directories()
        
        # Dictionary to store sound effects
        self.sounds = {}
        
        # Load sound effects if available in the assets folder
        self._load_sounds()
    
    def _create_sound_directories(self):
        """Create necessary directories for sound files"""
        directories = ['assets', 'assets/sounds', 'assets/music']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    
    def _load_sounds(self):
        """Load all sound effects if available"""
        sound_files = {
            'shoot': 'assets/sounds/sfx_laser1.ogg',
            'explosion_small': 'assets/sounds/explosion_small.wav',
            'explosion_medium': 'assets/sounds/explosion_medium.wav',
            'explosion_large': 'assets/sounds/explosion_large.wav',
            'player_death': 'assets/sounds/sfx_lose.ogg',
            'ufo_shoot': 'assets/sounds/laser2.ogg',
            'ufo_appear': 'assets/sounds/ufo_appear.wav',
            'big_explosion': 'assets/sounds/big_explosion.wav',
            'thrust': 'assets/sounds/thrust.wav',
            'phaser': 'assets/sounds/phaser.wav'
        }
        
        for sound_name, sound_path in sound_files.items():
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {sound_name}")
                except Exception as e:
                    print(f"Error loading sound {sound_name}: {e}")
            else:
                print(f"Sound file not found: {sound_path}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def play_thrust_sound(self):
        """Play the thrust sound for ship movement"""
        if not self.enabled:
            return
            
        if 'thrust' in self.sounds:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.sounds['thrust'], loops=0)
                
    def play_phaser_sound(self):
        """Play the phaser sound for advanced weapons"""
        if not self.enabled:
            return
            
        if 'phaser' in self.sounds:
            self.sounds['phaser'].play()
    
    def play_explosion_sound(self, size):
        """Play the appropriate explosion sound based on asteroid size"""
        if size >= 60:
            self.play_sound('explosion_large')
        elif size >= 40:
            self.play_sound('explosion_medium')
        else:
            self.play_sound('explosion_small')
    
    def start_background_music(self):
        """Start playing background music in a loop"""
        if not self.enabled:
            return
            
        music_file = 'assets/music/space.wav'
        
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                print("Background music started")
            except Exception as e:
                print(f"Error starting background music: {e}")
        else:
            print(f"Background music file not found: {music_file}")
    
    def stop_background_music(self):
        """Stop the background music"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Set the music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set the sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_sound(self):
        """Toggle all game sounds on/off"""
        self.enabled = not self.enabled
        
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                self.start_background_music()
        else:
            pygame.mixer.music.set_volume(0)
            for sound in self.sounds.values():
                sound.set_volume(0)
            
            pygame.mixer.music.pause()
