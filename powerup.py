import pygame
import random
import math
from circleshape import CircleShape
from constants import *

# Import sound to avoid circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class PowerUp(CircleShape):
    def __init__(self, x, y, powerup_type=None):
        super().__init__(x, y, POWERUP_RADIUS)
        
        # Randomly select power-up type if not specified
        if powerup_type is None:
            self.powerup_type = random.choice([POWERUP_AMMO, POWERUP_FIRE_RATE, POWERUP_SCORE, POWERUP_INVINCIBILITY])
        else:
            self.powerup_type = powerup_type
            
        # Set up movement pattern - slow drifting in a random direction
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * POWERUP_DRIFT_SPEED
        
        # Timer for despawning
        self.lifetime = POWERUP_LIFETIME
        
        # Animation variables
        self.pulse_time = 0
        self.pulse_rate = 2.0  # Pulse rate in seconds
        
    def update(self, dt):
        # Update position based on velocity
        self.position += self.velocity * dt
        
        # Bounce off screen edges
        if self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x = -self.velocity.x
        elif self.position.x > SCREEN_WIDTH - self.radius:
            self.position.x = SCREEN_WIDTH - self.radius
            self.velocity.x = -self.velocity.x
            
        if self.position.y < self.radius:
            self.position.y = self.radius
            self.velocity.y = -self.velocity.y
        elif self.position.y > SCREEN_HEIGHT - self.radius:
            self.position.y = SCREEN_HEIGHT - self.radius
            self.velocity.y = -self.velocity.y
        
        # Update pulse animation
        self.pulse_time += dt
        if self.pulse_time > self.pulse_rate:
            self.pulse_time -= self.pulse_rate
        
        # Update lifetime and check for expiration
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, screen):
        # Calculate pulse effect (0.8 to 1.2 size)
        pulse_factor = 0.8 + 0.4 * (math.sin(self.pulse_time / self.pulse_rate * 2 * math.pi) * 0.5 + 0.5)
        display_radius = self.radius * pulse_factor
        
        # Determine power-up color and appearance based on type
        if self.powerup_type == POWERUP_AMMO:
            # Ammo power-up - green with bullet-like symbol
            color = (0, 200, 0)  # Green
            pygame.draw.circle(screen, color, [self.position.x, self.position.y], display_radius, 2)
            # Draw bullet symbol
            pygame.draw.line(screen, color, 
                            [self.position.x - display_radius/2, self.position.y],
                            [self.position.x + display_radius/2, self.position.y], 2)
            
        elif self.powerup_type == POWERUP_FIRE_RATE:
            # Fire rate power-up - yellow with lightning bolt
            color = (255, 215, 0)  # Gold
            pygame.draw.circle(screen, color, [self.position.x, self.position.y], display_radius, 2)
            # Draw lightning bolt symbol
            points = [
                [self.position.x, self.position.y - display_radius/2],
                [self.position.x - display_radius/3, self.position.y],
                [self.position.x, self.position.y],
                [self.position.x + display_radius/3, self.position.y + display_radius/2]
            ]
            pygame.draw.lines(screen, color, False, points, 2)
            
        elif self.powerup_type == POWERUP_SCORE:
            # Score power-up - purple with $ symbol
            color = (200, 0, 200)  # Purple
            pygame.draw.circle(screen, color, [self.position.x, self.position.y], display_radius, 2)
            # Draw $ symbol
            font = pygame.font.SysFont(None, int(display_radius * 1.5))
            text = font.render("$", True, color)
            screen.blit(text, [self.position.x - text.get_width()/2, self.position.y - text.get_height()/2])
            
        elif self.powerup_type == POWERUP_INVINCIBILITY:
            # Invincibility power-up - blue with shield symbol
            color = (0, 100, 255)  # Blue
            pygame.draw.circle(screen, color, [self.position.x, self.position.y], display_radius, 2)
            # Draw shield symbol - arc
            pygame.draw.arc(screen, color,
                           [self.position.x - display_radius/2, self.position.y - display_radius/2,
                            display_radius, display_radius],
                           0, math.pi, 2)
        
        # If power-up is about to expire (less than 3 seconds), make it flash
        if self.lifetime < 3.0 and int(self.lifetime * 5) % 2 == 0:
            pygame.draw.circle(screen, (255, 255, 255), [self.position.x, self.position.y], display_radius, 1)

    def apply_effect(self, player):
        """Apply the power-up effect to the player"""
        if self.powerup_type == POWERUP_AMMO:
            # Add ammo
            player.current_ammo = min(player.current_ammo + POWERUP_AMMO_AMOUNT, AMMO_MAX_SHOTS)
            if sound_manager:
                sound_manager.play_sound('powerup_ammo') if hasattr(sound_manager, 'play_sound') else None
                
        elif self.powerup_type == POWERUP_FIRE_RATE:
            # Faster firing rate for a duration
            player.active_powerups[POWERUP_FIRE_RATE] = POWERUP_FIRE_RATE_DURATION
            if sound_manager:
                sound_manager.play_sound('powerup_fire_rate') if hasattr(sound_manager, 'play_sound') else None
                
        elif self.powerup_type == POWERUP_SCORE:
            # Add score bonus
            player.add_score(POWERUP_SCORE_AMOUNT)
            if sound_manager:
                sound_manager.play_sound('powerup_score') if hasattr(sound_manager, 'play_sound') else None
                
        elif self.powerup_type == POWERUP_INVINCIBILITY:
            # Add temporary invincibility
            player.active_powerups[POWERUP_INVINCIBILITY] = POWERUP_INVINCIBILITY_DURATION
            if sound_manager:
                sound_manager.play_sound('powerup_invincibility') if hasattr(sound_manager, 'play_sound') else None

