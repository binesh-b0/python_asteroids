import pygame
import random
import math
from circleshape import CircleShape
from constants import *
from enemy_projectile import EnemyProjectile

# Import sound here to avoid circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class UFO(CircleShape):
    """UFO enemy that moves in a pattern and shoots at the player"""
    # Class sprite variables
    ufo_sprite = None
    enemy_ship_sprite = None
    
    def __init__(self, x, y, is_ufo=True):
        super().__init__(x, y, UFO_RADIUS)
        self.shoot_timer = 0
        self.score_value = UFO_SCORE
        self.target = None  # Player target
        self.movement_pattern = self._select_movement_pattern()
        self.pattern_time = 0
        self.is_ufo = is_ufo  # Type flag: UFO or enemy ship
        self.damaged = False  # Track damage state for visual effects
        self.damage_flash_timer = 0  # Timer for damage flash effect
        self.rotation = 0  # Current rotation for rendering
        self.death_animation = False  # Flag for death animation
        self.death_timer = 0  # Timer for death animation
        self.death_scale = 1.0  # Scale factor for explosion animation
        
        # Load sprites if not already loaded
        if UFO.ufo_sprite is None:
            UFO.ufo_sprite = pygame.image.load("assets/images/enemyUFO.png").convert_alpha()
        if UFO.enemy_ship_sprite is None:
            UFO.enemy_ship_sprite = pygame.image.load("assets/images/enemyShip.png").convert_alpha()
            
        # Select appropriate sprite based on type
        if is_ufo:
            self.sprite = pygame.transform.scale(UFO.ufo_sprite, (UFO_RADIUS * 2.2, UFO_RADIUS * 2))
        else:
            self.sprite = pygame.transform.scale(UFO.enemy_ship_sprite, (UFO_RADIUS * 2.2, UFO_RADIUS * 2))
        
        # Create engine glow effect
        self.glow_size = UFO_RADIUS * 0.8
        self.glow_intensity = 0
        self.glow_direction = 1  # 1 = increasing, -1 = decreasing
        
        # Random initial velocity
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * UFO_SPEED
        
        # Set initial rotation based on velocity for ship type
        if not is_ufo:  # Only for enemy ships, UFOs don't rotate with direction
            self.rotation = math.degrees(math.atan2(self.velocity.y, self.velocity.x)) + 90
    
    def _select_movement_pattern(self):
        """Select a movement pattern for the UFO"""
        patterns = [
            self._sine_wave_movement,
            self._zigzag_movement,
            self._circular_movement
        ]
        return random.choice(patterns)
    
    def _sine_wave_movement(self, dt):
        """Move in a sine wave pattern"""
        self.pattern_time += dt
        
        # Basic forward movement
        base_direction = pygame.Vector2(self.velocity.x, 0).normalize() * UFO_SPEED
        
        # Add sine wave to y component
        amplitude = 100
        frequency = 1.5
        y_offset = amplitude * math.sin(frequency * self.pattern_time)
        
        # Set new velocity
        self.velocity = pygame.Vector2(base_direction.x, y_offset * dt * 10)
    
    def _zigzag_movement(self, dt):
        """Move in a zigzag pattern"""
        self.pattern_time += dt
        
        # Change direction every 1 second
        if int(self.pattern_time) % 2 == 0:
            direction = 1
        else:
            direction = -1
        
        # Move at an angle
        angle = 30 * direction
        speed = UFO_SPEED
        self.velocity = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * speed
    
    def _circular_movement(self, dt):
        """Move in a circular pattern"""
        self.pattern_time += dt
        
        # Calculate position on circle
        radius = 150
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        
        # Circular motion
        angular_speed = 1.0  # radians per second
        angle = self.pattern_time * angular_speed
        
        # Target position on circle
        target_x = center_x + radius * math.cos(angle)
        target_y = center_y + radius * math.sin(angle)
        
        # Vector to target
        target = pygame.Vector2(target_x, target_y)
        direction = target - self.position
        
        if direction.length() > 0:
            direction = direction.normalize()
        
        # Set velocity
        self.velocity = direction * UFO_SPEED
    
    def draw(self, screen):
        """Draw the UFO or enemy ship with visual effects"""
        # If in death animation, draw explosion instead
        if self.death_animation:
            self._draw_death_animation(screen)
            return
            
        # Create a copy of the sprite for applying effects
        sprite_copy = self.sprite.copy()
        
        # Apply damage flash effect if recently hit
        if self.damaged and self.damage_flash_timer > 0:
            # Create white flash overlay that fades out
            flash_alpha = int(min(255, self.damage_flash_timer * 500))
            flash_overlay = pygame.Surface(sprite_copy.get_size(), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, flash_alpha))
            sprite_copy.blit(flash_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Rotate ship sprite based on movement direction (only for enemy ships)
        if not self.is_ufo:
            # Calculate rotation based on velocity direction
            if self.velocity.length() > 0:
                target_rotation = math.degrees(math.atan2(self.velocity.y, self.velocity.x)) + 90
                
                # Smooth rotation (lerp)
                angle_diff = (target_rotation - self.rotation + 180) % 360 - 180
                self.rotation += angle_diff * 0.1  # Adjust speed of rotation
                
            rotated_sprite = pygame.transform.rotate(sprite_copy, -self.rotation)
        else:
            # UFOs don't rotate with movement direction
            rotated_sprite = sprite_copy
            
        # Position sprite
        sprite_rect = rotated_sprite.get_rect(center=self.position)
        
        # Draw engine glow effect before the ship
        self._draw_engine_glow(screen)
        
        # Draw the UFO/ship sprite
        screen.blit(rotated_sprite, sprite_rect)
    
    def _draw_engine_glow(self, screen):
        """Draw engine glow effect behind the UFO/ship"""
        # Update glow intensity for pulsing effect
        self.glow_intensity += 0.05 * self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.4:
            self.glow_intensity = 0.4
            self.glow_direction = 1
            
        # Create engine glow surface
        glow_size = self.glow_size * (1.0 + 0.2 * self.glow_intensity)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Determine glow position based on ship type and rotation
        if self.is_ufo:
            # For UFO, engine glow at bottom
            glow_pos = pygame.Vector2(self.position.x, self.position.y + self.radius * 0.5)
            glow_color = (100, 100, 255, int(100 * self.glow_intensity))  # Blue glow
        else:
            # For ship, engine glow at back based on rotation
            angle_rad = math.radians(self.rotation - 180)  # Opposite of ship direction
            offset = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad)) * (self.radius * 0.8)
            glow_pos = self.position + offset
            glow_color = (255, 100, 50, int(120 * self.glow_intensity))  # Orange/red glow
            
        # Draw glow circle
        pygame.draw.circle(
            glow_surface, 
            glow_color,
            (glow_size, glow_size),
            glow_size
        )
        
        # Apply glow to screen
        glow_rect = glow_surface.get_rect(center=glow_pos)
        screen.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_RGBA_ADD)
        
    def _draw_death_animation(self, screen):
        """Draw death explosion animation"""
        # Increase explosion size
        self.death_scale += 0.2
        alpha = max(0, int(255 * (1.0 - self.death_timer / 0.8)))  # Fade out over time
        
        # Create explosion circles with different colors
        for i, color in enumerate([(255, 200, 50, alpha), (255, 100, 50, alpha), (200, 50, 50, alpha)]):
            size = self.radius * (self.death_scale - i * 0.3)
            if size <= 0:
                continue
                
            explosion_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surf, color, (size, size), size)
            explosion_rect = explosion_surf.get_rect(center=self.position)
            screen.blit(explosion_surf, explosion_rect)
    
    def update(self, dt):
        """Update UFO position and behavior"""
        # Handle death animation if active
        if self.death_animation:
            self.death_timer += dt
            if self.death_timer >= 0.8:  # Animation duration
                self.kill()  # Remove when animation completes
            return
        
        # Apply the current movement pattern
        self.movement_pattern(dt)
        
        # Update position
        self.position += self.velocity * dt
        
        # Wrap around screen edges
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius
            
        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius
        
        # Update timers
        self.shoot_timer -= dt
        
        # Update damage flash effect
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            if self.damage_flash_timer <= 0:
                self.damaged = False
    
    def shoot_at_player(self, player_position):
        """Shoot a projectile at the player"""
        if self.shoot_timer <= 0 and not self.death_animation:
            # Reset timer
            self.shoot_timer = UFO_SHOOT_COUNTDOWN
            
            # Calculate firing position based on ship type and rotation
            if self.is_ufo:
                # UFO fires from center bottom
                fire_pos = pygame.Vector2(self.position.x, self.position.y + self.radius * 0.3)
            else:
                # Ship fires from front based on rotation
                angle_rad = math.radians(self.rotation)
                offset = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad)) * (self.radius * 0.8)
                fire_pos = self.position + offset
            
            # Create projectile at firing position
            projectile = EnemyProjectile(fire_pos.x, fire_pos.y)
            
            # Calculate direction to player
            direction = player_position - self.position
            if direction.length() > 0:
                direction = direction.normalize()
            
            # Add some randomness to the aim
            inaccuracy = random.uniform(-0.2, 0.2)
            direction = direction.rotate(inaccuracy * 30)
            
            # Set projectile velocity
            projectile.velocity = direction * UFO_SHOOT_SPEED
            
            # Play sound effect
            if sound_manager:
                sound_manager.play_sound('ufo_shoot')
            
            # Add visual firing effect
            self._create_firing_effect(fire_pos, direction)
                
            return projectile
            
        return None
    
    def _create_firing_effect(self, position, direction):
        """Create visual effect when firing"""
        # Flash effect will be handled in the EnemyProjectile class
        pass
    
    def hit(self):
        """Handle getting hit by a player shot"""
        # Start damage flash effect
        self.damaged = True
        self.damage_flash_timer = 0.2  # Flash duration in seconds
        
        # Start death animation
        self.death_animation = True
        self.death_timer = 0
        
        # Stop movement
        self.velocity = pygame.Vector2(0, 0)
        
        # Play explosion sound
        if sound_manager:
            sound_manager.play_sound('explosion_large')
            
        return True

