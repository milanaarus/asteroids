"""Окно игры и основной игровой цикл."""

import pygame
from objects import Missile, Ship

from settings import (
    BACKGROUND_COLOR,
    FPS,
    HEIGHT,
    SHIP_NOSE_OFFSET,
    WIDTH,
)


class Game:
    """Управляет окном и игровым циклом."""

    def __init__(self):
        """Создаёт окно и часы для ограничения частоты кадров."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Астероиды")
        self.clock = pygame.time.Clock()
        self.running = True
        self.ship = Ship()
        self.missiles = []

    def run(self):
        """Обрабатывает события, движение и отрисовку."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        direction = pygame.Vector2(1, 0).rotate(
                            self.ship.angle
                        )
                        nose = (
                            self.ship.position
                            + direction * SHIP_NOSE_OFFSET
                        )
                        self.missiles.append(
                            Missile(nose, self.ship.angle)
                        )

            keys = pygame.key.get_pressed()
            self.ship.update(keys, dt)

            for missile in self.missiles:
                missile.update(dt)

            self.missiles = [
                missile
                for missile in self.missiles
                if missile.time_left > 0
            ]

            self.screen.fill(BACKGROUND_COLOR)
            self.ship.draw(self.screen)

            for missile in self.missiles:
                missile.draw(self.screen)

            pygame.display.flip()

        pygame.quit()