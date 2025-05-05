from src.models.score import BaseScore
import datetime

class Score(BaseScore):
    def __init__(self):
        super().__init__()
        self.last_pop_time = datetime.datetime.now()  # 添加最后消除时间跟踪
    
    def add_score(self, points):
        self.score += points
        self.last_pop_time = datetime.datetime.now()  # 更新最后消除时间
        
    def check_speed_boost(self):
        # 检查是否需要触发加速
        idle_time = (datetime.datetime.now() - self.last_pop_time).seconds
        return idle_time >= 5  # 5秒无消除返回True

    def win(self):
        self.is_win = True

    def lose(self):
        self.is_lose = True

    def setup_next_level(self):
        self.is_win = False
        self.is_lose = False