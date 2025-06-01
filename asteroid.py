import pygame
import random
import math
import os
from circleshape import CircleShape
from constants import *
from enemy_projectile import EnemyProjectile
from effects import EffectManager

# Global effect manager
effect_manager = None

# Import sound to avoid circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class Asteroid(CircleShape):
    # Class variables for sprite collections
    meteor_sprites = {
        'brown': {
            'big': [], 
            'medium': [], 
            'small': [], 
            'tiny': []
        },
        'grey': {
            'big': [], 
            'medium': [], 
            'small': [], 
            'tiny': []
        }
    }
    
    sprites_loaded = False
    
    @classmethod
    def load_sprites(cls):
        """Load all meteor sprites into class variables"""
        if cls.sprites_loaded:
            return
            
        # Brown meteors
        for i in range(1, 5):  # big1 through big4
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorBrown_big{i}.png").convert_alpha()
                cls.meteor_sprites['brown']['big'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorBrown_big{i}.png")
                
        for i in range(1, 3):  # med1 through med2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorBrown_med{i}.png").convert_alpha()
                cls.meteor_sprites['brown']['medium'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorBrown_med{i}.png")
                
        for i in range(1, 3):  # small1 through small2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorBrown_small{i}.png").convert_alpha()
                cls.meteor_sprites['brown']['small'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorBrown_small{i}.png")
                
        for i in range(1, 3):  # tiny1 through tiny2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorBrown_tiny{i}.png").convert_alpha()
                cls.meteor_sprites['brown']['tiny'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorBrown_tiny{i}.png")
                
        # Grey meteors
        for i in range(1, 5):  # big1 through big4
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorGrey_big{i}.png").convert_alpha()
                cls.meteor_sprites['grey']['big'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorGrey_big{i}.png")
                
        for i in range(1, 3):  # med1 through med2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorGrey_med{i}.png").convert_alpha()
                cls.meteor_sprites['grey']['medium'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorGrey_med{i}.png")
                
        for i in range(1, 3):  # small1 through small2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorGrey_small{i}.png").convert_alpha()
                cls.meteor_sprites['grey']['small'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorGrey_small{i}.png")
                
        for i in range(1, 3):  # tiny1 through tiny2
            try:
                sprite = pygame.image.load(f"assets/images/Meteors/meteorGrey_tiny{i}.png").convert_alpha()
                cls.meteor_sprites['grey']['tiny'].append(sprite)
            except pygame.error:
                print(f"Error loading meteorGrey_tiny{i}.png")
                
        # Load fallback sprites if needed
        if not cls.meteor_sprites['brown']['big'] and not cls.meteor_sprites['grey']['big']:
            try:
                sprite = pygame.image.load("assets/images/meteorBig.png").convert_alpha()
                cls.meteor_sprites['brown']['big'].append(sprite)
                cls.meteor_sprites['grey']['big'].append(sprite)
            except pygame.error:
                print("Error loading fallback meteorBig.png")
                
        if not cls.meteor_sprites['brown']['small'] and not cls.meteor_sprites['grey']['small']:
            try:
                sprite = pygame.image.load("assets/images/meteorSmall.png").convert_alpha()
                cls.meteor_sprites['brown']['small'].append(sprite)
                cls.meteor_sprites['grey']['small'].append(sprite)
            except pygame.error:
                print("Error loading fallback meteorSmall.png")
                
        cls.sprites_loaded = True
    
    def __init__(self, x, y, radius, asteroid_type=None):
        super().__init__(x, y, radius)
        
        # Create effect manager if not already created
        global effect_manager
        if effect_manager is None:
            effect_manager = EffectManager()
        
        # Load meteor sprites if not already loaded
        Asteroid.load_sprites()
            
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
        
        # Randomly choose between brown and grey meteor variants
        self.color_variant = random.choice(['brown', 'grey'])
        
        # Select size category based on radius
        if self.radius >= ASTEROID_MIN_RADIUS * 2.5:
            size_category = 'big'
        elif self.radius >= ASTEROID_MIN_RADIUS * 1.5:
            size_category = 'medium'
        elif self.radius >= ASTEROID_MIN_RADIUS:
            size_category = 'small'
        else:
            size_category = 'tiny'
            
        # Select random sprite from appropriate category
        sprites = Asteroid.meteor_sprites[self.color_variant][size_category]
        if sprites:
            original_sprite = random.choice(sprites)
        else:
            # Fallback if no sprites found for this category
            if size_category in ['big', 'medium']:
                original_sprite = random.choice(Asteroid.meteor_sprites['brown']['big'] or Asteroid.meteor_sprites['grey']['big'])
            else:
                original_sprite = random.choice(Asteroid.meteor_sprites['brown']['small'] or Asteroid.meteor_sprites['grey']['small'])
            
        # Scale sprite to match asteroid radius
        # Compute scale factor to maintain aspect ratio
        sprite_size = self.radius * 2  # Diameter
        original_width, original_height = original_sprite.get_size()
        scale_factor = sprite_size / max(original_width, original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        self.sprite = pygame.transform.scale(original_sprite, (new_width, new_height))
        
        # Special visual effects initialization
        self.hit_flash_timer = 0
        self.is_hit = False
        self.shield_animation_angle = random.uniform(0, 360)
        self.shield_pulse = 0
        self.shield_growing = True
        
        # For explosive asteroids, add occasional particle trails
        self.trail_timer = 0
        
        # Random rotation for variety
        self.rotation = random.randrange(0, 360)
        self.rotation_speed = random.randrange(-30, 30)

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
        # Create a copy of the sprite to modify (for tinting)
        sprite_copy = self.sprite.copy()
        
        # Apply color tint based on asteroid type
        if self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            # Red/orange tint for explosive asteroids
            red_overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 0, 35))  # Subtle orange tint
            sprite_copy.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            
            # Add fiery glow effect
            glow_size = self.radius * 1.3
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_color = (255, 100, 0, 40)  # Semi-transparent orange
            pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
            glow_rect = glow_surf.get_rect(center=self.position)
            screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_RGBA_ADD)
            
            # Add trailing particles for explosive asteroids occasionally
            if random.random() < 0.1:  # 10% chance each frame
                # Random position on the asteroid's edge
                angle = random.uniform(0, 2 * math.pi)
                offset = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.radius
                particle_pos = self.position + offset
                
                # Add a small ember particle
                effect_manager.add_particle_system(
                    particle_pos,
                    effect_type="sparkle",
                    colors=[(255, 150, 0, 150), (255, 50, 0, 150)],
                    particle_count=2,
                    size_range=(1, 3),
                    speed_range=(5, 15),
                    duration=0.5
                )
            
        elif self.asteroid_type == ASTEROID_TYPE_ARMORED:
            # Blue tint for armored asteroids
            blue_overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
            blue_overlay.fill((100, 100, 255, 35))  # Subtle blue tint
            sprite_copy.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            
            # Draw shield effect using shield animation
            # Pulse the shield size for a dynamic effect
            self.shield_pulse += 0.05 if self.shield_growing else -0.05
            if self.shield_pulse >= 1.0:
                self.shield_pulse = 1.0
                self.shield_growing = False
            elif self.shield_pulse <= 0.5:
                self.shield_pulse = 0.5
                self.shield_growing = True
                
            # Rotate shield rings for a dynamic effect
            self.shield_animation_angle += 0.5
            
            # Draw multiple shield rings with different rotations
            for i in range(self.hits_remaining):
                shield_radius = self.radius + 5 * self.shield_pulse - (2 * i)
                num_segments = 16
                segment_angle = 2 * math.pi / num_segments
                start_angle = math.radians(self.shield_animation_angle + (i * 30))
                
                for j in range(num_segments):
                    if j % 2 == 0:  # Draw every other segment for a dashed effect
                        angle1 = start_angle + j * segment_angle
                        angle2 = start_angle + (j + 0.8) * segment_angle
                        start_pos = (
                            self.position.x + math.cos(angle1) * shield_radius,
                            self.position.y + math.sin(angle1) * shield_radius
                        )
                        end_pos = (
                            self.position.x + math.cos(angle2) * shield_radius,
                            self.position.y + math.sin(angle2) * shield_radius
                        )
                        pygame.draw.line(
                            screen,
                            (150, 150, 255),
                            start_pos,
                            end_pos,
                            width=2
                        )
        
        # Add hit flash effect if recently hit
        if self.is_hit and self.hit_flash_timer > 0:
            # White flash effect
            flash_alpha = int(255 * (self.hit_flash_timer / 0.2))  # Fade over 0.2 seconds
            flash_overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, flash_alpha))
            sprite_copy.blit(flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
        # Rotate and position the sprite
        rotated_sprite = pygame.transform.rotate(sprite_copy, self.rotation)
        sprite_rect = rotated_sprite.get_rect(center=self.position)
        
        # Draw the asteroid sprite
        screen.blit(rotated_sprite, sprite_rect)
    def update(self, dt):
        self.position += (self.velocity * dt)
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update hit flash timer
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer <= 0:
                self.is_hit = False
                
        # For explosive asteroids, add trailing particles occasionally
        if self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                self.trail_timer = random.uniform(0.1, 0.3)  # Random interval for natural effect
                
                # Calculate position behind the asteroid based on velocity
                if self.velocity.length() > 0:
                    direction = self.velocity.normalize()
                    trail_pos = self.position - direction * self.radius * 0.8
                    
                    # Add trail particle
                    effect_manager.add_particle_system(
                        trail_pos,
                        effect_type="sparkle",
                        colors=[(255, 150, 0, 100), (255, 100, 0, 80)],
                        particle_count=3,
                        size_range=(1, 3),
                        speed_range=(5, 15),
                        duration=0.4
                    )

    def hit(self):
        """Handle what happens when the asteroid is hit"""
        # Visual hit effect
        self.is_hit = True
        self.hit_flash_timer = 0.2  # 200ms flash
        
        # Add hit particles
        effect_manager.add_particle_system(
            self.position,
            effect_type="sparkle",
            colors=[(200, 200, 200, 150), (150, 150, 150, 150)],
            particle_count=8,
            size_range=(1, 3),
            speed_range=(50, 100),
            duration=0.3
        )
        
        # For armored asteroids, decrement hits
        if self.asteroid_type == ASTEROID_TYPE_ARMORED:
            self.hits_remaining -= 1
            
            # If armored asteroid still has hits remaining, don't destroy it
            if self.hits_remaining > 0:
                # Play armor hit sound
                if sound_manager:
                    sound_manager.play_sound('armor_hit')
                
                # Add shield impact effect
                shield_impact_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
                shield_color = (100, 150, 255, 150)  # Blue shield color
                pygame.draw.circle(shield_impact_surf, shield_color, 
                                 (self.radius * 2, self.radius * 2), self.radius * 1.5, 3)
                shield_rect = shield_impact_surf.get_rect(center=self.position)
                
                return False  # Not destroyed yet
        
        # Handle explosion for explosive asteroid
        if self.asteroid_type == ASTEROID_TYPE_EXPLOSIVE:
            self._explode()
            
        # Regular splitting behavior for normal and remaining cases
        return self.split()
        
    def _explode(self):
        """Create explosion projectiles and visual effects for explosive asteroids"""
        # Play special explosion sound
        if sound_manager:
            sound_manager.play_sound('big_explosion')
            
        # Create a large explosion effect
        effect_manager.add_particle_system(
            self.position,
            effect_type="explosion",
            colors=[(255, 200, 50, 200), (255, 100, 0, 200), (200, 0, 0, 200)],
            particle_count=40,
            size_range=(3, 8),
            speed_range=(50, 150),
            duration=1.0
        )
            
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
        """Split the asteroid into smaller pieces with visual effects"""
        # Create explosion effect before killing
        size_category = 'large'
        if self.radius < ASTEROID_MIN_RADIUS * 2:
            size_category = 'medium'
        if self.radius < ASTEROID_MIN_RADIUS * 1.5:
            size_category = 'small'
            
        # Play appropriate explosion sound based on size
        if sound_manager:
            if size_category == 'large':
                sound_manager.play_sound('explosion_large')
            elif size_category == 'medium':
                sound_manager.play_sound('explosion_medium')
            else:
                sound_manager.play_sound('explosion_small')
        
        # Add explosion particles
        if size_category == 'large':
            particle_count = 25
            size_range = (2, 6)
        elif size_category == 'medium':
            particle_count = 15
            size_range = (2, 5)
        else:
            particle_count = 10
            size_range = (1, 4)
            
        # Create explosion effect
        effect_manager.add_particle_system(
            self.position,
            particle_count=particle_count,
            size_range=size_range,
            speed_range=(30, 80),
            duration=0.8,
            colors=[(200, 200, 200, 200), (150, 150, 150, 200)]
        )
        
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
