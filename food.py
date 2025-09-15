import random
from typing import Tuple

import pygame


Vec2 = Tuple[int, int]


class Food:
    def __init__(self, config):
        self.config = config
        self.pos: Vec2 = (0, 0)
        self.img = None

    def load_assets(self):
        try:
            path = f"{self.config.assets_dir}/{self.config.img_food}"
            img = pygame.image.load(path)
            self.img = pygame.transform.scale(img, (self.config.cell_size, self.config.cell_size))
        except Exception:
            self.img = None

    def respawn(self, forbidden):
        # forbidden: iterable of grid positions to avoid (e.g., snake body)
        free = [(x, y) for x in range(self.config.cols) for y in range(self.config.rows) if (x, y) not in forbidden]
        if not free:
            self.pos = (0, 0)
        else:
            self.pos = random.choice(free)

    def draw(self, surf: pygame.Surface):
        cs = self.config.cell_size
        px, py = self.config.grid_to_px(self.pos)
        rect = pygame.Rect(px, py, cs, cs)
        if self.img is not None:
            surf.blit(self.img, rect)
        else:
            pygame.draw.rect(surf, (200, 40, 40), rect)
