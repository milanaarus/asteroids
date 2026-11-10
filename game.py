"""Окно игры и основной игровой цикл."""

import random
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
    SPLASH_COLOR,
    SPLASH_HEIGHT,
    SPLASH_WIDTH,
    BACKGROUND_ASTEROID_COLOR,
    BACKGROUND_ASTEROID_COUNT,
    BACKGROUND_ASTEROID_MAX_RADIUS,
    BACKGROUND_ASTEROID_MIN_RADIUS,
    BACKGROUND_SPEED,
    STAR_COLOR,
    STAR_COUNT,
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
        self.playing = False
        self.splash_rect = pygame.Rect(
            0, 0, SPLASH_WIDTH, SPLASH_HEIGHT
        )
        self.splash_rect.center = (WIDTH // 2, HEIGHT // 2)
        self.background_offset = 0
        self.create_background()

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
        """Обрабатывает потерю жизни или завершение игры."""
        for asteroid in self.asteroids[:]:
            if self.ship.collides_with(asteroid):
                self.explosions.append(
                    Explosion(asteroid.position)
                )
                self.asteroids.remove(asteroid)

                if self.lives == 0:
                    self.playing = False
                    self.asteroids.clear()
                    self.missiles.clear()
                    self.explosions.clear()
                else:
                    self.lives -= 1
                    self.ship = Ship()

                break

    def start_game(self):
        """Начинает новую игру с исходными очками и жизнями."""
        self.ship = Ship()
        self.asteroids.clear()
        self.missiles.clear()
        self.explosions.clear()
        self.asteroid_timer = 0
        self.score = 0
        self.lives = INITIAL_LIVES
        self.playing = True

    def draw_splash(self):
        """Рисует заставку с приглашением начать игру."""
        pygame.draw.rect(
            self.screen, SPLASH_COLOR, self.splash_rect
        )

        title = self.font.render(
            "АСТЕРОИДЫ", True, TEXT_COLOR
        )
        hint = self.font.render(
            "Нажмите здесь для начала", True, TEXT_COLOR
        )

        center_x, center_y = self.splash_rect.center
        self.screen.blit(
            title,
            title.get_rect(center=(center_x, center_y - 25)),
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(center_x, center_y + 25)),
        )

    def create_background(self):
        """Создаёт неподвижный фон и прозрачный слой астероидов."""
        self.static_background = pygame.Surface((WIDTH, HEIGHT))
        self.static_background.fill(BACKGROUND_COLOR)

        for _ in range(STAR_COUNT):
            position = (
                random.randrange(WIDTH),
                random.randrange(HEIGHT),
            )
            pygame.draw.circle(
                self.static_background, STAR_COLOR, position, 1
            )

        self.moving_background = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        for _ in range(BACKGROUND_ASTEROID_COUNT):
            center = pygame.Vector2(
                random.randrange(WIDTH),
                random.randrange(HEIGHT),
            )
            radius = random.randint(
                BACKGROUND_ASTEROID_MIN_RADIUS,
                BACKGROUND_ASTEROID_MAX_RADIUS,
            )
            points = [
                center + pygame.Vector2(
                    radius * random.uniform(0.7, 1.0), 0
                ).rotate(angle)
                for angle in range(0, 360, 45)
            ]

            # Копии у краёв позволяют слою двигаться без разрыва.
            for shift_x in (-WIDTH, 0, WIDTH):
                for shift_y in (-HEIGHT, 0, HEIGHT):
                    shifted_points = [
                        point + pygame.Vector2(shift_x, shift_y)
                        for point in points
                    ]
                    pygame.draw.polygon(
                        self.moving_background,
                        BACKGROUND_ASTEROID_COLOR,
                        shifted_points,
                    )

    def draw_background(self):
        """Рисует звёзды и две соседние копии движущегося слоя."""
        self.screen.blit(self.static_background, (0, 0))

        offset = int(self.background_offset)
        self.screen.blit(self.moving_background, (-offset, 0))
        self.screen.blit(
            self.moving_background, (WIDTH - offset, 0)
        )

    def run(self):
        """Управляет событиями, обновлением игры и отрисовкой."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.background_offset = (
                self.background_offset + BACKGROUND_SPEED * dt
            ) % WIDTH

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.playing:
                        if self.splash_rect.collidepoint(event.pos):
                            self.start_game()

                elif event.type == pygame.KEYDOWN:
                    if self.playing and event.key == pygame.K_SPACE:
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

            if self.playing:
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

                self.check_missile_collisions()
                self.check_ship_collisions()

                for explosion in self.explosions:
                    explosion.update(dt)

                self.explosions = [
                    explosion
                    for explosion in self.explosions
                    if not explosion.is_finished()
                ]

            self.draw_background()

            if self.playing:
                for asteroid in self.asteroids:
                    asteroid.draw(self.screen)

                self.ship.draw(self.screen)

                for missile in self.missiles:
                    missile.draw(self.screen)

                for explosion in self.explosions:
                    explosion.draw(self.screen)
            else:
                self.draw_splash()

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
