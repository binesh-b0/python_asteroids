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
    
    def __init__(self, x, y):
        super().__init__(x, y, UFO_RADIUS)
        self.shoot_timer = 0
        self.score_value = UFO_SCORE
        self.target = None  # Player target
        self.movement_pattern = self._select_movement_pattern()
        self.pattern_time = 0
        
        # Random initial velocity
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(math.cos(math.radians(angle)), math.sin(math.radians(angle))) * UFO_SPEED
    
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
        """Draw the UFO with its distinctive shape"""
        # Draw the main body of the UFO (ellipse)
        ellipse_rect = pygame.Rect(
            self.position.x - self.radius, 
            self.position.y - self.radius / 2,
            self.radius * 2, 
            self.radius
        )
        pygame.draw.ellipse(screen, (200, 200, 200), ellipse_rect, 2)
        
        # Draw the cockpit (top dome)
        cockpit_radius = self.radius / 2
        pygame.draw.arc(
            screen,
            (200, 200, 200),
            (self.position.x - cockpit_radius, self.position.y - self.radius - cockpit_radius / 2, cockpit_radius * 2, cockpit_radius * 2),
            math.pi, 2 * math.pi,
            2
        )
        
        # Draw lights around the UFO
        num_lights = 6
        light_radius = 3
        for i in range(num_lights):
            angle = 2 * math.pi * i / num_lights
            light_x = self.position.x + (self.radius - 5) * math.cos(angle)
            light_y = self.position.y + (self.radius / 2 - 2) * math.sin(angle)
            
            # Blink the lights randomly
            if random.random() > 0.7:
                light_color = (255, 255, 0)  # Yellow
            else:
                light_color = (200, 0, 0)  # Red
                
            pygame.draw.circle(screen, light_color, (light_x, light_y), light_radius)
    
    def update(self, dt):
        """Update UFO position and behavior"""
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
        
        # Update shooting timer
        self.shoot_timer -= dt
    
    def shoot_at_player(self, player_position):
        """Shoot a projectile at the player"""
        if self.shoot_timer <= 0:
            # Reset timer
            self.shoot_timer = UFO_SHOOT_COUNTDOWN
            
            # Create projectile aimed at player
            projectile = EnemyProjectile(self.position.x, self.position.y)
            
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
                
            return projectile
            
        return None

