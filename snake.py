from collections import deque
from typing import Deque, Tuple, Iterable

import pygame


Vec2 = Tuple[int, int]


class Snake:
    def __init__(self, config, start: Vec2):
        self.config = config
        self.body: Deque[Vec2] = deque()
        for i in range(config.start_length):
            self.body.appendleft((start[0] - i, start[1]))
        self.dir: Vec2 = (1, 0)  # moving right
        self.grow_pending = 0
        self.head_img = None

    def load_assets(self):
        # Load and scale head image
        try:
            path = f"{self.config.assets_dir}/{self.config.img_snake_head}"
            img = pygame.image.load(path)
            self.head_img = pygame.transform.scale(img, (self.config.cell_size, self.config.cell_size))
        except Exception:
            self.head_img = None

    def set_direction(self, d: Vec2):
        # Prevent direct reversal
        if len(self.body) > 1:
            ox, oy = self.dir
            nx, ny = d
            if (ox + nx, oy + ny) == (0, 0):
                return
        self.dir = d

    def head(self) -> Vec2:
        return self.body[0]

    def move(self):
        hx, hy = self.head()
        dx, dy = self.dir
        new_head = ((hx + dx) % self.config.cols, (hy + dy) % self.config.rows)
        self.body.appendleft(new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, n: int = 1):
        self.grow_pending += n

    def collides_self(self) -> bool:
        h = self.head()
        return h in list(self.body)[1:]

    def occupies(self, pos: Vec2) -> bool:
        return pos in self.body

    def draw(self, surf: pygame.Surface):
        cs = self.config.cell_size
        for i, (x, y) in enumerate(self.body):
            px, py = self.config.grid_to_px((x, y))
            rect = pygame.Rect(px, py, cs, cs)
            if i == 0 and self.head_img is not None:
                surf.blit(self.head_img, rect)
            else:
                shade = 70 + min(160, i * 5)
                pygame.draw.rect(surf, (shade, shade, shade), rect)
