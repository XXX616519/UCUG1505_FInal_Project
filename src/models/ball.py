import random
from src.Constants import BALL_RADIUS
from src.Constants import BLUE, RED, GREEN, YELLOW
from src.Sprites import Ball
import datetime

class Basic_Ball:
    def __init__(self, path, number, score_manager):
        self.score_manager = score_manager
        self.path = path
        self.colors = [BLUE, RED, GREEN, YELLOW]
        self.balls = []
        self.number_to_generate = number
        self.number_of_generated = 0

        self.reverse = False
        self.pause = False
        self.slow_down = False
        self.speed_factor = 1

    def generate(self):
        if self.number_of_generated < self.number_to_generate:
            if len(self.balls) == 0 or \
                    self.balls[0].pos_in_path >= 2 * BALL_RADIUS // \
                    self.path.step:
                self.balls.insert(0, Ball(random.choice(self.colors), 0,
                                          self.path))
                self.number_of_generated += 1