"""
main.py — Entry point
"""

from game_settings import Config
from game import Game

if __name__ == "__main__":
    config = Config()
    Game(config).run()
