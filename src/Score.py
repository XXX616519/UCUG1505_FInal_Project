from src.models.score import BaseScore

class Score(BaseScore):
    def win(self):
        self.is_win = True

    def lose(self):
        self.is_lose = True

    def setup_next_level(self):
        self.is_win = False
        self.is_lose = False