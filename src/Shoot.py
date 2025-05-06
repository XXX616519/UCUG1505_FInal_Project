from src.Sprites import ShootingBall
from src.Constants import * 
from src.Special_Ball import Bonus
import random
import datetime


class Shoot:
    def __init__(self, ball_generator, pos, bonus_manager, score_manager):
        self.ball_generator = ball_generator
        self.bonus_manager = bonus_manager
        self.score_manager = score_manager

        self.pos = pos
        self.charged_ball = ShootingBall(random.choice(
            self.ball_generator.colors), self.pos)

        self.shooting_balls = []

        self.combo_chain = []

        self.speed = False

        # 加载声音和图片
        self.explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
        self.smoke_image = pygame.image.load("assets/images/smoke.png")

    def shoot(self, target):
        if len(self.shooting_balls) == 0 or self.speed or \
                (datetime.datetime.now() -
                 self.shooting_balls[-1].time).microseconds > 300000:
            shooting_ball = self.charged_ball
            shooting_ball.set_target(target)
            shooting_ball.set_time(datetime.datetime.now())
            self.charged_ball = self.recharge()
            self.shooting_balls.append(shooting_ball)

    def recharge(self):
        # 过滤掉黑色，同时保留原始颜色选项
        available_colors = [
            color for color in self.ball_generator.get_available_colors() 
            if color != BLACK
        ] or self.ball_generator.colors  # 当场上只有黑球时使用原始颜色
        return ShootingBall(random.choice(available_colors), self.pos)

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
                if ball.color == BLACK:  # 黑球不可消除
                    ball_index = self.ball_generator.balls.index(ball)
                    self.ball_generator.insert(ball_index, shooting_ball)
                    self.shooting_balls.remove(shooting_ball)
                    break
                chain = self.collect_chain(ball, shooting_ball.color)
                if len(chain) > 1:  # 符合条件的撞击（球链长度大于 1）
                    # 播放爆炸声音
                    self.explosion_sound.play()

                    # 显示烟雾图片
                    self.show_smoke(ball.rect.center)

                    # 处理球链消除
                    chain += self.check_for_bonus(chain)
                    self.score_manager.add_score(10 * len(chain))
                    self.ball_generator.destroy(chain)

                    # 重新充能
                    if self.charged_ball.color not in \
                            self.ball_generator.get_available_colors() and \
                            len(self.ball_generator.balls) != 0:
                        self.charged_ball = self.recharge()

                    # 消除时重置计时
                    self.score_manager.last_pop_time = datetime.datetime.now()
                else:
                    # 如果球链长度小于等于 1，则插入射击球
                    ball_index = self.ball_generator.balls.index(ball)
                    self.ball_generator.insert(ball_index, shooting_ball)

                # 移除射出的球
                self.shooting_balls.remove(shooting_ball)
                break

    def show_smoke(self, position):
        """在指定位置显示烟雾图片"""
        screen = pygame.display.get_surface()  # 获取当前屏幕
        smoke_rect = self.smoke_image.get_rect(center=position)
        screen.blit(self.smoke_image, smoke_rect)
        pygame.display.update()

        # 延迟一段时间以显示烟雾效果
        pygame.time.delay(200)  # 延迟 200 毫秒

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
        if ball.color == BLACK:  # 排除黑球
            return []
        ball_index = self.ball_generator.balls.index(ball)
        ball_color = ball.color

        left_half = self.collect_half_chain(ball_index - 1, -1,
                                            color)
        right_half = self.collect_half_chain(ball_index + 1, 1,
                                             color)

        if ball_color == color:
            chain = left_half + [self.ball_generator.balls[ball_index]] + \
                    right_half
            chain.sort(key=lambda ball: ball.pos_in_path)

            return chain

        return right_half

    def collect_half_chain(self, i, delta, color):
        half_chain = []
        while len(self.ball_generator.balls) > i >= 0:
            current_ball = self.ball_generator.balls[i]
            # 遇到不同颜色（包括黑色）时停止收集
            if current_ball.color != color:
                break
            half_chain.append(current_ball)
            i += delta
        return half_chain

