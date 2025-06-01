import pygame
from circleshape import CircleShape
from constants import ENEMY_SHOT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT

class EnemyProjectile(CircleShape):
    """Projectile fired by enemies"""
    
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_SHOT_RADIUS)
    
    def draw(self, screen):
        """Draw the enemy projectile with a red color"""
        pygame.draw.circle(
            screen,
            center=[self.position.x, self.position.y],
            color=(255, 50, 50),  # Red color
            radius=self.radius,
        )
    
    def update(self, dt):
        """Update the projectile position"""
        self.position += (self.velocity * dt)
        
        # Remove if off-screen
        if (self.position.x < -self.radius or 
            self.position.x > SCREEN_WIDTH + self.radius or
            self.position.y < -self.radius or
            self.position.y > SCREEN_HEIGHT + self.radius):
            self.kill()

