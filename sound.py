import os
import pygame
import wave
import struct
import math
import random
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
            pygame.mixer.init()
        
        # Create sound directories if they don't exist
        self._create_sound_directories()
        
        # Dictionary to store sound effects
        self.sounds = {}
        
        # Load sound effects
        self._load_sounds()
    
    def _create_sound_directories(self):
        """Create necessary directories for sound files"""
        directories = ['assets', 'assets/sounds', 'assets/music']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    
    def _load_sounds(self):
        """Load all sound effects"""
        # Create placeholder sound files if they don't exist
        self._create_placeholder_sounds()
        
        # Load sound effects
        sound_files = {
            'shoot': 'assets/sounds/shoot.wav',
            'explosion_small': 'assets/sounds/explosion_small.wav',
            'explosion_medium': 'assets/sounds/explosion_medium.wav',
            'explosion_large': 'assets/sounds/explosion_large.wav',
            'player_death': 'assets/sounds/player_death.wav',
            'ufo_shoot': 'assets/sounds/ufo_shoot.wav',
            'ufo_appear': 'assets/sounds/ufo_appear.wav',
            'armor_hit': 'assets/sounds/armor_hit.wav',
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
    
    def _create_placeholder_sounds(self):
        """Create placeholder sound files if they don't exist"""
        
        # Define the sound files to create if they don't exist
        sounds_to_create = [
            ('assets/sounds/shoot.wav', 0.2, 'phaser'),  # Phaser sound
            ('assets/sounds/explosion_small.wav', 0.3, 'explosion'),  # Small explosion
            ('assets/sounds/explosion_medium.wav', 0.4, 'explosion'),  # Medium explosion
            ('assets/sounds/explosion_large.wav', 0.5, 'explosion'),  # Large explosion
            ('assets/sounds/player_death.wav', 0.8, 'explosion'),  # Player death sound
            ('assets/sounds/ufo_shoot.wav', 0.2, 'alien'),  # UFO shoot sound
            ('assets/sounds/ufo_appear.wav', 0.8, 'alien'),  # UFO appear sound
            ('assets/sounds/armor_hit.wav', 0.3, 'impact'),  # Armor hit sound
            ('assets/sounds/big_explosion.wav', 0.7, 'explosion'),  # Big explosion sound
            ('assets/sounds/thrust.wav', 0.5, 'engine'),  # Thrust engine sound
            ('assets/sounds/phaser.wav', 0.3, 'phaser'),  # Phaser weapon sound
            ('assets/music/background.wav', 20.0, 'music')  # Background music - longer for better looping
        ]
        
        for sound_info in sounds_to_create:
            sound_file = sound_info[0]
            duration = sound_info[1]
            sound_type = sound_info[2]
            
            if not os.path.exists(sound_file):
                # Create sound based on type
                try:
                    if sound_type == 'phaser':
                        self._create_phaser_sound(sound_file, duration)
                    elif sound_type == 'explosion':
                        self._create_explosion_sound(sound_file, duration)
                    elif sound_type == 'alien':
                        self._create_alien_sound(sound_file, duration)
                    elif sound_type == 'impact':
                        self._create_impact_sound(sound_file, duration)
                    elif sound_type == 'engine':
                        self._create_engine_sound(sound_file, duration)
                    elif sound_type == 'music':
                        self._create_space_music(sound_file, duration)
                    else:
                        self._create_simple_sound(sound_file, duration)
                    print(f"Created placeholder sound: {sound_file}")
                except Exception as e:
                    print(f"Error creating placeholder sound {sound_file}: {e}")
    
    def _create_simple_sound(self, filename, duration=0.5, freq=440.0, volume=0.5):
        """Create a simple sine wave sound file"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Generate simple sine wave
            max_amplitude = 2 ** (bits - 1) - 1
            step = freq * 2 * math.pi / sample_rate
            
            # Create frames
            for i in range(n_frames):
                # Simple fade in/out
                if i < n_frames // 4:
                    fade = i / (n_frames // 4)
                elif i > n_frames * 3 // 4:
                    fade = (n_frames - i) / (n_frames // 4)
                else:
                    fade = 1.0
                
                # Calculate sample value - properly using sine function
                value = int(max_amplitude * volume * fade * 0.8 * math.sin(i * step))
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)
                
    def _create_phaser_sound(self, filename, duration=0.3, volume=0.6):
        """Create a sci-fi phaser/laser sound effect"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Generate phaser sound with frequency sweep
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Frequency sweep parameters
            start_freq = 880.0  # Higher pitch start
            end_freq = 220.0    # Lower pitch end
            
            # Create frames
            for i in range(n_frames):
                # Calculate frequency at this point in time
                t = i / n_frames
                freq = start_freq + t * (end_freq - start_freq)
                
                # Add modulation for sci-fi effect
                mod_freq = 10 + 50 * t  # Modulation frequency increases
                mod_depth = 0.3 * (1 - t)  # Modulation depth decreases
                
                # Phase calculation
                phase = 2 * math.pi * freq * i / sample_rate
                mod_phase = 2 * math.pi * mod_freq * i / sample_rate
                
                # Simple fade out
                if i > n_frames * 0.7:
                    fade = (n_frames - i) / (n_frames * 0.3)
                else:
                    fade = 1.0
                
                # Calculate sample value with modulation
                value = int(max_amplitude * volume * fade * 
                            math.sin(phase + mod_depth * math.sin(mod_phase)))
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)

    def _create_explosion_sound(self, filename, duration=0.5, volume=0.7):
        """Create an explosion sound effect"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Maximum amplitude without clipping
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Noise parameters - explosions are noisy
            noise_level = 0.8
            
            # Create frames with noise and low frequency rumble
            for i in range(n_frames):
                # Calculate time position
                t = i / n_frames
                
                # Exponential decay envelope
                env = math.exp(-4 * t)
                
                # Low frequency rumble
                rumble_freq = 60.0 + 20.0 * t  # Slight frequency rise
                rumble_phase = 2 * math.pi * rumble_freq * i / sample_rate
                rumble = math.sin(rumble_phase) * 0.7
                
                # Random noise component
                noise = (random.random() * 2 - 1) * noise_level
                
                # Combine components with envelope
                sample = (noise * 0.6 + rumble * 0.4) * env
                
                # Apply volume and convert to int
                value = int(max_amplitude * volume * sample)
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)

    def _create_alien_sound(self, filename, duration=0.5, volume=0.6):
        """Create an alien/UFO sound effect"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Maximum amplitude
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Multiple oscillator parameters for alien sound
            base_freq = 300.0  # Base frequency
            
            # Create frames
            for i in range(n_frames):
                # Calculate time position
                t = i / n_frames
                
                # Warbling effect with multiple frequencies
                freq1 = base_freq * (1.0 + 0.1 * math.sin(2 * math.pi * 5 * t))
                freq2 = base_freq * 1.5 * (1.0 + 0.1 * math.sin(2 * math.pi * 3 * t))
                
                # Phase calculation
                phase1 = 2 * math.pi * freq1 * i / sample_rate
                phase2 = 2 * math.pi * freq2 * i / sample_rate
                
                # Fade in/out
                if i < n_frames * 0.2:
                    fade = i / (n_frames * 0.2)
                elif i > n_frames * 0.8:
                    fade = (n_frames - i) / (n_frames * 0.2)
                else:
                    fade = 1.0
                
                # Calculate sample with multiple oscillators
                osc1 = math.sin(phase1) * 0.6
                osc2 = math.sin(phase2) * 0.4
                sample = osc1 + osc2
                
                # Apply volume, fade and convert to int
                value = int(max_amplitude * volume * fade * sample)
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)

    def _create_impact_sound(self, filename, duration=0.3, volume=0.6):
        """Create an impact/collision sound effect"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Maximum amplitude
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Impact sound parameters
            base_freq = 200.0
            
            # Create frames
            for i in range(n_frames):
                # Calculate time position
                t = i / n_frames
                
                # Fast attack, slower decay
                if i < n_frames * 0.05:  # Quick attack
                    env = i / (n_frames * 0.05)
                else:  # Longer decay
                    env = math.exp(-8 * (t - 0.05))
                
                # Frequency drops quickly after impact
                freq = base_freq * (1.0 - 0.5 * min(1.0, t * 4))
                
                # Add some noise for metallic quality
                noise = (random.random() * 2 - 1) * 0.3
                
                # Phase calculation
                phase = 2 * math.pi * freq * i / sample_rate
                
                # Calculate sample with noise
                sample = math.sin(phase) * 0.7 + noise * 0.3
                
                # Apply envelope and convert to int
                value = int(max_amplitude * volume * env * sample)
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)

    def _create_engine_sound(self, filename, duration=0.5, volume=0.5):
        """Create a spaceship engine/thrust sound effect"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Maximum amplitude
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Engine sound parameters - mostly noise based
            base_freq = 100.0  # Low rumble frequency
            
            # Create frames
            for i in range(n_frames):
                # Calculate time position
                t = i / n_frames
                
                # Fade in/out
                if i < n_frames * 0.1:
                    fade = i / (n_frames * 0.1)
                elif i > n_frames * 0.9:
                    fade = (n_frames - i) / (n_frames * 0.1)
                else:
                    fade = 1.0
                
                # Engine rumble - low frequency oscillation
                rumble_phase = 2 * math.pi * base_freq * i / sample_rate
                rumble = math.sin(rumble_phase) * 0.3
                
                # Add filtered noise for the "thrust" sound
                noise = 0
                for j in range(5):  # Simple noise filtering
                    noise += (random.random() * 2 - 1) * (0.7 - j * 0.1)
                noise /= 5
                
                # Combine components
                sample = (noise * 0.7 + rumble * 0.3) * fade
                
                # Apply volume and convert to int
                value = int(max_amplitude * volume * sample)
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)

    def _create_space_music(self, filename, duration=20.0, volume=0.5):
        """Create ambient space music"""
        sample_rate = 44100
        bits = 16
        
        # Calculate number of frames
        n_frames = int(duration * sample_rate)
        
        # Create file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setparams((1, bits // 8, sample_rate, n_frames, 'NONE', 'not compressed'))
            
            # Maximum amplitude
            max_amplitude = 2 ** (bits - 1) - 1
            
            # Music parameters
            # Use a pentatonic scale for space ambience
            scale = [220.0, 261.63, 329.63, 392.0, 440.0]  # A, C, E, G, A
            
            # Chord progression timing (in seconds)
            chord_duration = 4.0
            chords = [
                [0, 2, 4],  # A minor
                [1, 3, 0],  # C major
                [2, 4, 1],  # E minor
                [3, 0, 2]   # G major
            ]
            
            # LFO (Low Frequency Oscillator) for subtle modulation
            lfo_freq = 0.2  # Very slow modulation
            
            # Arpeggiated patterns
            arp_speed = 0.25  # Quarter notes
            
            # Create frames
            chord_index = 0
            for i in range(n_frames):
                # Calculate time position
                t = i / sample_rate  # Time in seconds
                
                # Determine current chord
                chord_index = int(t / chord_duration) % len(chords)
                chord = chords[chord_index]
                
                # Crossfade between chords
                chord_pos = (t % chord_duration) / chord_duration
                next_chord_index = (chord_index + 1) % len(chords)
                next_chord = chords[next_chord_index]
                
                # Arpeggiation pattern
                arp_pos = int(t / arp_speed) % 3
                
                # Base frequency from current chord
                base_note = scale[chord[arp_pos]]
                
                # Calculate sample with multiple oscillators and subtle modulation
                sample = 0
                
                # Main note
                mod = 0.02 * math.sin(2 * math.pi * lfo_freq * t)  # Subtle pitch modulation
                phase1 = 2 * math.pi * base_note * (1 + mod) * t
                sample += 0.3 * math.sin(phase1)
                
                # Fifth
                phase2 = 2 * math.pi * (base_note * 1.5) * (1 + mod) * t
                sample += 0.2 * math.sin(phase2)
                
                # Octave
                phase3 = 2 * math.pi * (base_note * 2) * (1 + mod) * t
                sample += 0.15 * math.sin(phase3)
                
                # Pad sound (slow attack/release)
                pad_env = 0.15  # Constant level for pad
                pad_freq = scale[chord[0]] / 2  # Lower octave
                phase_pad = 2 * math.pi * pad_freq * t
                sample += pad_env * 0.2 * math.sin(phase_pad)
                
                # Gentle white noise for texture
                texture = (random.random() * 2 - 1) * 0.05
                
                # Combine everything
                final_sample = sample + texture
                
                # Apply volume and convert to int
                value = int(max_amplitude * volume * final_sample)
                
                # Pack into frame
                data = struct.pack('<h', value)
                wav_file.writeframes(data)
    
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
            # Use a channel to allow looping and control
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
        if size >= 60:  # Large asteroid
            self.play_sound('explosion_large')
        elif size >= 40:  # Medium asteroid
            self.play_sound('explosion_medium')
        else:  # Small asteroid
            self.play_sound('explosion_small')
    
    def start_background_music(self):
        """Start playing background music in a loop"""
        if not self.enabled:
            return
            
        music_file = 'assets/music/background.wav'
        
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                print("Background music started")
            except Exception as e:
                print(f"Error starting background music: {e}")
    
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
            
            # Restart music if it was playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                self.start_background_music()
        else:
            pygame.mixer.music.set_volume(0)
            for sound in self.sounds.values():
                sound.set_volume(0)
            
            # Pause music but don't stop it
            pygame.mixer.music.pause()

