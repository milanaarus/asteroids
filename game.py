"""Окно игры и основной игровой цикл."""

import pygame
from objects import Asteroid, Explosion, Missile, Ship

from settings import (
    BACKGROUND_COLOR,
    FPS,
    HEIGHT,
    SHIP_NOSE_OFFSET,
    WIDTH,
    ASTEROID_INTERVAL,
    FONT_SIZE,
    HUD_MARGIN,
    TEXT_COLOR,
    INITIAL_LIVES,
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
        self.asteroids = []
        self.asteroid_timer = 0
        self.score = 0
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.explosions = []
        self.lives = INITIAL_LIVES

    def check_missile_collisions(self):
        """Удаляет столкнувшиеся ракету и астероид, начисляет очко."""
        for missile in self.missiles[:]:
            for asteroid in self.asteroids[:]:
                if missile.collides_with(asteroid):
                    self.explosions.append(
                        Explosion(asteroid.position)
                    )
                    self.missiles.remove(missile)
                    self.asteroids.remove(asteroid)
                    self.score += 1
                    break

    def check_ship_collisions(self):
        """Обрабатывает столкновение корабля с астероидом."""
        for asteroid in self.asteroids[:]:
            if self.ship.collides_with(asteroid):
                self.explosions.append(
                    Explosion(asteroid.position)
                )
                self.asteroids.remove(asteroid)
                self.ship = Ship()
                self.lives -= 1
                break

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
            self.asteroid_timer += dt

            if self.asteroid_timer >= ASTEROID_INTERVAL:
                self.asteroid_timer -= ASTEROID_INTERVAL
                self.asteroids.append(Asteroid())

            for asteroid in self.asteroids:
                asteroid.update(dt)

            for missile in self.missiles:
                missile.update(dt)

            self.missiles = [
                missile
                for missile in self.missiles
                if missile.time_left > 0
            ]

            self.screen.fill(BACKGROUND_COLOR)
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            self.check_missile_collisions()
            if self.lives > 0:
                self.check_ship_collisions()
            for explosion in self.explosions:
                explosion.update(dt)

            self.explosions = [
                explosion
                for explosion in self.explosions
                if not explosion.is_finished()
            ]
            self.ship.draw(self.screen)

            for missile in self.missiles:
                missile.draw(self.screen)

            for explosion in self.explosions:
                explosion.draw(self.screen)

            score_text = self.font.render(
                f"Очки: {self.score}", True, TEXT_COLOR
            )
            self.screen.blit(score_text, (HUD_MARGIN, HUD_MARGIN))
            lives_text = self.font.render(
                f"Жизни: {self.lives}", True, TEXT_COLOR
            )
            lives_position = (
                WIDTH - lives_text.get_width() - HUD_MARGIN,
                HUD_MARGIN,
            )
            self.screen.blit(lives_text, lives_position)
            pygame.display.flip()

        pygame.quit()
