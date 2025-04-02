import pygame
import random
from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS,ASTEROID_MAX_RADIUS
class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            color=(225,225,225),
            center=[self.position.x,self.position.y],
            radius=self.radius,width=2
            )
    def update(self, dt):
        self.position += (self.velocity * dt)

    def split(self):
        self.kill()
        if self.radius < ASTEROID_MIN_RADIUS:
            return
        angle = random.uniform(20,50)
        v1 = self.velocity.rotate(angle) * 1.2
        v2 = self.velocity.rotate(-angle)
        a1 =Asteroid(self.position.x,self.position.y,self.radius-ASTEROID_MIN_RADIUS)
        a1.velocity =v1
        a2 = Asteroid(self.position.x,self.position.y,self.radius-ASTEROID_MIN_RADIUS)
        a2.velocity = v2