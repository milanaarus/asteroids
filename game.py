"""Окно игры и основной игровой цикл."""

import pygame
from objects import Ship

from settings import BACKGROUND_COLOR, FPS, HEIGHT, WIDTH


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

    def run(self):
        """Обрабатывает события, движение и отрисовку."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.ship.update(keys, dt)

            self.screen.fill(BACKGROUND_COLOR)
            self.ship.draw(self.screen)
            pygame.display.flip()

        pygame.quit()