import pygame
from src.Path import Path
from src.Sprites import *
from src.models.player import Player
from src.Generate_Ball import Generate_Ball
from src.Shoot import Shoot
from src.Special_Ball import Special_Ball
from src.Score import Score
from src.ui.ui_gen import UiManager
from src.ui import *

class Level:
    def __init__(self, number, score_manager):
        self.number = number
        self.path = Path(number)
        self.ball_generator = Generate_Ball(self.path, number * 50, score_manager)
        self.bonus_manager = Special_Ball(self.ball_generator)
        self.player = Player(number)
        self.finish = Finish(self.path, self.ball_generator.balls, score_manager)
        self.shooting_manager = Shoot(self.ball_generator, self.player.pos, self.bonus_manager, score_manager)

