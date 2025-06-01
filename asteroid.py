import pygame
import random
import math
from circleshape import CircleShape
from constants import *
from enemy_projectile import EnemyProjectile

# Import sound to avoid circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class Asteroid(CircleShape):
    def __init__(self, x, y, radius, asteroid_type=None):
        super().__init__(x, y, radius)
        
        # Randomly select asteroid type if not specified
        if asteroid_type is None:
            # Initially more regular asteroids, with lower chances for special types
            weights = [0.7, 0.15, 0.15]  # Regular, Explosive, Armored
            asteroid_types = [ASTEROID_TYPE_REGULAR, ASTEROID_TYPE_EXPLOSIVE, ASTEROID_TYPE_ARMORED]
            self.asteroid_type = random.choices(asteroid_types, weights=weights)[0]
        else:
            self.asteroid_type = asteroid_type
            
        self.score_value = self._get_score_value()
        
        # For armored asteroids
        if self.asteroid_type == ASTEROID_TYPE_ARMORED:
            self.hits_remaining = ARMORED_HITS_REQUIRED
        else:
            self.hits_remaining = 1

    def _get_score_value(self):
        """Calculate score value based on asteroid size and type"""
        base_score = 0
        
        # Base score from size
        if self.radius >= ASTEROID_MAX_RADIUS:
            base_score = SCORE_LARGE_ASTEROID
        elif self.radius >= ASTEROID_MIN_RADIUS * 2:
            base_score = SCORE_MEDIUM_ASTEROID
        else:
            base_score = SCORE_SMALL_ASTEROID
            
        # Adjust score based on type
        if self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            return int(base_score * 1.5)  # Explosive asteroids worth more
        elif self.asteroid_type == ASTEROID_TYPE_ARMORED:
            return int(base_score * 2)    # Armored asteroids worth even more
        else:
            return base_score             # Regular asteroids

    def draw(self, screen):
        """Draw the asteroid with unique visual indicators based on type"""
        # Base asteroid circle
        if self.asteroid_type == ASTEROID_TYPE_REGULAR:
            # Regular asteroid - white circle
            pygame.draw.circle(
                screen,
                color=(225, 225, 225),
                center=[self.position.x, self.position.y],
                radius=self.radius, width=2
            )
        elif self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            # Explosive asteroid - orange/red with spiky appearance
            pygame.draw.circle(
                screen,
                color=(255, 100, 0),  # Orange
                center=[self.position.x, self.position.y],
                radius=self.radius, width=2
            )
            
            # Add spikes to indicate explosiveness
            num_spikes = 8
            spike_length = self.radius * 0.3
            for i in range(num_spikes):
                angle = 2 * math.pi * i / num_spikes
                inner_x = self.position.x + (self.radius - 5) * math.cos(angle)
                inner_y = self.position.y + (self.radius - 5) * math.sin(angle)
                outer_x = self.position.x + (self.radius + spike_length) * math.cos(angle)
                outer_y = self.position.y + (self.radius + spike_length) * math.sin(angle)
                pygame.draw.line(screen, (255, 100, 0), (inner_x, inner_y), (outer_x, outer_y), 2)
        
        elif self.asteroid_type == ASTEROID_TYPE_ARMORED:
            # Armored asteroid - blue/metallic with shield indicator
            pygame.draw.circle(
                screen,
                color=(100, 100, 255),  # Blue-ish
                center=[self.position.x, self.position.y],
                radius=self.radius, width=2
            )
            
            # Draw inner circles to indicate remaining armor
            for i in range(self.hits_remaining):
                armor_radius = self.radius - (4 * (ARMORED_HITS_REQUIRED - i))
                pygame.draw.circle(
                    screen,
                    color=(150, 150, 255),
                    center=[self.position.x, self.position.y],
                    radius=armor_radius, width=1
                )
    def update(self, dt):
        self.position += (self.velocity * dt)

    def hit(self):
        """Handle what happens when the asteroid is hit"""
        # For armored asteroids, decrement hits
        if self.asteroid_type == ASTEROID_TYPE_ARMORED:
            self.hits_remaining -= 1
            
            # If armored asteroid still has hits remaining, don't destroy it
            if self.hits_remaining > 0:
                # Play armor hit sound
                if sound_manager:
                    sound_manager.play_sound('armor_hit')
                return False  # Not destroyed yet
        
        # Handle explosion for explosive asteroid
        if self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            self._explode()
            
        # Regular splitting behavior for normal and remaining cases
        return self.split()
        
    def _explode(self):
        """Create explosion projectiles for explosive asteroids"""
        # Play special explosion sound
        if sound_manager:
            sound_manager.play_sound('big_explosion')
            
        # Create projectiles in all directions
        projectiles = []
        for i in range(EXPLOSIVE_PROJECTILE_COUNT):
            angle = 360 * i / EXPLOSIVE_PROJECTILE_COUNT
            projectile = EnemyProjectile(self.position.x, self.position.y)
            
            # Direction based on angle
            direction = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            projectile.velocity = direction * EXPLOSIVE_PROJECTILE_SPEED
            
            projectiles.append(projectile)
            
        return projectiles
        
    def split(self):
        """Split the asteroid into smaller pieces"""
        # Kill the current asteroid
        self.kill()
        
        # Check if asteroid is too small to split
        if self.radius < ASTEROID_MIN_RADIUS:
            return True  # Destroyed but no new asteroids
            
        # Create two new smaller asteroids
        angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(angle) * 1.2
        v2 = self.velocity.rotate(-angle)
        
        # Smaller asteroids have a higher chance of being regular type
        if random.random() < 0.7:
            new_type = ASTEROID_TYPE_REGULAR
        else:
            # Choose between explosive and armored for variety
            new_type = random.choice([ASTEROID_TYPE_EXPLOSIVE, ASTEROID_TYPE_ARMORED])
            
        # Create new asteroids of possibly different types    
        a1 = Asteroid(self.position.x, self.position.y, self.radius - ASTEROID_MIN_RADIUS, new_type)
        a1.velocity = v1
        
        a2 = Asteroid(self.position.x, self.position.y, self.radius - ASTEROID_MIN_RADIUS, new_type)
        a2.velocity = v2
        
        return True  # Asteroid was destroyed
