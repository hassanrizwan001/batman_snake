import sys
from pathlib import Path

import pygame

from snake import Snake
from food import Food
from score_io import read_high_score, write_high_score


class Game:
    def __init__(self, config):
        self.cfg = config
        self.screen = None
        self.clock = None
        self.font = None
        self.big_font = None
        self.snake = None
        self.food = None
        self.running = True
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.game_over_img = None

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
        pygame.display.set_caption(self.cfg.title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)

        # Load optional game over image
        try:
            go_path = f"{self.cfg.assets_dir}/{self.cfg.img_game_over}"
            img = pygame.image.load(go_path)
            w = min(self.cfg.width - 60, img.get_width())
            h = min(self.cfg.height - 100, img.get_height())
            self.game_over_img = pygame.transform.smoothscale(img, (w, h))
        except Exception:
            self.game_over_img = None

    def reset(self):
        mid = (self.cfg.cols // 2, self.cfg.rows // 2)
        self.snake = Snake(self.cfg, start=mid)
        self.snake.load_assets()
        self.food = Food(self.cfg)
        self.food.load_assets()
        self.food.respawn(forbidden=self.snake.body)
        self.score = 0
        self.game_over = False

        # Ensure score file exists/readable
        self.high_score = read_high_score(self.cfg.score_file)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                if not self.game_over:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.set_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.set_direction((1, 0))
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.set_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.set_direction((0, 1))
                else:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()

    def update(self):
        if self.game_over:
            return
        self.snake.move()
        # Eat food
        if self.snake.head() == self.food.pos:
            self.snake.grow(1)
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
                write_high_score(self.cfg.score_file, self.high_score)
            self.food.respawn(forbidden=self.snake.body)
        # Self collision
        if self.snake.collides_self():
            self.game_over = True

    def draw_grid(self):
        cs = self.cfg.cell_size
        for x in range(self.cfg.cols):
            px, _ = self.cfg.grid_to_px((x, 0))
            pygame.draw.line(self.screen, self.cfg.grid_color, (px, 48), (px, self.cfg.height))
        for y in range(self.cfg.rows):
            _, py = self.cfg.grid_to_px((0, y))
            pygame.draw.line(self.screen, self.cfg.grid_color, (0, py), (self.cfg.width, py))

    def draw_hud(self):
        hud_rect = pygame.Rect(0, 0, self.cfg.width, 48)
        pygame.draw.rect(self.screen, self.cfg.hud_bg, hud_rect)
        text = f"Score: {self.score}    High: {self.high_score}    Esc: Quit"
        surf = self.font.render(text, True, self.cfg.text_color)
        self.screen.blit(surf, (12, 12))

    def draw_game_over(self):
        overlay = pygame.Surface((self.cfg.width, self.cfg.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        msg1 = self.big_font.render("Game Over", True, (240, 80, 80))
        msg2 = self.font.render("Press Enter to restart", True, self.cfg.text_color)
        self.screen.blit(msg1, msg1.get_rect(center=(self.cfg.width // 2, 90)))
        self.screen.blit(msg2, msg2.get_rect(center=(self.cfg.width // 2, 130)))
        if self.game_over_img is not None:
            rect = self.game_over_img.get_rect(center=(self.cfg.width // 2, (self.cfg.height + 48) // 2))
            self.screen.blit(self.game_over_img, rect)

    def draw(self):
        self.screen.fill(self.cfg.bg_color)
        self.draw_hud()
        self.draw_grid()
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        try:
            self.init_pygame()
            self.reset()
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(self.cfg.fps)
        finally:
            pygame.quit()
