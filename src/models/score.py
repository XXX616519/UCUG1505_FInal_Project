class BaseScore:
    def __init__(self):
        self.score = 0
        self.lives = 2
        self.is_win = False
        self.is_lose = False
        self.lose_game = False

    def add_score(self, score):
        self.add_lives(score)
        self.score += score

    def add_lives(self, score):
        for i in range(self.score + 1, self.score + score + 1):
            if i % 500 == 0:
                self.lives += 1

    def take_live(self):
        self.lives -= 1
        self.check_for_game_lose()

    def check_for_game_lose(self):
        if self.lives == 0:
            self.lose_game = True
