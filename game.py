import pygame
import cv2
import mediapipe as mp
import speech_recognition as sr
import time
from src.Path import Path
from src.Sprites import *
from src.Generate_Ball import Generate_Ball
from src.Shoot import Shoot
from src.Special_Ball import Special_Ball
from src.Score import Score
from src.ui.ui_gen import UiManager
from src.ui import *
from src.Level import Level


# initialize the camera
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Zuma")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.level_num = 1
        self.score_manager = Score()
        self.setup_new_game()
        self.is_quit = False
        self.is_paused = False

    # def get_gesture_shoot_target(self):
    #     ret, frame = cap.read()
    #     if not ret:
    #         return None

    #     # 初始化返回值（默认无手势）
    #     gesture_result = None

    #     # 转换颜色空间并镜像
    #     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     image = cv2.flip(image, 1)
    #     results = hands.process(image)

    #     if results.multi_hand_landmarks:
    #         # 取第一个检测到的手
    #         hand_landmarks = results.multi_hand_landmarks[0]
    #         h, w, _ = image.shape

    #         # 使用手腕基部（Landmark 0）作为手掌位置
    #         wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    #         current_x = int(wrist.x * WIDTH)  # 映射到 Pygame 窗口宽度
    #         current_y = int(wrist.y * HEIGHT)  # 映射到 Pygame 窗口高度

    #         # 判断是否为滑动动作
    #         if not hasattr(self, 'slide_start_x'):
    #             # 初始化滑动起始位置（第一次检测到手掌时记录）
    #             self.slide_start_x = current_x
    #             self.slide_start_time = time.time()
    #         else:
    #             # 计算滑动距离和方向
    #             delta_x = current_x - self.slide_start_x
    #             elapsed_time = time.time() - self.slide_start_time

    #             # 修改点1：调整滑动触发条件（降低阈值）
    #             if (
    #                 abs(delta_x) > WIDTH * 0.2 and  # 原0.5 → 0.2
    #                 elapsed_time < 1.0 and           # 原0.5 → 1.0
    #                 abs(current_y - int(wrist.y * HEIGHT)) < HEIGHT * 0.3  # 原0.2 → 0.3
    #             ):
    #                 # 判断方向：左到右为正方向
    #                 if delta_x > 0:
    #                     gesture_result = "rotate_360_clockwise"  # 顺时针旋转
    #                 else:
    #                     gesture_result = "rotate_360_counterclockwise"  # 逆时针旋转
                    
    #                 # 重置滑动检测
    #                 del self.slide_start_x
    #                 del self.slide_start_time

    #         return gesture_result
    #     else:
    #         # 未检测到手时清除滑动状态
    #         if hasattr(self, 'slide_start_x'):
    #             del self.slide_start_x
    #             del self.slide_start_time
    #         return None

    def get_gesture_shoot_target(self):
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            return None

        # 转换颜色空间并镜像
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            # 取第一个检测到的手
            hand_landmarks = results.multi_hand_landmarks[0]
            h, w, _ = image.shape

            # 使用手腕基部（Landmark 0）作为手掌位置
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_x = int(wrist.x * WIDTH)  # 映射到Pygame窗口宽度
            current_y = int(wrist.y * HEIGHT)  # 映射到Pygame窗口高度
            
            # 打印手掌位置坐标
            # print(f"手掌位置: X={current_x}, Y={current_y}")

            # 计算旋转角度（0-360度）
            rotation_angle = int((current_x / WIDTH) * 360)
            rotation_angle = max(0, min(360, rotation_angle))
            
            # print(f"计算得到的旋转角度: {rotation_angle}度")
            
            return rotation_angle
        else:
            print("未检测到手部")
            return None


    def play(self):
        self.continue_game(self.ui_manager.start_game_btn,
                           self.ui_manager.start_game_display)
        while not self.is_quit:
            self.setup_new_game()
            self.play_game()

        pygame.quit()

    def setup_new_game(self):
        self.level = Level(self.level_num, self.score_manager)
        self.ui_manager = UiManager(self.screen, self.level)

    # def play_game(self):
    #     game_finished = False

    #     while not game_finished and not self.is_quit:
    #         self.level.ball_generator.generate()

    #         self.clock.tick(FPS)

    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 self.is_quit = True
    #             elif event.type == pygame.MOUSEBUTTONDOWN:
    #                 mouse_pos = pygame.mouse.get_pos()
    #                 if self.ui_manager.pause_btn.rect.collidepoint(mouse_pos):
    #                     self.is_paused = not self.is_paused
    #                 elif self.ui_manager.restart_btn.rect.collidepoint(mouse_pos):
    #                     self.setup_new_game()
    #                     self.score_manager.setup_next_level()
    #                 else:
    #                     self.level.shooting_manager.shoot(mouse_pos)

    #         # 如果没有暂停，则处理手势输入
    #         if not self.is_paused:
    #             gesture_target = self.get_gesture_shoot_target()
    #             if gesture_target:
    #                 # 调用射击管理器发射函数，传入手势确定的目标方向
    #                 self.level.shooting_manager.shoot(gesture_target)
    #             self.update_sprites()

    #         self.update_display(self.ui_manager.game_display)

    #         if self.score_manager.is_win:
    #             game_finished = True
    #             self.handle_win()
    #         elif self.score_manager.is_lose:
    #             game_finished = True
    #             self.handle_lose()

    def play_game(self):
        game_finished = False

        while not game_finished and not self.is_quit:
            self.level.ball_generator.generate()
            self.clock.tick(FPS)
            # 语音检测
            # voice_shoot = False
            # if not self.is_paused:
            #     voice_shoot = self.level.player.listen_for_shoot()
            voice_shoot = False
            if not self.is_paused:
                try:
                    voice_shoot = self.level.player.listen_for_shoot()
                except Exception as e:
                    print(f"Voice recognition error: {e}")
                    voice_shoot = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.ui_manager.pause_btn.rect.collidepoint(mouse_pos):
                        self.is_paused = not self.is_paused
                    elif self.ui_manager.restart_btn.rect.collidepoint(mouse_pos):
                        self.setup_new_game()
                        self.score_manager.setup_next_level()
                    # else:
                    #     self.level.shooting_manager.shoot(mouse_pos)

            # if not self.is_paused:
            #     target_angle = self.get_gesture_shoot_target()
            #     if target_angle is not None:
            #         print(f"设置玩家旋转角度: {target_angle}")
            #         self.level.player.rotate_angle = target_angle
            #         # 强制调用玩家更新
            #         self.level.player.update()
                
            #     self.update_sprites()

            # if not self.is_paused:
            #     # 手势控制
            #     target_angle = self.get_gesture_shoot_target()
            #     if target_angle is not None:
            #         self.level.player.set_gesture_angle(target_angle)
            #         # 自动射击
            #         self.level.shooting_manager.shoot(target_angle)
            #     else:
            #         self.level.player.set_mouse_control()
                
            #     self.update_sprites()

            # self.update_display(self.ui_manager.game_display)

            
            if not self.is_paused:
                target_angle = self.get_gesture_shoot_target()
                if target_angle is not None:
                    self.level.player.set_gesture_angle(target_angle)
                    # 语音触发射击
                    if voice_shoot:
                        self.level.shooting_manager.shoot(target_angle)
                else:
                    self.level.player.set_mouse_control()
                
                self.update_sprites()

            self.update_display(self.ui_manager.game_display)

            if self.score_manager.is_win:
                game_finished = True
                self.handle_win()
            elif self.score_manager.is_lose:
                game_finished = True
                self.handle_lose()

    def handle_win(self):
        if self.level_num == 3:
            self.win_game()
        else:
            self.continue_game(self.ui_manager.continue_btn,
                               self.ui_manager.win_level_display)
            self.level_num += 1
            self.score_manager.setup_next_level()

    def handle_lose(self):
        self.score_manager.take_live()
        if self.score_manager.lose_game:
            self.continue_game(self.ui_manager.new_game_button,
                               self.ui_manager.lose_game_display)
            self.level_num = 1
            self.score_manager = Score()
        else:
            self.continue_game(self.ui_manager.start_level_again_btn,
                               self.ui_manager.lose_level_display)
            self.score_manager.setup_next_level()

    def continue_game(self, button, window):
        game_continued = False
        while not game_continued and not self.is_quit:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button.rect.collidepoint(mouse):
                        game_continued = True
            self.update_display(window)

    def win_game(self):
        on_win_window = True
        while on_win_window and not self.is_quit:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ui_manager.start_game_again_btn.rect.collidepoint(mouse):
                        on_win_window = False
                        self.level_num = 1
                    elif self.ui_manager.finish_btn.rect.collidepoint(mouse):
                        self.is_quit = True

            self.update_display(self.ui_manager.win_game_display)

    def update_sprites(self):
        self.level.player.update()
        self.level.shooting_manager.update()
        self.level.ball_generator.update()
        self.level.bonus_manager.update()
        self.level.finish.update()

    def update_display(self, display):
        self.ui_manager.draw_window(display)
        if display is self.ui_manager.game_display:
            self.ui_manager.show_score(self.score_manager.score)
            self.ui_manager.show_lives(self.score_manager.lives)
        pygame.display.update()