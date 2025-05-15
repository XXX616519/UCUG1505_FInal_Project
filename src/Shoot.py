import pygame
import random
import math
import datetime
import os
import csv
from src.Sprites import ShootingBall
from src.Constants import *
from src.Special_Ball import Bonus

class Shoot:
    def __init__(self, ball_generator, player, bonus_manager, score_manager):
        self.ball_generator = ball_generator
        self.player = player  # 接收整个 player 对象
        self.bonus_manager = bonus_manager
        self.score_manager = score_manager

        self.charged_ball = ShootingBall(random.choice(
            self.ball_generator.colors), self.player.get_shoot_pos())
        self.shooting_balls = []
        self.combo_chain = []
        self.speed = False

        # 用于记录每次射击的日志（内部保存，仅供调试或后续使用）
        # 日志记录字段：射击时间、与上一发射间隔、球的颜色、射击角度
        self.shot_log = []

        # 设置保存 csv 的文件夹与文件
        self.log_dir = "lucky"
        self.csv_log_file = os.path.join(self.log_dir, "lucky.csv")
        os.makedirs(self.log_dir, exist_ok=True)
        # 如果 csv 文件不存在，则写入表头（时间、角度、颜色）
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["time", "angle", "color"])

        # 加载声音和图片
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.smoke_image = pygame.image.load("assets/images/smoke.png")

    def shoot(self, target):
        """
        射击方法
         - target 可以是角度（手势控制）或鼠标坐标。
         - 射击时会记录射击的时间、角度、颜色到 shot_log 以及写入 lucky/lucky.csv 文件中，列为：time, angle, color。
        """
        # 控制连续射击的时间间隔（微秒），防止短时间内重复发射
        if len(self.shooting_balls) == 0 or self.speed or \
                (datetime.datetime.now() - self.shooting_balls[-1].time).microseconds > 300000:
            
            shooting_ball = self.charged_ball
            # 固定位置（可根据需要改为 self.player.get_shoot_pos()）
            shooting_ball.pos = (530, 330)
            print("Shooting ball 发射位置: ", shooting_ball.pos)

            # 记录射击时间
            shot_time = datetime.datetime.now()

            # 根据 target 类型设置目标，并计算射击的角度
            if isinstance(target, (int, float)):
                # 如果 target 为角度数值，则归一化到 [0,360)
                shot_angle = target % 360
                angle_rad = math.radians(shot_angle)
                direction = (math.cos(angle_rad), math.sin(angle_rad))
                target_point = (
                    shooting_ball.pos[0] + direction[0] * 1000,
                    shooting_ball.pos[1] + direction[1] * 1000
                )
                shooting_ball.set_target(target_point)
            else:
                # 如果 target 为坐标，则根据坐标计算角度
                dx = target[0] - shooting_ball.pos[0]
                dy = target[1] - shooting_ball.pos[1]
                angle_rad = math.atan2(dy, dx)
                shot_angle = math.degrees(angle_rad)
                if shot_angle < 0:
                    shot_angle += 360
                shooting_ball.set_target(target)

            shooting_ball.set_time(shot_time)

            # 计算与上一次射击的时间差（以秒计）
            if self.shot_log:
                time_interval = (shot_time - self.shot_log[-1]["timestamp"]).total_seconds()
            else:
                time_interval = 0

            # 记录此次射击日志（内部记录）
            log_entry = {
                "timestamp": shot_time,
                "time_interval": time_interval,
                "color": shooting_ball.color,
                "angle": shot_angle
            }
            self.shot_log.append(log_entry)
            print(f"记录射击日志 => 时间: {shot_time}, 时间间隔: {time_interval}s, 颜色: {shooting_ball.color}, 角度: {shot_angle}")

            # 将本次射击的数据写入 CSV 文件（写入字段：时间、角度、颜色）
            with open(self.csv_log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([shot_time.strftime("%Y-%m-%d %H:%M:%S.%f"), shot_angle, shooting_ball.color])

            # 发射后进行充能操作
            self.charged_ball = self.recharge()
            self.shooting_balls.append(shooting_ball)

    def recharge(self):
        available_colors = [
            color for color in self.ball_generator.get_available_colors() 
            if color != BLACK
        ] or self.ball_generator.colors
        return ShootingBall(random.choice(available_colors), self.player.get_shoot_pos())

    def draw(self, screen):
        self.charged_ball.draw(screen)
        for ball in self.shooting_balls:
            ball.draw(screen)

    def update(self):
        self.speed = self.bonus_manager.handle_speed_bonus()
        self.charged_ball.update()
        for ball in self.shooting_balls:
            ball.update()
            self.remove_flown_away(ball)
            self.handle_shoot(ball)

    def remove_flown_away(self, ball):
        x = ball.rect.center[0]
        y = ball.rect.center[1]
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            self.shooting_balls.remove(ball)

    def handle_shoot(self, shooting_ball):
        for ball in self.ball_generator.balls:
            if shooting_ball.rect.colliderect(ball.rect):
                if ball.color == BLACK:
                    ball_index = self.ball_generator.balls.index(ball)
                    self.ball_generator.insert(ball_index, shooting_ball)
                    self.shooting_balls.remove(shooting_ball)
                    break
                chain = self.collect_chain(ball, shooting_ball.color)
                if len(chain) > 1:
                    self.explosion_sound.play()
                    self.show_smoke(ball.rect.center)
                    chain += self.check_for_bonus(chain)
                    self.score_manager.add_score(10 * len(chain))
                    self.ball_generator.destroy(chain)
                    if self.charged_ball.color not in self.ball_generator.get_available_colors() and len(self.ball_generator.balls) != 0:
                        self.charged_ball = self.recharge()
                    self.score_manager.last_pop_time = datetime.datetime.now()
                else:
                    ball_index = self.ball_generator.balls.index(ball)
                    self.ball_generator.insert(ball_index, shooting_ball)
                self.shooting_balls.remove(shooting_ball)
                break

    def show_smoke(self, position):
        screen = pygame.display.get_surface()
        smoke_rect = self.smoke_image.get_rect(center=position)
        screen.blit(self.smoke_image, smoke_rect)
        pygame.display.update()
        pygame.time.delay(200)

    def check_for_bonus(self, chain):
        for ball in chain:
            if ball.bonus is not None:
                if ball.bonus is Bonus.Bomb:
                    return self.bonus_manager.handle_bomb_bonus(chain)
                elif ball.bonus is Bonus.Speed:
                    self.speed = True
                    self.bonus_manager.start_bonus(ball.bonus)
                elif ball.bonus is Bonus.InstantWin:
                    self.score_manager.win()
                else:
                    self.bonus_manager.start_bonus(ball.bonus)
        return []

    def collect_chain(self, ball, color):
        if ball.color == BLACK:
            return []
        ball_index = self.ball_generator.balls.index(ball)
        ball_color = ball.color
        left_half = self.collect_half_chain(ball_index - 1, -1, color)
        right_half = self.collect_half_chain(ball_index + 1, 1, color)
        if ball_color == color:
            chain = left_half + [self.ball_generator.balls[ball_index]] + right_half
            chain.sort(key=lambda ball: ball.pos_in_path)
            return chain
        return right_half

    def collect_half_chain(self, i, delta, color):
        half_chain = []
        while len(self.ball_generator.balls) > i >= 0:
            current_ball = self.ball_generator.balls[i]
            if current_ball.color != color:
                break
            half_chain.append(current_ball)
            i += delta
        return half_chain