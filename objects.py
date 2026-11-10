"""Классы игровых объектов."""

import random
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
    ASTEROID_COLOR,
    ASTEROID_MAX_SPEED,
    ASTEROID_MIN_SPEED,
    ASTEROID_RADIUS,
    ASTEROID_ROTATION_SPEED,
    EXPLOSION_COLOR,
    EXPLOSION_FRAMES,
    EXPLOSION_FRAME_TIME,
    EXPLOSION_SIZE,
    SHIP_RADIUS,
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

    def collides_with(self, other):
        """Проверяет столкновение с учётом перехода через края."""
        dx = (self.position.x - other.position.x + WIDTH / 2) % WIDTH
        dx -= WIDTH / 2

        dy = (self.position.y - other.position.y + HEIGHT / 2) % HEIGHT
        dy -= HEIGHT / 2

        distance_squared = dx * dx + dy * dy
        return distance_squared <= (self.radius + other.radius) ** 2


class Ship(SpaceObject):
    """Представляет корабль игрока."""

    def __init__(self):
        """Размещает корабль в центре окна."""
        super().__init__((WIDTH / 2, HEIGHT / 2))
        self.angle = 0
        self.thrusting = False
        self.radius = SHIP_RADIUS

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
        self.radius = MISSILE_RADIUS

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


class Asteroid(SpaceObject):
    """Представляет движущийся и вращающийся астероид."""

    def __init__(self):
        """Выбирает случайные положение и скорости астероида."""
        position = (
            random.uniform(0, WIDTH),
            random.uniform(0, HEIGHT),
        )
        direction = pygame.Vector2(1, 0).rotate(
            random.uniform(0, 360)
        )
        speed = random.uniform(
            ASTEROID_MIN_SPEED,
            ASTEROID_MAX_SPEED,
        )
        super().__init__(position, direction * speed)

        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(
            -ASTEROID_ROTATION_SPEED,
            ASTEROID_ROTATION_SPEED,
        )
        self.radius = ASTEROID_RADIUS

        # Разные расстояния от центра создают неровный контур.
        self.points = [
            pygame.Vector2(
                self.radius * random.uniform(0.7, 1.0), 0
            ).rotate(angle)
            for angle in range(0, 360, 45)
        ]

    def update(self, dt):
        """Обновляет положение и угол поворота астероида."""
        self.move(dt)
        self.angle += self.rotation_speed * dt

    def draw(self, screen):
        """Рисует повёрнутый контур астероида."""
        rotated_points = [
            self.position + point.rotate(self.angle)
            for point in self.points
        ]
        pygame.draw.polygon(
            screen, ASTEROID_COLOR, rotated_points, 2
        )


class Explosion:
    """Показывает взрыв, последовательно выбирая кадры изображения."""

    def __init__(self, position):
        """Создаёт ленту кадров и запоминает место взрыва."""
        self.position = pygame.Vector2(position)
        self.age = 0

        self.sheet = pygame.Surface(
            (EXPLOSION_SIZE * EXPLOSION_FRAMES, EXPLOSION_SIZE),
            pygame.SRCALPHA,
        )

        # Каждый кадр занимает отдельный квадрат в общей ленте.
        for frame in range(EXPLOSION_FRAMES):
            progress = (frame + 1) / EXPLOSION_FRAMES
            radius = int((EXPLOSION_SIZE / 2 - 2) * progress)
            alpha = int(255 * (1 - frame / EXPLOSION_FRAMES))

            center = (
                frame * EXPLOSION_SIZE + EXPLOSION_SIZE // 2,
                EXPLOSION_SIZE // 2,
            )
            pygame.draw.circle(
                self.sheet,
                (*EXPLOSION_COLOR, alpha),
                center,
                radius,
                3,
            )

    def update(self, dt):
        """Увеличивает время, прошедшее с начала взрыва."""
        self.age += dt

    def is_finished(self):
        """Возвращает True, когда показаны все кадры."""
        return self.age >= EXPLOSION_FRAMES * EXPLOSION_FRAME_TIME

    def draw(self, screen):
        """Выбирает текущий кадр из ленты и рисует его."""
        frame = int(self.age / EXPLOSION_FRAME_TIME)

        if frame >= EXPLOSION_FRAMES:
            return

        area = pygame.Rect(
            frame * EXPLOSION_SIZE,
            0,
            EXPLOSION_SIZE,
            EXPLOSION_SIZE,
        )
        position = self.position - pygame.Vector2(
            EXPLOSION_SIZE / 2,
            EXPLOSION_SIZE / 2,
        )
        screen.blit(self.sheet, position, area)
