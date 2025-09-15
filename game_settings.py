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
    # Note: the repo folder is spelled 'assests'
    ASSETS_DIR = "assests"
    IMG_SNAKE_HEAD = "batman.png"
    IMG_FOOD = "joker.jpeg"
    IMG_GAME_OVER = "batman_joker_death.jpeg"

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

    def grid_to_px(self, pos):
        x, y = pos
        return x * self.cell_size, y * self.cell_size + 48
