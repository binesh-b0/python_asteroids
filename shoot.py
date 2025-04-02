import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS

class Shoot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            center=[self.position.x,self.position.y],
            color=(225,225,0),
            radius=self.radius,
        )
    def update(self, dt):
        self.position += (self.velocity*dt)