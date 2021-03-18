from typing import List, Tuple
import pygame
from pygame import Vector2, gfxdraw
from random import random
from math import sqrt, sin, cos, pi
from __future__ import annotations

Color = Tuple[int, int, int]


SC_WIDTH = 600
SC_HEIGHT = 600
SC_SIZE = (SC_WIDTH, SC_HEIGHT)
pygame.init()
screen = pygame.display.set_mode(SC_SIZE)
clock = pygame.time.Clock()


class Ball:
    def __init__(self, r: Vector2, v: Vector2, mass: float, radius: float, color: Color) -> None:
        self.r = r
        self.v = v
        self.mass = mass
        self.radius = radius
        self.color = color
    
    @property
    def x(self) -> float:
        return self.r.x
    
    @property
    def y(self) -> float:
        return self.r.y
    
    def overlaps(self, other: Ball) -> bool:
        return (self.r - other.r).magnitude_squared() < (self.radius + other.radius)**2
    
    def draw(self) -> None:
        gfxdraw.aacircle(screen, int(self.x*SC_WIDTH), int((1-self.y)*SC_HEIGHT), int(self.radius*SC_WIDTH), self.color)
        gfxdraw.filled_circle(screen, int(self.x*SC_WIDTH), int((1-self.y)*SC_HEIGHT), int(self.radius*SC_WIDTH), self.color)


class Physics:
    def __init__(self, balls: List[Ball]) -> None:
        self.balls = balls

    def update_pos(self, dt: float) -> None:
        for ball in self.balls:
            ball.r = ball.r + dt*ball.v

    def fix_overlap(self, b1: Ball, b2: Ball) -> None:
        r12 = b1.r - b2.r
        v12 = b1.v - b2.v
        a = v12.dot(v12)
        b = -2*v12.dot(r12)
        c = r12.dot(r12) - (b1.radius + b2.radius)**2
        if a != 0:
            alpha = (-b + sqrt(b**2 - 4*a*c))/(2*a)
            b1.r = b1.r - alpha*b1.v
            b2.r = b2.r - alpha*b2.v

    def ball_collision(self, b1: Ball, b2: Ball) -> None:
        self.fix_overlap(b1, b2)
        m1, m2 = b1.mass, b2.mass
        M = m1 + m2
        r1, r2 = b1.r, b2.r
        d = (r1 - r2).magnitude_squared()
        v1, v2 = b1.v, b2.v
        dv = 2 / M * (v1-v2).dot(r1-r2) / d * (r1 - r2)
        b1.v = v1 - m2 * dv
        b2.v = v2 + m1 * dv

    def handle_overlap(self) -> None:
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                if i != j:
                    b1, b2 = self.balls[i], self.balls[j]
                    if b1.overlaps(b2):
                        self.ball_collision(b1, b2)

    def handle_wall_collision(self) -> None:
        for b in self.balls:
            if b.x - b.radius < 0:
                b.r.x = b.radius
                b.v.x = -b.v.x
            elif b.x + b.radius > 1:
                b.r.x = 1 - b.radius
                b.v.x = -b.v.x
            if b.y - b.radius < 0:
                b.r.y = b.radius
                b.v.y = -b.v.y
            elif b.y + b.radius > 1:
                b.r.y = 1 - b.radius
                b.v.y = -b.v.y

    def update(self, dt: float) -> None:
        self.update_pos(dt)
        self.handle_wall_collision()
        self.handle_overlap()


def generate_balls(number: int) -> List[Ball]:
    balls: List[Ball] = []
    for _ in range(number):
        r = Vector2(random(), random())
        rand = random()*2*pi - pi
        vec = Vector2(cos(rand), sin(rand)).normalize()*0.3
        m = random()*0.5 + 0.5
        radius = random()*0.05 + 0.025
        color = tuple([200 - int(((m-0.5)/0.5)*200) for _ in range(3)])
        balls.append(Ball(r, vec, m, radius, color))
    return balls


balls = generate_balls(13)
physics = Physics(balls)

playing = True
while playing:
    clock.tick(120)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
            
    screen.fill((255,255,255))

    physics.update(1/120)

    for ball in balls:
        ball.draw()

    pygame.display.update()

pygame.quit()