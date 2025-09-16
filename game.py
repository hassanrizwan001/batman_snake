from pathlib import Path
import math

import pygame

from snake import Snake
from food import Food
from power_up import PowerUp
from score_io import read_high_score, write_high_score


class Game:
    def __init__(self, config):
        self.cfg = config
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.big_font = None
        self.snake = None
        self.food = None
        self.power_up = None
        self.running = True
        self.score = 0
        self.high_score = 0
        self.state = "menu"
        self.game_over = False
        self.game_over_img = None
        self.effect_message = ""
        self.effect_msg_timer = 0
        self.speed_effect_delta = 0
        self.speed_effect_timer = 0
        self.frames_since_powerup = 0

        self.difficulty_names = list(self.cfg.difficulties.keys())
        if not self.difficulty_names:
            self.difficulty_names = ["Standard"]
            self.cfg.difficulties.setdefault(
                "Standard",
                {
                    "fps": self.cfg.fps,
                    "powerup_delay": 8,
                    "description": "Default pace.",
                },
            )
        self.selected_difficulty = 0
        self.current_difficulty = self.difficulty_names[self.selected_difficulty]
        self.diff_data = self._load_difficulty(self.current_difficulty)
        self.base_fps = int(self.diff_data["fps"])
        self.powerup_delay = int(self.diff_data["powerup_delay"])

        self.character_names = list(self.cfg.characters.keys())
        if not self.character_names:
            self.character_names = [self.cfg.default_character]
        if self.cfg.default_character in self.character_names:
            self.selected_character = self.character_names.index(self.cfg.default_character)
        else:
            self.selected_character = 0
        self.current_character_name = self.character_names[self.selected_character]
        self.current_character_data = self.cfg.get_character(self.current_character_name)
        self.character_previews = {}
        self.menu_background_phase = 0.0

    def _load_difficulty(self, name):
        base = {"fps": self.cfg.fps, "powerup_delay": 8, "description": ""}
        base.update(self.cfg.difficulties.get(name, {}))
        return base

    def init_pygame(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
        pygame.display.set_caption(self.cfg.title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
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

        self._load_character_previews()
        self._load_music()

    def _load_music(self):
        music_name = getattr(self.cfg, "music_file", "")
        if not music_name:
            return
        music_path = Path(self.cfg.assets_dir) / music_name
        if not music_path.exists():
            return
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def _load_character_previews(self):
        self.character_previews = {}
        preview_size = self.cfg.cell_size * 3
        for name in self.character_names:
            data = self.cfg.get_character(name)
            asset = data.get("head") or self.cfg.img_snake_head
            path = Path(self.cfg.assets_dir) / asset
            try:
                img = pygame.image.load(path).convert_alpha()
                scaled = pygame.transform.smoothscale(img, (preview_size, preview_size))
                self.character_previews[name] = scaled
            except Exception:
                preview = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)
                pygame.draw.circle(
                    preview,
                    (200, 200, 200, 180),
                    (preview_size // 2, preview_size // 2),
                    preview_size // 2,
                )
                self.character_previews[name] = preview

    def start_game(self):
        self.current_difficulty = self.difficulty_names[self.selected_difficulty]
        self.diff_data = self._load_difficulty(self.current_difficulty)
        self.base_fps = int(self.diff_data.get("fps", self.cfg.fps))
        self.powerup_delay = max(1, int(self.diff_data.get("powerup_delay", 8)))
        self.current_character_name = self.character_names[self.selected_character]
        self.current_character_data = self.cfg.get_character(self.current_character_name)
        self.reset()
        self.state = "playing"

    def reset(self):
        mid = (self.cfg.cols // 2, self.cfg.rows // 2)
        self.snake = Snake(self.cfg, start=mid, character=self.current_character_data)
        self.snake.load_assets()
        self.food = Food(self.cfg)
        self.food.load_assets()
        self.food.respawn(forbidden=self.snake.body)
        self.power_up = None
        self.frames_since_powerup = 0
        self.speed_effect_delta = 0
        self.speed_effect_timer = 0
        self.effect_message = ""
        self.effect_msg_timer = 0
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
                elif self.state == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_difficulty = (self.selected_difficulty - 1) % len(
                            self.difficulty_names
                        )
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_difficulty = (self.selected_difficulty + 1) % len(
                            self.difficulty_names
                        )
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.selected_character = (self.selected_character - 1) % len(
                            self.character_names
                        )
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.selected_character = (self.selected_character + 1) % len(
                            self.character_names
                        )
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_game()
                elif self.state == "playing":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.set_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.set_direction((1, 0))
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.set_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.set_direction((0, 1))
                elif self.state == "game_over":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_game()
                    elif event.key in (pygame.K_m,):
                        self.state = "menu"

    def update(self):
        if self.state != "playing":
            return
        self.snake.move()

        # Eat food
        if self.snake.head() == self.food.pos:
            self.snake.grow(1)
            self.score += 1
            self._update_high_score()
            forbidden = set(self.snake.body)
            if self.power_up:
                forbidden.add(self.power_up.pos)
            self.food.respawn(forbidden=forbidden)

        # Handle power-up lifecycle
        if self.power_up:
            if not self.power_up.tick():
                self.power_up = None
            elif self.snake.head() == self.power_up.pos:
                self._consume_power_up()

        self.frames_since_powerup += 1
        spawn_threshold = self.powerup_delay * self.base_fps
        if self.power_up is None and self.frames_since_powerup >= spawn_threshold:
            self._spawn_power_up()

        # Self collision
        if self.snake.collides_self():
            self.game_over = True
            self.state = "game_over"

        # Timers for effects/messages
        if self.speed_effect_timer > 0:
            self.speed_effect_timer -= 1
            if self.speed_effect_timer == 0:
                self.speed_effect_delta = 0
        if self.effect_msg_timer > 0:
            self.effect_msg_timer -= 1
            if self.effect_msg_timer == 0:
                self.effect_message = ""

    def _spawn_power_up(self):
        self.power_up = PowerUp(self.cfg)
        forbidden = set(self.snake.body)
        forbidden.add(self.food.pos)
        lifetime_frames = self.cfg.powerup_lifetime * self.base_fps
        if not self.power_up.spawn(forbidden, lifetime_frames):
            self.power_up = None
        else:
            self.frames_since_powerup = 0

    def _consume_power_up(self):
        data = self.power_up.data
        score_delta = data.get("score", 0)
        if score_delta:
            self.score = max(0, self.score + score_delta)
        grow = data.get("grow", 0)
        if grow > 0:
            self.snake.grow(grow)
        elif grow < 0:
            shrink = min(len(self.snake.body) - 2, abs(grow))
            for _ in range(max(0, shrink)):
                if len(self.snake.body) > 2:
                    self.snake.body.pop()
        speed_delta = data.get("speed_delta", 0)
        if speed_delta:
            self.speed_effect_delta = speed_delta
            self.speed_effect_timer = max(
                self.base_fps, data.get("speed_time", 4) * self.base_fps
            )
        self.effect_message = f"{self.power_up.label}! {self.power_up.description}"
        self.effect_msg_timer = 2 * self.base_fps
        self.power_up = None
        self.frames_since_powerup = 0
        self._update_high_score()

    def _update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            write_high_score(self.cfg.score_file, self.high_score)

    def draw_grid(self, tick_ms: int):
        base_color = self.cfg.grid_color
        pulse = max(0, int(18 * math.sin(tick_ms / 280.0)))
        grid_color = tuple(min(255, c + pulse) for c in base_color)
        cs = self.cfg.cell_size
        for x in range(self.cfg.cols):
            px, _ = self.cfg.grid_to_px((x, 0))
            pygame.draw.line(self.screen, grid_color, (px, 48), (px, self.cfg.height))
        for y in range(self.cfg.rows):
            _, py = self.cfg.grid_to_px((0, y))
            pygame.draw.line(self.screen, grid_color, (0, py), (self.cfg.width, py))

    def draw_hud(self):
        hud_rect = pygame.Rect(0, 0, self.cfg.width, 48)
        pygame.draw.rect(self.screen, self.cfg.hud_bg, hud_rect)
        text = (
            f"Score: {self.score}    High: {self.high_score}    "
            f"Mode: {self.current_difficulty}    Hero: {self.current_character_name}"
        )
        surf = self.font.render(text, True, self.cfg.text_color)
        self.screen.blit(surf, (12, 6))
        if self.effect_message and self.effect_msg_timer > 0:
            msg_surf = self.small_font.render(self.effect_message, True, (220, 200, 90))
            self.screen.blit(msg_surf, (12, 26))
        else:
            info = self.small_font.render("Esc: Quit", True, self.cfg.text_color)
            self.screen.blit(info, (12, 26))

    def draw_menu_background(self, tick_ms: int):
        self.screen.fill(self.cfg.bg_color)
        radius = int(min(self.cfg.width, self.cfg.height) * 0.35)
        pulse = 0.5 + 0.5 * math.sin(tick_ms / 600.0)
        spotlight = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            spotlight,
            (240, 220, 120, int(90 + pulse * 70)),
            (radius, radius),
            radius,
        )
        spotlight_rect = spotlight.get_rect(center=(self.cfg.width // 2, self.cfg.height // 2 + 40))
        self.screen.blit(spotlight, spotlight_rect)

    def draw_menu(self, tick_ms: int):
        self.draw_menu_background(tick_ms)
        title = self.big_font.render("Batman Snake", True, self.cfg.text_color)
        self.screen.blit(title, title.get_rect(center=(self.cfg.width // 2, 110)))

        prompt = self.small_font.render(
            "Select difficulty (Up/Down) and hero (Left/Right)", True, self.cfg.text_color
        )
        self.screen.blit(prompt, prompt.get_rect(center=(self.cfg.width // 2, 154)))

        current_hero = self.character_names[self.selected_character]
        preview = self.character_previews.get(current_hero)
        if preview is not None:
            wobble = 4 * math.sin(tick_ms / 450.0)
            rect = preview.get_rect(center=(self.cfg.width // 2, 238 + wobble))
            self.screen.blit(preview, rect)
        hero_label = self.font.render(f"Current hero: {current_hero}", True, (240, 200, 80))
        self.screen.blit(hero_label, hero_label.get_rect(center=(self.cfg.width // 2, 320)))

        for idx, name in enumerate(self.difficulty_names):
            desc = self.cfg.difficulties.get(name, {}).get("description", "")
            label = f"{name} - {desc}" if desc else name
            is_selected = idx == self.selected_difficulty
            color = (240, 200, 80) if is_selected else self.cfg.text_color
            surf = self.font.render(label, True, color)
            y = 360 + idx * 32
            self.screen.blit(surf, surf.get_rect(center=(self.cfg.width // 2, y)))

        hint = self.small_font.render("Press Enter to patrol Gotham", True, self.cfg.text_color)
        self.screen.blit(hint, hint.get_rect(center=(self.cfg.width // 2, self.cfg.height - 60)))

    def draw_game_over(self):
        overlay = pygame.Surface((self.cfg.width, self.cfg.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        msg1 = self.big_font.render("Game Over", True, (240, 80, 80))
        msg2 = self.font.render("Press Enter to restart", True, self.cfg.text_color)
        msg3 = self.small_font.render("Press M for menu", True, self.cfg.text_color)
        self.screen.blit(msg1, msg1.get_rect(center=(self.cfg.width // 2, 90)))
        self.screen.blit(msg2, msg2.get_rect(center=(self.cfg.width // 2, 130)))
        self.screen.blit(msg3, msg3.get_rect(center=(self.cfg.width // 2, 158)))
        if self.game_over_img is not None:
            rect = self.game_over_img.get_rect(center=(self.cfg.width // 2, (self.cfg.height + 48) // 2))
            self.screen.blit(self.game_over_img, rect)

    def draw(self):
        tick_ms = pygame.time.get_ticks()
        if self.state == "menu":
            self.draw_menu(tick_ms)
        else:
            self.screen.fill(self.cfg.bg_color)
            self.draw_hud()
            self.draw_grid(tick_ms)
            self.food.draw(self.screen, tick_ms)
            if self.power_up:
                self.power_up.draw(self.screen, tick_ms)
            self.snake.draw(self.screen, tick_ms)
            if self.state == "game_over":
                self.draw_game_over()
        pygame.display.flip()

    def get_tick_rate(self):
        if self.speed_effect_timer > 0:
            return max(4, self.base_fps + self.speed_effect_delta)
        return self.base_fps

    def run(self):
        try:
            self.init_pygame()
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(self.get_tick_rate())
        finally:
            pygame.quit()


if __name__ == "__main__":
    from game_settings import Config

    Game(Config()).run()
