import pygame
import random
import math
from constants import *
from asteroid import Asteroid
from ufo import UFO
from sound import SoundManager

# Try to import sound manager without creating circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class Wave:
    """Represents a single wave of enemies in a level"""
    def __init__(self, asteroids_count, ufo_count, asteroid_size_distribution, boss=False, name="Wave"):
        self.asteroids_count = asteroids_count  # Number of asteroids to spawn
        self.ufo_count = ufo_count  # Number of UFOs to spawn
        self.asteroid_size_distribution = asteroid_size_distribution  # Ratio of large:medium:small
        self.boss = boss  # Whether this is a boss wave
        self.name = name  # Name to display
        
        # Wave state
        self.asteroids_spawned = 0
        self.ufos_spawned = 0
        self.completed = False
        self.asteroid_timer = 0
        self.ufo_timer = 0
        
    def reset(self):
        """Reset wave state for replaying"""
        self.asteroids_spawned = 0
        self.ufos_spawned = 0
        self.completed = False
        self.asteroid_timer = 0
        self.ufo_timer = 0
        
    def is_complete(self, asteroid_count):
        """Check if wave is complete (all enemies spawned and destroyed)"""
        return (self.asteroids_spawned >= self.asteroids_count and 
                self.ufos_spawned >= self.ufo_count and 
                asteroid_count == 0)
        
    def get_next_asteroid_size(self):
        """Determine size of next asteroid based on distribution"""
        roll = random.random()
        if roll < self.asteroid_size_distribution[0]:
            return ASTEROID_KINDS  # Large
        elif roll < self.asteroid_size_distribution[0] + self.asteroid_size_distribution[1]:
            return ASTEROID_KINDS - 1  # Medium
        else:
            return 1  # Small

