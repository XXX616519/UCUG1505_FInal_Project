from src.Sprites import ShootingBall
from src.Constants import * 
from src.Special_Ball import Bonus
import random
import datetime
import speech_recognition as sr
import math


# class Player(pygame.sprite.Sprite):
#     def __init__(self, level):
#         pygame.sprite.Sprite.__init__(self)

#         if level == 1:
#             self.pos = (530, 330)
#         else:
#             self.pos = SCREEN_CENTER

#         self.original_image = pygame.transform.smoothscale(
#             pygame.image.load('assets/images/player.png'), PLAYER_SIZE)
#         self.original_image.set_colorkey(BLACK)

#         self.image = self.original_image

#         self.rect = self.image.get_rect(center=self.pos)

#         self.angle = 0

#     def update(self):
#         mouse_x, mouse_y = pygame.mouse.get_pos()
#         rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
#         self.angle = (180 / math.pi) * (-math.atan2(rel_y, rel_x)) + 90
#         self.image = pygame.transform.rotate(self.original_image, self.angle)
#         self.image.set_colorkey(BLACK)
#         self.rect = self.image.get_rect(center=self.rect.center)

#     def draw(self, screen):
#         screen.blit(self.image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.voice_recognizer = sr.Recognizer()
        self.last_voice_time = 0
        self.voice_cooldown = 1.0  # 1秒冷却时间


        if level == 1:
            self.pos = (530, 330)
        else:
            self.pos = SCREEN_CENTER

        # 加载原始图像
        self.original_image = pygame.transform.smoothscale(
            pygame.image.load('assets/images/player.png'), PLAYER_SIZE)
        self.original_image.set_colorkey(BLACK)
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)
        
        # 旋转控制
        self.angle = 0
        self.use_gesture_control = False  # 默认使用鼠标控制
        self.gesture_target_angle = 0  # 手势控制的目标角度
        
        # 射击方向
        self.shoot_direction = [1, 0]  # 默认向右

    def update(self):
        if not self.use_gesture_control:
            # 鼠标控制模式
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
            self.angle = (180 / math.pi) * (-math.atan2(rel_y, rel_x)) + 90
        else:
            # 手势控制模式
            self.angle = self.gesture_target_angle
        
        # 更新图像旋转
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)
        
        # 计算射击方向
        angle_rad = math.radians(self.angle)
        self.shoot_direction = [math.cos(angle_rad), math.sin(angle_rad)]

    def set_gesture_angle(self, angle):
        """设置手势控制的角度"""
        self.use_gesture_control = True
        self.gesture_target_angle = angle

    def set_mouse_control(self):
        """切换回鼠标控制"""
        self.use_gesture_control = False

    def get_shoot_pos(self):
        """获取射击起始位置(稍微靠前一些)"""
        offset = 30  # 从玩家中心向前偏移的距离
        return (
            self.pos[0] + self.shoot_direction[0] * offset,
            self.pos[1] + self.shoot_direction[1] * offset
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)