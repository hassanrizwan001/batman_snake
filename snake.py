from collections import deque
from typing import Deque, Tuple, Optional
import math

import pygame


Vec2 = Tuple[int, int]


class Snake:
    def __init__(self, config, start: Vec2, character: Optional[dict] = None):
        self.config = config
        self.character = character or {}
        self.body: Deque[Vec2] = deque(
            (start[0] - i, start[1]) for i in range(config.start_length)
        )
        self.dir: Vec2 = (1, 0)  # moving right
        self.grow_pending = 0
        self.head_img = None
        self.head_frames: dict[Vec2, list[pygame.Surface]] = {}
        self.body_palette = self.character.get("body_palette", [(70, 70, 70)])
        if not self.body_palette:
            self.body_palette = [(70, 70, 70)]
        self.trail_color = self.character.get("trail", (240, 210, 80))

    def load_assets(self):
        head_name = self.character.get("head") or self.config.img_snake_head
        try:
            path = f"{self.config.assets_dir}/{head_name}"
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            img = None
        if img is None:
            self.head_img = None
            self.head_frames = {}
            return

        base_frames = self._build_head_variants(img)
        self._build_oriented_frames(base_frames)
        default_frames = self.head_frames.get((1, 0))
        if default_frames:
            self.head_img = default_frames[0]
        else:
            self.head_img = None

    def _build_head_variants(self, base: pygame.Surface) -> list[pygame.Surface]:
        # Create subtle animation frames by adding a glow and cape flicker overlay.
        frames = []
        frames.append(base.copy())

        glow = base.copy()
        overlay = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        w, h = base.get_size()
        pygame.draw.circle(
            overlay,
            (*self.trail_color, 70),
            (w // 2, h // 2),
            max(6, int(0.45 * max(w, h))),
        )
        glow.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        frames.append(glow)

        blink = base.copy()
        eyelid = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(
            eyelid,
            (30, 30, 30, 160),
            pygame.Rect(0, int(h * 0.45), w, max(2, int(h * 0.18))),
        )
        blink.blit(eyelid, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        frames.append(blink)
        return frames

    def _build_oriented_frames(self, frames: list[pygame.Surface]):
        size = (self.config.cell_size, self.config.cell_size)
        oriented: dict[Vec2, list[pygame.Surface]] = {}
        base_scaled = [pygame.transform.smoothscale(frame, size) for frame in frames]
        oriented[(1, 0)] = base_scaled
        for direction, angle in {
            (-1, 0): 180,
            (0, -1): 90,
            (0, 1): -90,
        }.items():
            oriented[direction] = [
                pygame.transform.smoothscale(pygame.transform.rotate(frame, angle), size)
                for frame in frames
            ]
        self.head_frames = oriented

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

    def _segment_color(self, index: int, tick_ms: int) -> Tuple[int, int, int]:
        palette = self.body_palette
        base = palette[index % len(palette)]
        wobble = 0.6 + 0.4 * math.sin((tick_ms / 220.0) + index * 0.55)
        return tuple(min(255, max(0, int(c * wobble))) for c in base)

    def draw(self, surf: pygame.Surface, tick_ms: Optional[int] = None):
        if tick_ms is None:
            tick_ms = pygame.time.get_ticks()
        cs = self.config.cell_size
        frames = self.head_frames.get(self.dir) or self.head_frames.get((1, 0))
        if frames:
            frame_idx = (tick_ms // 150) % len(frames)
            head_surface = frames[frame_idx]
        else:
            head_surface = None

        for i, (x, y) in enumerate(self.body):
            px, py = self.config.grid_to_px((x, y))
            rect = pygame.Rect(px, py, cs, cs)
            if i == 0 and head_surface is not None:
                surf.blit(head_surface, rect)
            else:
                color = self._segment_color(i, tick_ms)
                pygame.draw.rect(surf, color, rect, border_radius=6)
                if i > 0:
                    pulse = 0.3 + 0.7 * math.sin((tick_ms / 260.0) + i * 0.4)
                    radius = max(2, int((cs // 2) * 0.35 * pulse))
                    center = (rect.centerx, rect.centery)
                    pygame.draw.circle(surf, self.trail_color, center, radius)

        if not frames and self.head_img is not None:
            # fallback static head
            px, py = self.config.grid_to_px(self.head())
            rect = pygame.Rect(px, py, cs, cs)
            surf.blit(self.head_img, rect)
