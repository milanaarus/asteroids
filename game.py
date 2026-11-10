"""Окно игры и основной игровой цикл."""

import pygame

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

    def run(self):
        """Обрабатывает события и обновляет изображение."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(BACKGROUND_COLOR)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()