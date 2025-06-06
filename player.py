import pygame
import math
from circleshape import CircleShape
from constants import *
from shoot import Shoot

# Import sound here to avoid circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

class Player(CircleShape):
    timer = 0
    def __init__(self, x, y):
        super().__init__(x,y,PLAYER_RADIUS)
        self.health = PLAYER_MAX_HEALTH
        self.regen = PLAYER_HEALTH_REGEN_RATE
        self.rotation = 0
        self.score = 0
        self.thrust_playing = False  # Track if thrust sound is currently playing
        self.current_ammo = AMMO_INITIAL
        self.ammo_recharge_timer = 0
        self.active_powerups = {}  # Dictionary to track active power-ups and their remaining duration
        self.is_invincible = False  # Track invincibility state
        
        # Lives system
        self.lives = PLAYER_INITIAL_LIVES
        self.is_respawning = False
        self.respawn_timer = 0
        self.spawn_invulnerability_timer = 0
        self.initial_position = pygame.Vector2(x, y)  # Store initial position for respawning
        
        # Load player sprites
        self.sprite_normal = pygame.image.load("assets/images/player.png").convert_alpha()
        self.sprite_left = pygame.image.load("assets/images/playerLeft.png").convert_alpha()
        self.sprite_right = pygame.image.load("assets/images/playerRight.png").convert_alpha()
        self.sprite_damaged = pygame.image.load("assets/images/playerDamaged.png").convert_alpha()
        self.shield_sprite = pygame.image.load("assets/images/shield.png").convert_alpha()
        
        # Scale sprites to match player radius
        self.sprite_size = PLAYER_RADIUS * 2  # Diameter
        self.sprite_normal = pygame.transform.scale(self.sprite_normal, (self.sprite_size, self.sprite_size))
        self.sprite_left = pygame.transform.scale(self.sprite_left, (self.sprite_size, self.sprite_size))
        self.sprite_right = pygame.transform.scale(self.sprite_right, (self.sprite_size, self.sprite_size))
        self.sprite_damaged = pygame.transform.scale(self.sprite_damaged, (self.sprite_size, self.sprite_size))
        self.shield_sprite = pygame.transform.scale(self.shield_sprite, (self.sprite_size * 1.5, self.sprite_size * 1.5))
        
        # Track turning state for sprite selection
        self.turning_left = False
        self.turning_right = False
        self.current_sprite = self.sprite_normal

    def triangle(self):
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        # Don't draw anything if respawning
        if self.is_respawning:
            return
            
        # Select appropriate sprite based on turning state
        if self.turning_left:
            current_sprite = self.sprite_left
        elif self.turning_right:
            current_sprite = self.sprite_right
        else:
            current_sprite = self.sprite_normal
            
        # Make the sprite flash blue when invincible
        is_flashing = (self.is_invincible or self.spawn_invulnerability_timer > 0) and int(pygame.time.get_ticks() / 100) % 2 == 0
        
        # Rotate the sprite to match player rotation
        rotated_sprite = pygame.transform.rotate(current_sprite, -self.rotation)  # Negative because pygame rotates clockwise
        sprite_rect = rotated_sprite.get_rect(center=self.position)
        
        # Apply blue tint for invincibility if flashing
        if is_flashing:
            # Create a blue overlay on the sprite
            blue_overlay = pygame.Surface(rotated_sprite.get_size(), pygame.SRCALPHA)
            blue_overlay.fill((0, 100, 255, 128))  # Semi-transparent blue
            rotated_sprite.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
        # Draw the player sprite
        screen.blit(rotated_sprite, sprite_rect)
        
        # Draw shield sprite if invincible
        if self.is_invincible or self.spawn_invulnerability_timer > 0:
            rotated_shield = pygame.transform.rotate(self.shield_sprite, -self.rotation)
            shield_rect = rotated_shield.get_rect(center=self.position)
            screen.blit(rotated_shield, shield_rect)
        
        # Draw visual indicators for active power-ups
        if POWERUP_FIRE_RATE in self.active_powerups:
            # Draw fire rate indicator - small yellow circles around the ship
            angle_step = 2 * math.pi / 8
            radius = self.radius * 1.5
            for i in range(8):
                angle = i * angle_step
                x = self.position.x + radius * math.cos(angle)
                y = self.position.y + radius * math.sin(angle)
                pygame.draw.circle(screen, (255, 215, 0), (x, y), 3)

    def rotate(self, dt, direction=1):
        """
        Rotate the ship by the given amount.
        direction: 1 for counterclockwise (left), -1 for clockwise (right)
        """
        self.rotation += PLAYER_TURN_SPEED * dt * direction

    def update(self, dt):
        Player.timer -= dt
        
        # Handle respawn and invulnerability timers
        self.update_respawn_state(dt)
        
        # Skip movement controls if respawning
        if self.is_respawning:
            return
            
        keys = pygame.key.get_pressed()

        # Check if movement keys are pressed
        is_moving = keys[pygame.K_w] or keys[pygame.K_s]
        
        # Handle thrust sound
        if is_moving and not self.thrust_playing and sound_manager:
            sound_manager.play_thrust_sound()
            self.thrust_playing = True
        elif not is_moving and self.thrust_playing:
            self.thrust_playing = False

        # Handle ammo recharge
        if self.current_ammo < AMMO_MAX_SHOTS:
            self.ammo_recharge_timer += dt
            if self.ammo_recharge_timer >= AMMO_RECHARGE_RATE:
                self.ammo_recharge_timer = 0
                self.current_ammo = min(self.current_ammo + AMMO_RECHARGE_AMOUNT, AMMO_MAX_SHOTS)
        
        # Update power-up durations
        self.update_powerups(dt)

        # Update turning state for sprite selection
        self.turning_left = keys[pygame.K_a]
        self.turning_right = keys[pygame.K_d]
        
        if self.turning_left:
            self.rotate(dt, -1)  # Rotate counterclockwise (left)
        if self.turning_right:
            self.rotate(dt, 1)  # Rotate clockwise (right)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()

    def move(self,dt):
        forward = pygame.Vector2(0, -1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt

    def shoot(self):
        # Apply fire rate power-up if active
        cooldown = PLAYER_SHOT_COUNTDOWN
        if POWERUP_FIRE_RATE in self.active_powerups:
            cooldown *= POWERUP_FIRE_RATE_MULTIPLIER  # Faster firing rate
            
        if Player.timer > 0:
            return
        # Check if player has ammo
        if self.current_ammo <= 0:
            # Play empty ammo sound if available
            if sound_manager:
                sound_manager.play_sound('empty') if hasattr(sound_manager, 'play_sound') else None
            return
        
        # Consume ammo
        self.current_ammo -= 1
        
        Player.timer = cooldown
        shot = Shoot(self.position.x,self.position.y)
        shot.velocity = pygame.Vector2(0,-1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        
        # Play shooting sound 
        if sound_manager:
            sound_manager.play_sound('shoot') if hasattr(sound_manager, 'play_sound') else None

    def add_score(self, points):
        """Add points to the player's score"""
        self.score += points
        return self.score
    
    def update_powerups(self, dt):
        """Update active power-ups and their durations"""
        # Create a list of power-ups to remove (can't modify dict during iteration)
        to_remove = []
        
        # Update each power-up duration
        for powerup_type, duration in self.active_powerups.items():
            # Reduce duration by elapsed time
            self.active_powerups[powerup_type] -= dt
            
            # If power-up has expired, add to removal list
            if self.active_powerups[powerup_type] <= 0:
                to_remove.append(powerup_type)
        
        # Remove expired power-ups
        for powerup_type in to_remove:
            del self.active_powerups[powerup_type]
            
            # Handle special cleanup for certain power-ups
            if powerup_type == POWERUP_INVINCIBILITY:
                # Turn off invincibility when power-up expires
                self.is_invincible = False
                if sound_manager:
                    sound_manager.play_sound('shield_down') if hasattr(sound_manager, 'play_sound') else None
        
        # Update invincibility state based on power-up
        self.is_invincible = POWERUP_INVINCIBILITY in self.active_powerups
    
    def is_vulnerable(self):
        """Return True if player can be damaged (not invincible and not respawning)"""
        return not (self.is_invincible or self.is_respawning or self.spawn_invulnerability_timer > 0)
    
    def lose_life(self):
        """Handle player losing a life"""
        if self.lives > 0:
            self.lives -= 1
            
            # If we still have lives left, start respawn sequence
            if self.lives > 0:
                self.is_respawning = True
                self.respawn_timer = PLAYER_RESPAWN_TIME
                # Play death sound
                if sound_manager:
                    sound_manager.play_sound('player_death')
                return False  # Game not over
            return True  # Game over
        return True  # Game over
    
    def respawn(self):
        """Reset player for respawn"""
        # Reset position to center
        self.position = pygame.Vector2(self.initial_position)
        # Reset velocity
        self.velocity = pygame.Vector2(0, 0)
        # Reset rotation
        self.rotation = 0
        # Start invulnerability timer
        self.spawn_invulnerability_timer = PLAYER_SPAWN_INVULNERABILITY_TIME
        # Reset is_respawning flag
        self.is_respawning = False
        # Reset ammo
        self.current_ammo = AMMO_INITIAL
        
    def update_respawn_state(self, dt):
        """Update respawn and invulnerability timers"""
        # Update respawn timer if respawning
        if self.is_respawning:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn()
        
        # Update spawn invulnerability timer
        if self.spawn_invulnerability_timer > 0:
            self.spawn_invulnerability_timer -= dt
