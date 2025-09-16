import math
import random
from typing import Tuple, Optional

import pygame


Vec2 = Tuple[int, int]


class Food:
    def __init__(self, config):
        self.config = config
        self.pos: Vec2 = (0, 0)
        self.img = None
        self.glow = None

    def load_assets(self):
        try:
            path = f"{self.config.assets_dir}/{self.config.img_food}"
            img = pygame.image.load(path).convert_alpha()
            self.img = pygame.transform.smoothscale(
                img, (self.config.cell_size, self.config.cell_size)
            )
        except Exception:
            self.img = None
        size = self.config.cell_size + 24
        self.glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            self.glow,
            (210, 60, 90, 90),
            (size // 2, size // 2),
            size // 2,
        )

    def respawn(self, forbidden):
        # forbidden: iterable of grid positions to avoid (e.g., snake body)
        free = [
            (x, y)
            for x in range(self.config.cols)
            for y in range(self.config.rows)
            if (x, y) not in forbidden
        ]
        if not free:
            self.pos = (0, 0)
        else:
            self.pos = random.choice(free)

    def draw(self, surf: pygame.Surface, tick_ms: Optional[int] = None):
        if tick_ms is None:
            tick_ms = pygame.time.get_ticks()
        cs = self.config.cell_size
        px, py = self.config.grid_to_px(self.pos)
        wobble = math.sin((tick_ms / 220.0) + self.pos[0] * 0.6)
        offset = int(wobble * 4)
        if self.glow is not None:
            scale = 1.0 + 0.2 * math.sin((tick_ms / 310.0) + self.pos[1] * 0.4)
            size = int(self.glow.get_width() * scale)
            glow = pygame.transform.smoothscale(self.glow, (size, size))
            rect = glow.get_rect(center=(px + cs // 2, py + cs // 2 + offset))
            surf.blit(glow, rect)
        rect = pygame.Rect(px, py + offset, cs, cs)
        if self.img is not None:
            surf.blit(self.img, rect)
        else:
            pygame.draw.rect(surf, (200, 40, 40), rect, border_radius=5)
