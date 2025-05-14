import pygame
import cv2
import mediapipe as mp
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
from src.Constants import WIDTH, HEIGHT, FPS, SCREEN_CENTER

# 初始化摄像头
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

    def get_gesture_shoot_target(self):
        """
        读取摄像头并检测手势
        返回值为一个元组 (旋转角度, 是否握拳)
        """
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            return None

        # 转换颜色空间并镜像
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        results = hands.process(image)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            # h, w, _ = image.shape

            # 使用手腕作为参考点
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_x = int(wrist.x * WIDTH)
            # current_y = int(wrist.y * HEIGHT)

            # 根据手腕横坐标计算旋转角度（0-360 度）
            rotation_angle = int((current_x / WIDTH) * 720)
            rotation_angle = max(0, min(720, rotation_angle))

            # 判断是否为握拳（除了拇指之外，其他四指的指尖与手腕的距离是否都较小）
            def distance(a, b):
                return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5

            index_dist = distance(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP], wrist)
            middle_dist = distance(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP], wrist)
            ring_dist = distance(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP], wrist)
            pinky_dist = distance(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP], wrist)
            
            # 根据经验设置阈值（归一化坐标中，一般阈值设置为 0.1）
            fist_threshold = 0.2
            is_fist = (index_dist < fist_threshold and 
                       middle_dist < fist_threshold and 
                       ring_dist < fist_threshold and 
                       pinky_dist < fist_threshold)
            #print(rotation_angle)
            return (rotation_angle, is_fist)
        
        else:
            #print("未检测到手部")
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

    def play_game(self):
        game_finished = False

        while not game_finished and not self.is_quit:
            self.level.ball_generator.generate()
            self.clock.tick(FPS)
            
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
                    else:
                        self.level.shooting_manager.shoot(mouse_pos)

            if not self.is_paused:
                gesture = self.get_gesture_shoot_target()
                angle=0
                if gesture:
                    angle, is_fist = gesture
                    # 更新玩家旋转角度
                    self.level.player.set_gesture_angle(angle)
                    # 当检测到握拳时立即触发射击动作
                    if is_fist:
                        if angle>360:
                            angle %= 360
                        #self.update_sprites(angle)
                        print("检测到握拳，发射小球= ",angle)
                        self.level.shooting_manager.shoot(angle)
                else :
                    self.level.player.set_mouse_control()

                if angle>360:
                    angle%=360
                self.update_sprites(angle)

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

    def update_sprites(self,angle):
        self.level.player.update(angle)
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