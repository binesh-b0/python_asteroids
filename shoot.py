import pygame # type: ignore
import math
import random
from circleshape import CircleShape
from constants import SHOT_RADIUS
from effects import EffectManager

# Global effect manager
effect_manager = None

class Shoot(CircleShape):
    # Class sprite variables
    laser_green_sprite = None
    laser_red_sprite = None
    
    @classmethod
    def init_sprites(cls):
        """Initialize all sprites used by bullets"""
        if cls.laser_green_sprite is None:
            cls.laser_green_sprite = pygame.image.load("assets/images/laserGreen.png").convert_alpha()
        if cls.laser_red_sprite is None:
            cls.laser_red_sprite = pygame.image.load("assets/images/laserRed.png").convert_alpha()

    def __init__(self, x, y, is_player=True):
        super().__init__(x, y, SHOT_RADIUS)
        
        # Create effect manager if not already created
        global effect_manager
        if effect_manager is None:
            effect_manager = EffectManager()
            
        # Initialize sprites if needed
        Shoot.init_sprites()
        
        # Select appropriate sprite based on type
        self.is_player = is_player
        if is_player:
            self.sprite = Shoot.laser_green_sprite
            self.glow_color = (0, 255, 0, 100)  # Green glow
        else:
            self.sprite = Shoot.laser_red_sprite
            self.glow_color = (255, 0, 0, 100)  # Red glow
            
        # Get original dimensions to maintain aspect ratio
        orig_width, orig_height = self.sprite.get_size()
        aspect_ratio = orig_width / orig_height
        
        # Scale sprite to match shot size while maintaining aspect ratio
        # Make bullet length based on radius, but keep proper width based on aspect ratio
        self.sprite_length = SHOT_RADIUS
        self.sprite_width = int(self.sprite_length / aspect_ratio)
        self.sprite = pygame.transform.scale(self.sprite, (self.sprite_width, self.sprite_length))
        self.sprite = pygame.transform.rotate(self.sprite, 90)  # Rotate to match direction
        
        # Add firing effect at creation point
        effect_manager.add_particle_system(
            (x, y),
            effect_type="sparkle",
            colors=[(0, 255, 0, 200)] if is_player else [(255, 0, 0, 200)],
            particle_count=8,
            duration=0.3
        )
        
        # Track rotation for proper rendering
        self.rotation = 0
        
    def draw(self, screen):
        # Calculate rotation based on velocity direction
        if self.velocity.length() > 0:
            # Get angle in degrees, adjusted for pygame's coordinate system
            self.rotation = math.degrees(math.atan2(self.velocity.y, self.velocity.x))
            
        # Rotate the sprite to match the direction of travel
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.rotation + 90)  # +90 to align properly
        sprite_rect = rotated_sprite.get_rect(center=self.position)
        
        # Draw small trailing particles occasionally
        if random.random() < 0.3:  # 30% chance each frame
            # Calculate position slightly behind the laser
            trail_angle = math.radians(self.rotation - 90)  # Convert to radians and adjust for direction
            trail_offset = pygame.Vector2(math.cos(trail_angle), math.sin(trail_angle)) * (self.sprite_length / 2)
            trail_pos = self.position - trail_offset
            

        
        # Draw the laser sprite
        screen.blit(rotated_sprite, sprite_rect)
        
        
    def update(self, dt):
        """Update bullet position and effects"""
        self.position += (self.velocity * dt)
        
    def kill(self):
        """Handle bullet destruction with effects"""
        # Add a small particle burst when the bullet is destroyed
        effect_manager.add_particle_system(
            self.position,
            effect_type="sparkle",
            colors=[(0, 255, 0, 150)] if self.is_player else [(255, 0, 0, 150)],
            particle_count=5,
            duration=0.3,
            size_range=(1, 3)
        )
        
        # Call the parent kill method
        super().kill()