class LevelManager:
    """Manages game levels, waves, and difficulty progression"""
    def __init__(self, difficulty=DIFFICULTY_NORMAL):
        self.current_level = 1
        self.difficulty = difficulty
        self.difficulty_mods = DIFFICULTY_MODIFIERS[difficulty]
        
        # Level state
        self.current_wave_index = 0
        self.waves = []
        self.transition_active = False
        self.transition_timer = 0
        self.transition_duration = 3.0  # seconds
        self.level_complete = False
        self.game_complete = False
        
        # UI elements
        self.font = pygame.font.SysFont(None, FONT_SIZE * 2)
        self.small_font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Initialize first level
        self._generate_level(self.current_level)
        
    def _generate_level(self, level):
        """Generate waves for the given level number"""
        self.waves = []
        self.current_wave_index = 0
        self.level_complete = False
        
        # Base values that scale with level
        base_asteroids = 4 + level
        base_ufos = level // 2
        
        # Difficulty scaling
        asteroid_multiplier = 1.0 + ((level - 1) * 0.1)  # 10% more asteroids per level
        ufo_multiplier = 1.0 + ((level - 1) * 0.15)  # 15% more UFOs per level
        
        # Apply difficulty setting
        asteroid_multiplier *= self.difficulty_mods['spawn_rate_multiplier']
        
        # Calculate actual counts
        asteroid_count = max(1, int(base_asteroids * asteroid_multiplier))
        ufo_count = max(0, int(base_ufos * ufo_multiplier))
        
        # Wave 1: Mostly large asteroids
        self.waves.append(Wave(
            asteroids_count=asteroid_count,
            ufo_count=0,
            asteroid_size_distribution=[0.7, 0.2, 0.1],  # 70% large, 20% medium, 10% small
            name=f"Wave 1: Asteroid Field"
        ))
        
        # Wave 2: Mix of asteroids and first UFOs
        self.waves.append(Wave(
            asteroids_count=asteroid_count + 2,
            ufo_count=ufo_count,
            asteroid_size_distribution=[0.5, 0.3, 0.2],  # More balanced
            name=f"Wave 2: First Contact"
        ))
        
        # Wave 3: More challenging with faster asteroids
        self.waves.append(Wave(
            asteroids_count=asteroid_count + 4,
            ufo_count=ufo_count + 1,
            asteroid_size_distribution=[0.3, 0.4, 0.3],  # More medium asteroids
            name=f"Wave 3: Incoming Storm"
        ))
        
        # Boss wave every 3 levels
        if level % 3 == 0:
            # Boss wave - either a large UFO "mothership" or asteroid swarm
            if level % 6 == 0:
                # UFO boss wave
                self.waves.append(Wave(
                    asteroids_count=asteroid_count // 2,
                    ufo_count=ufo_count + 3,  # More UFOs
                    asteroid_size_distribution=[0.2, 0.3, 0.5],  # Mostly small, quick asteroids
                    boss=True,
                    name=f"BOSS: UFO Fleet"
                ))
            else:
                # Asteroid boss wave
                self.waves.append(Wave(
                    asteroids_count=asteroid_count * 2,  # Double asteroids
                    ufo_count=1,
                    asteroid_size_distribution=[0.6, 0.3, 0.1],  # Lots of large asteroids
                    boss=True,
                    name=f"BOSS: Asteroid Storm"
                ))
    
    def update(self, dt, asteroid_count, spawn_asteroid_func, spawn_ufo_func):
        """Update level progress and handle wave spawning"""
        if self.transition_active:
            # Handle transition screen between waves/levels
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.transition_active = False
                if self.level_complete:
                    self.current_level += 1
                    if self.current_level > 12:  # Game complete after level 12
                        self.game_complete = True
                    else:
                        self._generate_level(self.current_level)
                        self.level_complete = False
            return
        
        # Check if current wave is complete
        current_wave = self.waves[self.current_wave_index]
        if current_wave.is_complete(asteroid_count):
            # Move to next wave or level
            self.current_wave_index += 1
            if self.current_wave_index >= len(self.waves):
                # Level complete
                self.level_complete = True
                self.transition_active = True
                self.transition_timer = self.transition_duration
                if sound_manager:
                    sound_manager.play_sound('big_explosion')  # Celebration sound
            else:
                # Next wave
                self.transition_active = True
                self.transition_timer = self.transition_duration / 2  # Shorter between waves
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')  # Signal new wave
            return
        
        # Handle spawning for current wave
        current_wave.asteroid_timer -= dt
        current_wave.ufo_timer -= dt
        
        # Spawn asteroids
        if current_wave.asteroids_spawned < current_wave.asteroids_count and current_wave.asteroid_timer <= 0:
            # Calculate asteroid spawn delay (decreases with level)
            spawn_delay = max(0.5, 2.0 - (self.current_level * 0.1))
            current_wave.asteroid_timer = spawn_delay
            
            # Determine asteroid size
            size = current_wave.get_next_asteroid_size()
            
            # Call spawn function from main game
            spawn_asteroid_func(size)
            current_wave.asteroids_spawned += 1
        
        # Spawn UFOs
        if current_wave.ufos_spawned < current_wave.ufo_count and current_wave.ufo_timer <= 0:
            # Calculate UFO spawn delay
            spawn_delay = max(3.0, 8.0 - (self.current_level * 0.5))
            current_wave.ufo_timer = spawn_delay
            
            # Call spawn function from main game
            spawn_ufo_func()
            current_wave.ufos_spawned += 1
    
    def draw_transition(self, screen):
        """Draw level/wave transition screen"""
        if not self.transition_active:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        if self.level_complete:
            # Level complete message
            level_text = self.font.render(f"LEVEL {self.current_level} COMPLETE!", True, (255, 255, 255))
            screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            
            # Next level message
            if self.current_level < 12:  # Max level
                next_text = self.small_font.render(f"Prepare for Level {self.current_level + 1}", True, (200, 200, 200))
                screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            else:
                # Final level complete
                next_text = self.small_font.render("Congratulations! You've completed the game!", True, (255, 215, 0))
                screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        else:
            # Wave introduction
            next_wave = self.waves[self.current_wave_index]
            wave_text = self.font.render(next_wave.name, True, (255, 255, 255))
            screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            
            # Wave info
            if next_wave.boss:
                # Boss wave - red alert text
                info_text = self.small_font.render("WARNING: Boss Wave Incoming!", True, (255, 50, 50))
            else:
                info_text = self.small_font.render(f"Asteroids: {next_wave.asteroids_count}   UFOs: {next_wave.ufo_count}", True, (200, 200, 200))
            
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def draw_hud(self, screen, x, y):
        """Draw level and wave information on HUD"""
        level_text = self.small_font.render(f"Level: {self.current_level}", True, (255, 255, 255))
        screen.blit(level_text, (x, y))
        
        wave_text = self.small_font.render(f"Wave: {self.current_wave_index + 1}/{len(self.waves)}", True, (255, 255, 255))
        screen.blit(wave_text, (x, y + FONT_SIZE))
        
        # Progress in current wave
        current_wave = self.waves[self.current_wave_index]
        progress_text = self.small_font.render(
            f"Wave Progress: {current_wave.asteroids_spawned}/{current_wave.asteroids_count} asteroids, "
            f"{current_wave.ufos_spawned}/{current_wave.ufo_count} UFOs", 
            True, (200, 200, 200)
        )
        screen.blit(progress_text, (x, y + FONT_SIZE * 2))
        
        return y + FONT_SIZE * 3  # Return next Y position for other HUD elements
    
    def get_score_multiplier(self):
        """Get score multiplier based on current level"""
        # Base multiplier from difficulty setting
        base_multiplier = self.difficulty_mods['score_multiplier']
        
        # Level multiplier - increases by 0.1 per level
        level_multiplier = 1.0 + ((self.current_level - 1) * 0.1)
        
        # Boss wave bonus
        if self.waves[self.current_wave_index].boss:
            boss_multiplier = 1.5
        else:
            boss_multiplier = 1.0
            
        return base_multiplier * level_multiplier * boss_multiplier

