from src.Constants import *
from src.Sprites import Ball
from src.models.ball import Basic_Ball
import random
import datetime

class Generate_Ball(Basic_Ball):
    def __init__(self, path, number, score_manager):
        super().__init__(path, number, score_manager)
        self.speed_factor = SPEED_NORMAL  # 使用常量初始化
        self.speed_boost_end = None  # 加速结束时间

    def generate(self):
        if self.number_of_generated < self.number_to_generate:
            if len(self.balls) == 0 or \
                    self.balls[0].pos_in_path >= 2 * BALL_RADIUS // \
                    self.path.step:
                self.balls.insert(0, Ball(random.choice(self.colors), 0,
                                          self.path))
                self.number_of_generated += 1

    def move_stopped_ball(self, i):
        if not self.balls[i].can_move:
            # 只有当后面的球足够接近时才唤醒（等待后段汇合）
            if i > 0 and self.balls[i-1].can_move:
                distance = self.balls[i].pos_in_path - self.balls[i-1].pos_in_path
                if distance <= 20:
                    self.balls[i].can_move = True

    def update_balls(self):
        # 检查是否需要恢复普通速度
        if self.speed_boost_end and datetime.datetime.now() > self.speed_boost_end:
            self.speed_factor = SPEED_NORMAL
            self.speed_boost_end = None
            
        # 更新速度因子
        if self.score_manager.check_speed_boost():
            self.speed_factor = SPEED_FAST
            if not self.speed_boost_end:  # 首次触发时设置结束时间
                self.speed_boost_end = datetime.datetime.now() + datetime.timedelta(seconds=3)
        
        # 设置每个球的 prev_ball 属性为下一球，限制前端球的移动
        for idx, ball in enumerate(self.balls):
            if idx < len(self.balls) - 1:
                ball.prev_ball = self.balls[idx + 1]
            else:
                ball.prev_ball = None
        
        for i in range(len(self.balls)):
            if self.balls[i].can_move:
                # 仅影响移动速度，不影响位置计算
                self.balls[i].move(1 * self.speed_factor)
            self.move_stopped_ball(i)

    def update_chain(self):
        for i in range(1, len(self.balls)):
            left_ball = self.balls[i - 1]
            right_ball = self.balls[i]
            # 恢复固定间距判断（移除速度因子影响）
            if right_ball.pos_in_path - left_ball.pos_in_path > 20:
                if left_ball.color == right_ball.color:
                    self.join_balls(i - 1)
                else:
                    self.stop_balls(i)

    def update(self):
        # 设置每个球的 prev_ball 属性，用于在 move 中限制和 join 时正确关联
        for idx, ball in enumerate(self.balls):
            if idx > 0:
                ball.prev_ball = self.balls[idx-1]
            else:
                ball.prev_ball = None
        self.update_chain()
        if not self.reverse and not self.pause:
            self.update_balls()
        if len(self.balls) == 0 and self.number_of_generated == \
                self.number_to_generate:
            self.score_manager.win()
        

    def draw(self, screen):
        for ball in self.balls:
            ball.draw(screen)

    def get_available_colors(self):
        return [ball.color for ball in self.balls]

    def insert(self, index, shooting_ball):
        ball = self.convert_shooting_ball(index, shooting_ball)
        self.balls.insert(index + 1, ball)
        for i in range(index + 2, len(self.balls)):
            if self.balls[i].pos_in_path - self.balls[i - 1].pos_in_path >= \
                    2 * BALL_RADIUS // self.path.step:
                break
            self.balls[i].set_position(self.count_next_pos(i - 1))

    def convert_shooting_ball(self, index, shooting_ball):
        ball = Ball(shooting_ball.color,
                    self.count_next_pos(index), self.path)
        ball.can_move = self.balls[index].can_move
        return ball

    def destroy(self, chain):
        # Remove specified balls and freeze head segment until back segment catches up
        # Determine the start index of the removed segment in original list
        indices = sorted(self.balls.index(ball) for ball in chain)
        start = indices[0] if indices else len(self.balls)
        # Remove the eliminated balls
        for ball in chain:
            if ball in self.balls:
                self.balls.remove(ball)
        # Freeze head segment (balls after the removal) until back segment catches up
        for i in range(start, len(self.balls)):
            self.balls[i].can_move = False

    def join_balls(self, index):
        # 保持自然移动速度
        target_pos = self.count_next_pos(index)
        for i in range(index + 1, len(self.balls)):
            if self.balls[i].pos_in_path < target_pos:
                # 使用基础速度移动（不受速度因子影响）
                self.balls[i].move(1)
            else:
                break
            target_pos = self.count_next_pos(i)

    def stop_balls(self, tail_index):
        # 修改停止逻辑：停止后面的球直到间距恢复
        for idx in range(tail_index, len(self.balls)):
            if idx == 0:
                continue
            gap = self.balls[idx].pos_in_path - self.balls[idx-1].pos_in_path
            if gap > 20:
                for j in range(idx, len(self.balls)):
                    self.balls[j].can_move = False
                break

    def count_next_pos(self, index):
        return self.balls[index].pos_in_path + 2 * BALL_RADIUS // self.path.step