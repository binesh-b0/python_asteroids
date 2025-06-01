import pygame
import math
from circleshape import CircleShape
from constants import ENEMY_SHOT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT

class EnemyProjectile(CircleShape):
    """Projectile fired by enemies"""
    # Class sprite variables
    laser_sprite = None
    
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_SHOT_RADIUS)
        
        # Load laser sprite if not already loaded
        if EnemyProjectile.laser_sprite is None:
            EnemyProjectile.laser_sprite = pygame.image.load("assets/images/laserRed.png").convert_alpha()

        orig_width, orig_height = EnemyProjectile.laser_sprite.get_size()
        aspect_ratio = orig_width / orig_height
              
        # Scale sprite to match the shot size
        self.sprite_width = ENEMY_SHOT_RADIUS 
        self.sprite_height =int(self.sprite_width / aspect_ratio)
        self.sprite = pygame.transform.scale(EnemyProjectile.laser_sprite, 
                                           (self.sprite_width, self.sprite_height))
        
        # Track rotation for proper rendering
        self.rotation = 0
        
        # Shot creation effect timer
        self.creation_effect = True
        self.effect_timer = 0.1  # Effect duration in seconds
        
    def draw(self, screen):
        """Draw the enemy projectile with sprite and effects"""
        # Calculate rotation based on velocity direction
        if self.velocity.length() > 0:
            # Get angle in degrees, adjusted for pygame's coordinate system
            self.rotation = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            
        # Rotate the sprite to match the direction of travel
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.rotation + 90)  # +90 to align properly
        sprite_rect = rotated_sprite.get_rect(center=self.position)
        
        # Draw the laser sprite
        screen.blit(rotated_sprite, sprite_rect)
        
        # Add firing effect when shot is first created
        if self.creation_effect:
            # Create a bright flash at the center
            flash_size = self.radius * 4
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            flash_alpha = int(255 * (self.effect_timer / 0.1))  # Fade out over effect duration
            pygame.draw.circle(flash_surf, (255, 100, 100, flash_alpha), 
                             (flash_size, flash_size), flash_size)
            flash_rect = flash_surf.get_rect(center=self.position)
            screen.blit(flash_surf, flash_rect, special_flags=pygame.BLEND_RGBA_ADD)
        
        # # Add a subtle glow effect
        # glow_color = (255, 50, 50, 100)  # Red glow
        # glow_surf = pygame.Surface((ENEMY_SHOT_RADIUS * 4, ENEMY_SHOT_RADIUS * 4), pygame.SRCALPHA)
        # pygame.draw.circle(glow_surf, glow_color, 
        #                  (ENEMY_SHOT_RADIUS * 2, ENEMY_SHOT_RADIUS * 2), ENEMY_SHOT_RADIUS * 1.5)
        # glow_rect = glow_surf.get_rect(center=self.position)
        # screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_RGBA_ADD)
    
    def update(self, dt):
        """Update the projectile position and effects"""
        self.position += (self.velocity * dt)
        
        # Update firing effect
        if self.creation_effect:
            self.effect_timer -= dt
            if self.effect_timer <= 0:
                self.creation_effect = False
        
        # Remove if off-screen
        if (self.position.x < -self.radius or 
            self.position.x > SCREEN_WIDTH + self.radius or
            self.position.y < -self.radius or
            self.position.y > SCREEN_HEIGHT + self.radius):
            self.kill()

