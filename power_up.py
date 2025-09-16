import math
import random
from typing import Iterable, Tuple, Optional

import pygame


Vec2 = Tuple[int, int]


POWERUP_DEFS = (
    {
        "key": "batboost",
        "label": "Bat Boost",
        "desc": "Score surge and a burst of speed.",
        "color": (110, 160, 255),
        "score": 3,
        "grow": 2,
        "speed_delta": 4,
        "speed_time": 5,
    },
    {
        "key": "jokertrap",
        "label": "Joker Trap",
        "desc": "Chaotic slowdown that trims the tail.",
        "color": (220, 85, 150),
        "score": -2,
        "grow": -2,
        "speed_delta": -4,
        "speed_time": 5,
    },
)


class PowerUp:
    """Spawnable Gotham-themed modifiers that affect the run."""

    def __init__(self, config):
        self.config = config
        self.definition = POWERUP_DEFS[0]
        self.pos: Vec2 = (0, 0)
        self.img = None
        self.remaining_frames = 0
        self.spawn_tick = 0

    @property
    def label(self) -> str:
        return self.definition["label"]

    @property
    def description(self) -> str:
        return self.definition["desc"]

    @property
    def data(self) -> dict:
        return self.definition

    def _choose_definition(self):
        self.definition = random.choice(POWERUP_DEFS)
        self._load_art()

    def _load_art(self):
        asset_map = getattr(self.config, "powerup_assets", {})
        asset_name = asset_map.get(self.definition["key"])
        if not asset_name:
            self.img = None
            return
        path = f"{self.config.assets_dir}/{asset_name}"
        try:
            img = pygame.image.load(path).convert_alpha()
            self.img = pygame.transform.smoothscale(
                img, (self.config.cell_size, self.config.cell_size)
            )
        except Exception:
            self.img = None

    def spawn(self, forbidden: Iterable[Vec2], lifetime_frames: int) -> bool:
        self._choose_definition()
        blocked = set(forbidden)
        free = [
            (x, y)
            for x in range(self.config.cols)
            for y in range(self.config.rows)
            if (x, y) not in blocked
        ]
        if not free:
            return False
        self.pos = random.choice(free)
        self.remaining_frames = max(0, int(lifetime_frames))
        self.spawn_tick = pygame.time.get_ticks()
        return True

    def tick(self) -> bool:
        if self.remaining_frames <= 0:
            return False
        self.remaining_frames -= 1
        return self.remaining_frames > 0

    def draw(self, surf: pygame.Surface, tick_ms: Optional[int] = None):
        if tick_ms is None:
            tick_ms = pygame.time.get_ticks()
        px, py = self.config.grid_to_px(self.pos)
        cs = self.config.cell_size
        wobble = math.sin((tick_ms / 200.0) + self.pos[0] * 0.5)
        offset = int(wobble * 3)
        rect = pygame.Rect(px, py + offset, cs, cs)
        timer_ratio = 1.0
        if self.remaining_frames > 0:
            timer_ratio = max(0.0, min(1.0, self.remaining_frames / max(1, self.config.fps * self.config.powerup_lifetime)))
        ring_radius = int(cs * (0.6 + 0.25 * math.sin((tick_ms / 140.0) + self.pos[1])))
        pygame.draw.circle(
            surf,
            tuple(min(255, int(c + 40)) for c in self.definition["color"]),
            (rect.centerx, rect.centery),
            ring_radius,
            width=2,
        )
        if self.img is not None:
            surf.blit(self.img, rect)
        else:
            pygame.draw.rect(surf, self.definition["color"], rect, border_radius=6)
            pygame.draw.rect(surf, (30, 30, 30), rect, width=2, border_radius=6)
        if timer_ratio < 1.0:
            # Draw shrinking timer halo
            halo_radius = int(cs * (0.9 * timer_ratio + 0.2))
            pygame.draw.circle(
                surf,
                (220, 220, 220),
                (rect.centerx, rect.centery),
                max(halo_radius, cs // 3),
                width=1,
            )
