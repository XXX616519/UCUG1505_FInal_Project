# import cv2
# import mediapipe as mp
# from game.Path import Path
# from game.Sprites import *
# from game.BallGenerator import BallGenerator
# from game.ShootingManager import ShootingManager
# from game.BonusManager import BonusManager
# from game.ScoreManager import ScoreManager
# from game.ui import *


# class Level:
#     def __init__(self, number, score_manager):
        
#         self.number = number
#         self.path = Path(number)
#         self.ball_generator = BallGenerator(self.path, number * 50, score_manager)
#         self.bonus_manager = BonusManager(self.ball_generator)
#         self.player = Player(number)
#         self.finish = Finish(self.path, self.ball_generator.balls, score_manager)
#         self.shooting_manager = ShootingManager(self.ball_generator, self.player.pos, self.bonus_manager, score_manager)


# class Game:
#     def __init__(self):
#         pygame.init()
#         pygame.mixer.init()
#         pygame.display.set_caption("Zuma")

#         print("now")
#         self.cap = cv2.VideoCapture(0)
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
#         self.mp_draw = mp.solutions.drawing_utils
#         self.last_gesture = None

#         self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
#         self.clock = pygame.time.Clock()
#         self.level_num = 1
#         self.score_manager = ScoreManager()
#         self.setup_new_game()
#         self.is_quit = False

#     def play(self):
#         self.continue_game(self.ui_manager.start_game_btn,
#                            self.ui_manager.start_game_display)
#         while not self.is_quit:
#             self.setup_new_game()
#             self.play_game()

#         pygame.quit()

#     def setup_new_game(self):
#         self.level = Level(self.level_num, self.score_manager)
#         self.ui_manager = UiManager(self.screen, self.level)

#     def play_game(self):
#         game_finished = False

#         while not game_finished and not self.is_quit:
#             self.level.ball_generator.generate()

#             self.clock.tick(FPS)

#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.is_quit = True
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     self.level.shooting_manager.shoot(pygame.mouse.get_pos())

#             self.update_sprites()
#             self.update_display(self.ui_manager.game_display)

#             if self.score_manager.is_win:
#                 game_finished = True
#                 self.handle_win()
#             elif self.score_manager.is_lose:
#                 game_finished = True
#                 self.handle_lose()

#     def handle_win(self):
#         if self.level_num == 3:
#             self.win_game()
#         else:
#             self.continue_game(self.ui_manager.continue_btn,
#                                self.ui_manager.win_level_display)
#             self.level_num += 1
#             self.score_manager.setup_next_level()

#     def handle_lose(self):
#         self.score_manager.take_live()
#         if self.score_manager.lose_game:
#             self.continue_game(self.ui_manager.new_game_button,
#                                self.ui_manager.lose_game_display)
#             self.level_num = 1
#             self.score_manager = ScoreManager()
#         else:
#             self.continue_game(self.ui_manager.start_level_again_btn,
#                                self.ui_manager.lose_level_display)
#             self.score_manager.setup_next_level()

#     def continue_game(self, button, window):
#         game_continued = False
#         while not game_continued and not self.is_quit:
#             mouse = pygame.mouse.get_pos()
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.is_quit = True
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if button.rect.collidepoint(mouse):
#                         game_continued = True
#             self.update_display(window)

#     def win_game(self):
#         on_win_window = True
#         while on_win_window and not self.is_quit:
#             mouse = pygame.mouse.get_pos()
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.is_quit = True
#                 elif event.type == pygame.MOUSEBUTTONDOWN:
#                     if self.ui_manager.start_game_again_btn.rect.collidepoint(mouse):
#                         on_win_window = False
#                         self.level_num = 1
#                     elif self.ui_manager.finish_btn.rect.collidepoint(mouse):
#                         self.is_quit = True

#             self.update_display(self.ui_manager.win_game_display)

#     def update_sprites(self):
#         self.level.player.update()
#         self.level.shooting_manager.update()
#         self.level.ball_generator.update()
#         self.level.bonus_manager.update()
#         self.level.finish.update()

#     def update_display(self, display):
#         self.ui_manager.draw_window(display)
#         if display is self.ui_manager.game_display:
#             self.ui_manager.show_score(self.score_manager.score)
#             self.ui_manager.show_lives(self.score_manager.lives)
#         pygame.display.update()


# if __name__ == '__main__':
#     game = Game()
#     game.play()


import cv2
import mediapipe as mp
import pygame
from game.Path import Path
from game.Sprites import *
from game.BallGenerator import BallGenerator
from game.ShootingManager import ShootingManager
from game.BonusManager import BonusManager
from game.ScoreManager import ScoreManager
from game.ui import *

