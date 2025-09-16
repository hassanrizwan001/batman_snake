class Config:
    """Central configuration for the Batman Snake game."""

    # Grid settings
    CELL_SIZE = 24
    GRID_COLS = 24
    GRID_ROWS = 24

    # Window settings
    TITLE = "Batman Snake"
    BG_COLOR = (10, 10, 10)
    GRID_COLOR = (35, 35, 35)
    TEXT_COLOR = (240, 240, 240)
    HUD_BG = (20, 20, 20)

    # Gameplay
    START_LENGTH = 3
    FPS = 12

    # File and assets
    SCORE_FILE = "highscore.txt"
    ASSETS_DIR = "assets"
    IMG_SNAKE_HEAD = "batman.png"
    IMG_FOOD = "joker.jpeg"
    IMG_GAME_OVER = "batman_joker_death.jpeg"
    MUSIC_FILE = "gotham_theme.ogg"

    POWERUP_ASSETS = {
        "batboost": "bat_signal.png",
        "jokertrap": "joker_card.png",
    }

    POWERUP_LIFETIME = 8  # seconds

    CHARACTERS = {
        "Batman": {
            "head": "batman.png",
            "body_palette": [(50, 50, 60), (32, 32, 32), (75, 75, 95)],
            "trail": (245, 220, 80),
        },
        "Joker": {
            "head": "joker.jpeg",
            "body_palette": [(80, 15, 15), (120, 30, 90), (190, 60, 140)],
            "trail": (120, 210, 90),
        },
    }
    DEFAULT_CHARACTER = "Batman"

    DIFFICULTIES = {
        "Rookie": {
            "fps": 10,
            "powerup_delay": 9,  # seconds between spawns
            "description": "Relaxed patrol around Gotham.",
        },
        "Vigilante": {
            "fps": 14,
            "powerup_delay": 7,
            "description": "Balanced pace with frequent threats.",
        },
        "Dark Knight": {
            "fps": 18,
            "powerup_delay": 6,
            "description": "Relentless speed for seasoned heroes.",
        },
    }

    def __init__(self):
        self.cell_size = int(self.CELL_SIZE)
        self.cols = int(self.GRID_COLS)
        self.rows = int(self.GRID_ROWS)
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size + 48  # extra space for HUD
        self.title = self.TITLE
        self.bg_color = self.BG_COLOR
        self.grid_color = self.GRID_COLOR
        self.text_color = self.TEXT_COLOR
        self.hud_bg = self.HUD_BG
        self.start_length = int(self.START_LENGTH)
        self.fps = int(self.FPS)
        self.score_file = self.SCORE_FILE
        self.assets_dir = self.ASSETS_DIR
        self.img_snake_head = self.IMG_SNAKE_HEAD
        self.img_food = self.IMG_FOOD
        self.img_game_over = self.IMG_GAME_OVER
        self.music_file = self.MUSIC_FILE
        self.powerup_assets = dict(self.POWERUP_ASSETS)
        self.powerup_lifetime = int(self.POWERUP_LIFETIME)
        self.difficulties = dict(self.DIFFICULTIES)
        self.characters = dict(self.CHARACTERS)
        self.default_character = self.DEFAULT_CHARACTER

    def grid_to_px(self, pos):
        x, y = pos
        return x * self.cell_size, y * self.cell_size + 48

    def get_character(self, name):
        """Return a character definition merged with sensible defaults."""
        base = {
            "head": self.IMG_SNAKE_HEAD,
            "body_palette": [(70, 70, 70), (50, 50, 50)],
            "trail": (255, 215, 0),
        }
        base.update(self.characters.get(name, {}))
        head_asset = base.get("head") or self.IMG_SNAKE_HEAD
        base["head"] = head_asset
        palette = base.get("body_palette") or [(70, 70, 70), (50, 50, 50)]
        if not isinstance(palette, (list, tuple)):
            palette = [palette]
        base["body_palette"] = list(palette)
        return base
