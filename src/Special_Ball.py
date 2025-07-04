import datetime
import random
from enum import Enum


class Bonus(Enum):
    Pause = 0
    Reverse = 1
    Bomb = 2
    Speed = 3
    InstantWin = 4


class Special_Ball:
    def __init__(self, ball_generator):
        self.ball_generator = ball_generator
        self.bonuses = [Bonus.Pause, Bonus.Reverse, Bonus.Bomb, Bonus.Speed]
        self.game_start_time = datetime.datetime.now()
        self.pause_start_time = None
        self.reverse_start_time = None
        self.speed_start_time = None
        self.balls_with_bonuses = []

    def start_bonus(self, bonus):
        if bonus is Bonus.Pause:
            self.start_pause()
        elif bonus is Bonus.Reverse:
            self.start_reverse()
        elif bonus is Bonus.Speed:
            self.start_speed()

    def start_speed(self):
        self.speed_start_time = datetime.datetime.now()
        self.ball_generator.slow_down = True
        self.ball_generator.speed_factor = 0.5

    def start_reverse(self):
        self.reverse_start_time = datetime.datetime.now()
        self.ball_generator.reverse = True

    def start_pause(self):
        self.pause_start_time = datetime.datetime.now()
        self.ball_generator.pause = True

    def stop_reverse(self):
        self.reverse_start_time = None
        self.ball_generator.reverse = False

    def stop_pause(self):
        self.pause_start_time = None
        self.ball_generator.pause = False

    def stop_speed(self):
        self.speed_start_time = None
        self.ball_generator.slow_down = False
        self.ball_generator.speed_factor = 1

    def handle_reverse_bonus(self):
        if self.reverse_start_time is not None:
            if (datetime.datetime.now() - self.reverse_start_time).seconds < 4:
                self.move_balls_back()
            else:
                self.stop_reverse()

    def move_balls_back(self):
        speed_factor = self.ball_generator.speed_factor
        for i in range(len(self.ball_generator.balls)):
            self.ball_generator.balls[i].move(-1 * speed_factor)

    def handle_pause_bonus(self):
        if self.pause_start_time is not None:
            if (datetime.datetime.now() - self.pause_start_time).seconds == 5:
                self.stop_pause()

    def handle_speed_bonus(self):
        # 判断减速状态是否超过5秒
        if self.speed_start_time is None:
            return False
        delta = (datetime.datetime.now() - self.speed_start_time).seconds
        if delta >= 5:
            self.stop_speed()
            return False
        return True 

    def handle_bomb_bonus(self, chain):
        chain_tail = self.ball_generator.balls.index(chain[0]) - 1
        chain_head = self.ball_generator.balls.index(chain[-1]) + 1

        result_chain = []

        for _ in range(3):
            if chain_tail < 0:
                break
            result_chain.append(self.ball_generator.balls[chain_tail])
            chain_tail -= 1

        for _ in range(3):
            if chain_head > len(self.ball_generator.balls) - 1:
                break
            result_chain.append(self.ball_generator.balls[chain_head])
            chain_head += 1

        return result_chain

    def update(self):
        self.handle_reverse_bonus()
        self.handle_pause_bonus()
        self.handle_speed_bonus()
        self.update_balls_with_bonuses()
        self.generate_bonus()

    def generate_bonus(self):
        cur_time = datetime.datetime.now()
        if (cur_time - self.game_start_time).seconds == 15:
            ball_with_bonus = random.choice(self.ball_generator.balls)
            bonus = random.choice([*self.bonuses, Bonus.InstantWin])
            ball_with_bonus.set_bonus(bonus)
            self.balls_with_bonuses.append((ball_with_bonus, cur_time))
            self.game_start_time = cur_time

    def update_balls_with_bonuses(self):
        for ball, time in self.balls_with_bonuses:
            # 对InstantWin特殊处理5秒消失，其他保持15秒
            timeout = 3 if ball.bonus is Bonus.InstantWin else 15
            if (datetime.datetime.now() - time).seconds >= timeout:
                ball.set_bonus(None)
                self.balls_with_bonuses.remove((ball, time))
