import pygame
import math
import time
import speech_recognition as sr
from src.Constants import *
from src.Sprites import ShootingBall


class Player(pygame.sprite.Sprite):
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.voice_recognizer = sr.Recognizer()
        self.recognizer = sr.Recognizer()
        self.last_voice_time = 0
        self.voice_cooldown = 0.1  # 冷却时间
        self.microphone = sr.Microphone()

        # if level == 1:
        self.pos = (530, 330)
        # else:
        #     self.pos = SCREEN_CENTER

        # 加载原始图像
        self.original_image = pygame.transform.smoothscale(
            pygame.image.load('assets/images/player.png'), PLAYER_SIZE)
        self.original_image.set_colorkey(BLACK)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.pos)

        # 旋转控制
        self.angle = 0
        self.use_gesture_control = False  # 默认使用鼠标控制
        self.use_voice_control = False  # 默认未启用语音控制
        self.use_keyboard_control = False
        self.keyboard_target_angle = self.angle
        # 添加缺失的 gesture_target_angle 初始化
        self.gesture_target_angle = 0

        # 射击方向
        self.shoot_direction = [1, 0]  # 默认向右

    def listen_for_shoot(self, allowed_commands=["shoot", "hello", "end"]):
        """
        监听语音命令，触发射击动作。
        """
        current_time = time.time()
        if current_time - self.last_voice_time < self.voice_cooldown:
            return False

        try:
            with self.microphone as source:
                print("Listening for voice command...")
                audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=2)
            try:
                command = self.voice_recognizer.recognize_google(audio, language="en-US").lower()
                print("Recognized command:", command)
                for valid_cmd in allowed_commands:
                    if valid_cmd in command:
                        self.last_voice_time = current_time
                        return True
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Microphone error: {e}")

        return False

    def update(self, passangle):
        if self.use_keyboard_control:
            # 键盘控制模式：直接使用键盘目标角度
            self.angle = (self.keyboard_target_angle) % 360   # 补偿旋转偏移
        elif self.use_voice_control:
            # 语音控制模式：使用语音目标角度并进行与手势一致的贴图补偿
            self.angle = (self.voice_target_angle + 90) % 360
        elif self.use_gesture_control:
            # 手势控制模式直接使用传入角度（已包含补偿）
            self.angle = (self.gesture_target_angle + 90) % 360
        else:
            # 鼠标控制模式（保持原有逻辑）
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x = mouse_x - self.rect.centerx
            rel_y = mouse_y - self.rect.centery
            raw_angle = math.degrees(math.atan2(-rel_y, rel_x)) % 360
            self.angle = (raw_angle + 90) % 360  # 补偿旋转偏移
        # 统一方向向量计算（保持原有逻辑）
        angle_rad = math.radians(self.angle - 90)  # 修正角度偏移
        self.shoot_direction = (math.cos(angle_rad), -math.sin(angle_rad))

        if self.use_keyboard_control:
            angle_rad = math.radians(self.angle)  # 修正角度偏移
            self.shoot_direction = (-math.cos(angle_rad), math.sin(angle_rad))

        # 更新图像旋转
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=self.pos)

    def set_gesture_angle(self, angle):
        """切换到手势控制并设置角度"""
        self.use_voice_control = False
        self.use_gesture_control = True
        self.gesture_target_angle = angle

    def set_mouse_control(self):
        """切换回鼠标控制"""
        self.use_voice_control = False
        self.use_gesture_control = False
        # 键盘控制关闭
        self.use_keyboard_control = False

    def set_voice_angle(self, angle):
        """切换到语音控制并设置角度"""
        self.use_gesture_control = False
        self.use_voice_control = True
        self.voice_target_angle = angle
        # 键盘控制关闭
        self.use_keyboard_control = False

    def set_keyboard_angle(self, angle):
        """切换到键盘控制并设置角度"""
        self.use_keyboard_control = True
        self.use_voice_control = False
        self.use_gesture_control = False
        self.keyboard_target_angle = angle 

    def get_shoot_pos(self):
        """获取射击起始位置(略微靠前)"""
        offset = 0  # 偏移距离
        return (
            self.pos[0] + self.shoot_direction[0] * offset,
            self.pos[1] + self.shoot_direction[1] * offset
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_current_angle(self):
        """获取当前玩家的角度"""
        return self.angle