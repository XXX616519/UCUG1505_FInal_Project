import math
import pygame.gfxdraw
from src.Constants import *
from src.ui import BONUS_IMAGES

class Ball(pygame.sprite.Sprite):
    def __init__(self, color, pos_in_path, path):
        pygame.sprite.Sprite.__init__(self)

        self.color = color

        self.path = path
        self.pos_in_path = float(pos_in_path)

        self.image = pygame.Surface(BALL_SIZE)
        self.pos = self.path.positions[int(self.pos_in_path)]
        self.rect = self.image.get_rect(center=(round(self.pos.x),
                                                round(self.pos.y)))

        self.can_move = True
        self.bonus = None

    def set_bonus(self, bonus):
        self.bonus = bonus

    def set_position(self, pos_in_path):
        self.pos_in_path = pos_in_path
        self.pos = self.path.positions[int(self.pos_in_path)]
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self):
        if self.can_move:
            self.move(1)

    def move(self, steps):
        if self.can_move:
            max_position = float('inf')
            if hasattr(self, 'prev_ball') and self.prev_ball is not None:
                max_position = self.prev_ball.pos_in_path + 20
            self.pos_in_path = min(self.pos_in_path + steps, max_position)
            if self.pos_in_path >= 0:
                new_index = min(int(self.pos_in_path), len(self.path.positions)-1)
                self.pos = pygame.math.Vector2(self.path.positions[new_index])
                self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, screen):
        # 添加渐变和高光
        gradient_rect = pygame.Rect(0, 0, BALL_RADIUS*2, BALL_RADIUS*2)
        gradient = pygame.Surface((BALL_RADIUS*2, BALL_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(gradient, self.color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        # 添加高光
        highlight_pos = (BALL_RADIUS//2, BALL_RADIUS//2)
        pygame.draw.circle(gradient, (255, 255, 255, 120), highlight_pos, BALL_RADIUS//3)
        # 添加描边
        pygame.gfxdraw.aacircle(screen, self.rect.centerx, self.rect.centery, BALL_RADIUS, (30, 30, 30))
        screen.blit(gradient, self.rect)
        
        if self.bonus is not None:
            # 使用get方法安全访问，当颜色不存在时返回None
            bonus_image_path = BONUS_IMAGES.get(self.bonus, {}).get(self.color)
            if bonus_image_path:
                screen.blit(pygame.image.load(bonus_image_path),
                          (self.rect.x, self.rect.y))

    def __eq__(self, other):
        return self.color == other.color and \
               self.rect.center == other.rect.center and \
               self.can_move == other.can_move


class ShootingBall(pygame.sprite.Sprite):
    def __init__(self, color, pos=SCREEN_CENTER):
        pygame.sprite.Sprite.__init__(self)

        self.color = color

        self.image = pygame.Surface(BALL_SIZE)
        self.rect = self.image.get_rect(center=pos)

        self.target = (0, 0)
        self.speed = 15

        self.time = None
        self.trail_positions = []

    def set_time(self, time):
        self.time = time

    def set_target(self, target):
        self.target = (target[0] - self.rect.center[0],
                       target[1] - self.rect.center[1])
        length = math.hypot(*self.target)
        self.target = (self.target[0] / length, self.target[1] / length)

    def update(self):
        self.rect.center = (self.rect.center[0] + self.target[0] * self.speed,
                            self.rect.center[1] + self.target[1] * self.speed)
        self.trail_positions.append(self.rect.center)
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)

    def draw(self, screen):
        # 添加动态拖尾效果
        for i in range(1, len(self.trail_positions)):
            alpha = 255 * (i/len(self.trail_positions))
            pos = self.trail_positions[-i]
            radius = BALL_RADIUS * (1 - i/len(self.trail_positions))
            pygame.draw.circle(screen, self.color + (int(alpha),), pos, int(radius))
        
        # 添加发光效果
        glow = pygame.Surface((BALL_RADIUS*4, BALL_RADIUS*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, self.color + (50,), (BALL_RADIUS*2, BALL_RADIUS*2), BALL_RADIUS*2)
        screen.blit(glow, self.rect.move(-BALL_RADIUS, -BALL_RADIUS).topleft)
        
        # 基础球体绘制
        pygame.draw.circle(screen, self.color, self.rect.center, BALL_RADIUS)


class Finish(pygame.sprite.Sprite):
    def __init__(self, path, balls, score_manager):
        pygame.sprite.Sprite.__init__(self)

        self.balls = balls
        self.score_manager = score_manager

        self.image = pygame.transform.smoothscale(
            pygame.image.load("assets/images/endpoint.png"), (80, 80))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=path.positions[-1])

    def update(self):
        for ball in self.balls:
            if self.rect.colliderect(ball.rect):
                self.score_manager.lose()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
