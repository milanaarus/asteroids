"""Классы игровых объектов."""

import pygame

from settings import (
    FLAME_COLOR,
    HEIGHT,
    SHIP_ACCELERATION,
    SHIP_COLOR,
    SHIP_DRAG,
    SHIP_ROTATION_SPEED,
    WIDTH,
    MISSILE_COLOR,
    MISSILE_LIFETIME,
    MISSILE_RADIUS,
    MISSILE_SPEED,
)


class SpaceObject:
    """Хранит положение и скорость объекта."""

    def __init__(self, position, velocity=(0, 0)):
        """Задаёт положение и скорость объекта."""
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)

    def move(self, dt):
        """Перемещает объект с переходом через границы окна."""
        self.position += self.velocity * dt
        self.position.x %= WIDTH
        self.position.y %= HEIGHT


class Ship(SpaceObject):
    """Представляет корабль игрока."""

    def __init__(self):
        """Размещает корабль в центре окна."""
        super().__init__((WIDTH / 2, HEIGHT / 2))
        self.angle = 0
        self.thrusting = False

    def update(self, keys, dt):
        """Обновляет поворот, скорость и положение корабля."""
        if keys[pygame.K_LEFT]:
            self.angle -= SHIP_ROTATION_SPEED * dt

        if keys[pygame.K_RIGHT]:
            self.angle += SHIP_ROTATION_SPEED * dt

        self.thrusting = keys[pygame.K_UP]

        if self.thrusting:
            direction = pygame.Vector2(1, 0).rotate(self.angle)
            self.velocity += direction * SHIP_ACCELERATION * dt
        else:
            self.velocity *= max(0, 1 - SHIP_DRAG * dt)

            if self.velocity.length() < 1:
                self.velocity.update(0, 0)

        self.move(dt)

    def draw(self, screen):
        """Рисует корабль и пламя при включённом двигателе."""
        if self.thrusting:
            flame_points = [
                pygame.Vector2(-15, -7),
                pygame.Vector2(-30, 0),
                pygame.Vector2(-15, 7),
            ]
            rotated_flame = [
                self.position + point.rotate(self.angle)
                for point in flame_points
            ]
            pygame.draw.polygon(screen, FLAME_COLOR, rotated_flame)

        points = [
            pygame.Vector2(20, 0),
            pygame.Vector2(-15, -12),
            pygame.Vector2(-15, 12),
        ]
        rotated_points = [
            self.position + point.rotate(self.angle)
            for point in points
        ]
        pygame.draw.polygon(screen, SHIP_COLOR, rotated_points, 2)


class Missile(SpaceObject):
    """Представляет ракету с ограниченным временем жизни."""

    def __init__(self, position, angle):
        """Создаёт ракету, летящую в заданном направлении."""
        direction = pygame.Vector2(1, 0).rotate(angle)
        super().__init__(position, direction * MISSILE_SPEED)
        self.time_left = MISSILE_LIFETIME

    def update(self, dt):
        """Перемещает ракету и уменьшает время её жизни."""
        self.move(dt)
        self.time_left -= dt

    def draw(self, screen):
        """Рисует ракету."""
        pygame.draw.circle(
            screen,
            MISSILE_COLOR,
            self.position,
            MISSILE_RADIUS,
        )