class Level:
    def __init__(self, number, score_manager):
        self.number = number
        self.path = Path(number)
        self.ball_generator = BallGenerator(self.path, number * 50, score_manager)
        self.bonus_manager = BonusManager(self.ball_generator)
        self.player = Player(number)
        self.finish = Finish(self.path, self.ball_generator.balls, score_manager)
        self.shooting_manager = ShootingManager(self.ball_generator, self.player.pos, self.bonus_manager, score_manager)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Zuma")

        # 初始化摄像头和mediapipe手部检测
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

        self.prev_fist = False  # 记录上一帧是否握拳，用于检测握拳切换事件

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.level_num = 1
        self.score_manager = ScoreManager()
        self.setup_new_game()
        self.is_quit = False

    def play(self):
        self.continue_game(self.ui_manager.start_game_btn,
                           self.ui_manager.start_game_display)
        while not self.is_quit:
            self.setup_new_game()
            self.play_game()

        # 释放摄像头资源
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()

    def setup_new_game(self):
        self.level = Level(self.level_num, self.score_manager)
        self.ui_manager = UiManager(self.screen, self.level)

    def play_game(self):
        game_finished = False

        while not game_finished and not self.is_quit:
            self.level.ball_generator.generate()

            self.clock.tick(FPS)

            # 处理摄像头手势输入
            self.process_gesture_input()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.level.shooting_manager.shoot(pygame.mouse.get_pos())

            self.update_sprites()
            self.update_display(self.ui_manager.game_display)

            if self.score_manager.is_win:
                game_finished = True
                self.handle_win()
            elif self.score_manager.is_lose:
                game_finished = True
                self.handle_lose()

    def process_gesture_input(self):
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.flip(img, 1)  # 镜像翻转，方便控制
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # 只用第一只手
            self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # 计算手掌中心点x坐标（归一化0~1）
            x_coords = [lm.x for lm in hand_landmarks.landmark]
            y_coords = [lm.y for lm in hand_landmarks.landmark]

            cx = sum(x_coords) / len(x_coords)
            cy = sum(y_coords) / len(y_coords)

            # 判断是否握拳和是否五指并拢
            # 简单方法：计算各指尖与对应指根的距离，距离小则是握拳，距离大则是张开
            # 指尖和对应指根索引（mediapipe手部关键点）：
            # 0: wrist
            # 指尖：8(食指), 12(中指), 16(无名指), 20(小指)
            # 指根：5(食指基部), 9(中指基部), 13(无名指基部), 17(小指基部)
            finger_tips = [8, 12, 16, 20]
            finger_dips = [6, 10, 14, 18]  # 中间关节，可以更准确判断弯曲

            # 计算每个手指尖到对应指根的距离（归一化）
            finger_folded = []
            for tip, dip in zip(finger_tips, finger_dips):
                tip_pos = hand_landmarks.landmark[tip]
                dip_pos = hand_landmarks.landmark[dip]
                dist = ((tip_pos.x - dip_pos.x)**2 + (tip_pos.y - dip_pos.y)**2)**0.5
                # 距离阈值调试用，距离小于阈值视为弯曲
                finger_folded.append(dist < 0.05)

            # 拇指判断
            # 拇指尖4和拇指根2的距离
            thumb_tip = hand_landmarks.landmark[4]
            thumb_mcp = hand_landmarks.landmark[2]
            thumb_dist = ((thumb_tip.x - thumb_mcp.x)**2 + (thumb_tip.y - thumb_mcp.y)**2)**0.5
            thumb_folded = thumb_dist < 0.05

            # 握拳条件：大部分手指都弯曲
            is_fist = finger_folded.count(True) >= 3 and thumb_folded

            # 五指并拢条件：手指尖之间距离都很小（简单判断）
            # 计算食指尖8和小指尖20距离
            tip8 = hand_landmarks.landmark[8]
            tip20 = hand_landmarks.landmark[20]
            fingers_close = ((tip8.x - tip20.x)**2 + (tip8.y - tip20.y)**2)**0.5 < 0.1

            # 控制祖玛旋转：
            # 仅当五指并拢时，映射x坐标到0~360度角度
            if fingers_close and not is_fist:
                angle = int(cx * 360)  # 屏幕左边x=0 => 0度，右边x=1 => 360度
                self.level.player.set_angle(angle)
                self.prev_fist = False  # 重置握拳状态防止误触发发射

            # 握拳触发发射，只在握拳状态切换时触发
            if is_fist and not self.prev_fist:
                # 触发发射，方向用当前玩家角度计算发射位置
                # 这里简单用玩家当前角度作为方向
                self.level.shooting_manager.shoot_by_angle(self.level.player.angle)
                self.prev_fist = True

            if not is_fist:
                self.prev_fist = False

        # 可选：显示摄像头窗口，便于调试
        # cv2.imshow("Hand Gesture", img)
        # cv2.waitKey(1)

    # 下面的函数保持不变
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
            self.score_manager = ScoreManager()
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

if __name__ == '__main__':
    game = Game()
    game.play()