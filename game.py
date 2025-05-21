import pygame
import cv2
import mediapipe as mp
import os
import shutil
import time
from vosk import Model, KaldiRecognizer
import pyaudio
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
from win_animation.simulation import Simulation


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


def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return

    # 遍历文件夹中的所有文件和子文件夹
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除子文件夹及其中的所有内容
        except Exception as e:
            print(f"删除 {file_path} 失败: {e}")


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
        self.voice_model = Model("D:/PDF/UCUG1505_FInal_Project/model/vosk-model-small-en-us-0.15")  # 确保下载并解压 vosk 模型到 "model" 文件夹
        self.recognizer = KaldiRecognizer(self.voice_model, 16000)
        self.audio_stream = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        self.audio_stream.start_stream()
        self.control_mode = None  # 控制模式："mouse", "gesture", "voice"
        self.voice_angle = 0  # 语音控制当前角度
        # self.keyboard_target_angle = 0  # 键盘控制当前角度

    def get_gesture_shoot_target(self):
        """
        读取摄像头并检测手势
        返回值为一个元组 (旋转角度, 是否握拳)
        """
        ret, frame = cap.read()
        if not ret:
            print("Can't read from the camera")
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
            rotation_angle = int((current_x / WIDTH) * 360)
            rotation_angle = max(0, min(360, rotation_angle))

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

    def listen_for_voice_command(self):
        """
        使用 vosk 捕获用户命令。
        """
        try:
            data = self.audio_stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                self.voice_command = eval(result).get("text", "").lower()
                print(f"Recognized command: {self.voice_command}")
            else:
                self.voice_command = None
        except Exception as e:
            print(f"Error during voice recognition: {e}")
            self.voice_command = None

    def play(self):
        self.show_start_menu()
        while not self.is_quit:
            self.setup_new_game()
            self.play_game()
        pygame.quit()

    def setup_new_game(self):
        self.level = Level(self.level_num, self.score_manager)
        self.ui_manager = UiManager(self.screen, self.level)
        self.voice_angle = self.level.player.angle  # 重置语音角度为初始角度
        # 保留已选择的控制模式，不重置

    def show_start_menu(self):
        """显示开始菜单，选择控制模式"""
        start_menu_active = True
        while start_menu_active and not self.is_quit:
            self.screen.fill((0, 0, 0))
            self.ui_manager.draw_start_menu_buttons()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.ui_manager.mouse_control_btn.collidepoint(mouse_pos):
                        self.control_mode = "mouse"
                        start_menu_active = False
                    elif self.ui_manager.gesture_control_btn.collidepoint(mouse_pos):
                        self.control_mode = "gesture"
                        start_menu_active = False
                    elif self.ui_manager.voice_control_btn.collidepoint(mouse_pos):
                        self.control_mode = "voice"
                        start_menu_active = False
                    elif self.ui_manager.keyboard_control_btn.collidepoint(mouse_pos):
                        self.control_mode = "keyboard"
                        start_menu_active = False

    def play_game(self):
        game_finished = False

        while not game_finished and not self.is_quit:
            # 处理键盘控制初始设置
            if self.control_mode == "keyboard":
                # 切换到键盘控制，保持当前角度
                self.level.player.set_keyboard_angle(self.level.player.get_current_angle())

            # 确保在不同控制模式下正确设置玩家控制标志
            if self.control_mode == "mouse":
                self.level.player.set_mouse_control()
            elif self.control_mode == "gesture":
                # 始终启用手势控制，禁用鼠标控制
                self.level.player.use_gesture_control = True
            elif self.control_mode == "voice":
                # 语音模式也禁用鼠标控制
                self.level.player.use_gesture_control = True

            self.level.ball_generator.generate()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_quit = True
                # 键盘事件处理
                elif event.type == pygame.KEYDOWN and self.control_mode == "keyboard":
                    if event.key == pygame.K_a:
                        new_angle = (self.level.player.get_current_angle() - 20) % 360
                        self.level.player.set_keyboard_angle(new_angle)
                    elif event.key == pygame.K_d:
                        new_angle = (self.level.player.get_current_angle() + 20) % 360
                        self.level.player.set_keyboard_angle(new_angle)
                    elif event.key == pygame.K_SPACE:
                        angle = self.level.player.get_current_angle()
                        self.level.shooting_manager.shoot(angle)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # 一直允许点击暂停、重启和切换模式按钮
                    if self.ui_manager.pause_btn.rect.collidepoint(mouse_pos):
                        self.is_paused = not self.is_paused
                    elif self.ui_manager.restart_btn.rect.collidepoint(mouse_pos):
                        self.setup_new_game()
                        self.score_manager.setup_next_level()
                    elif self.ui_manager.change_mode_btn.rect.collidepoint(mouse_pos):
                        # 弹出控制模式选择菜单，保持当前关卡
                        self.show_start_menu()
                    else:
                        # 仅在鼠标模式下允许射击
                        if self.control_mode == "mouse":
                            self.level.shooting_manager.shoot(mouse_pos)

            if not self.is_paused:
                if self.control_mode == "mouse":
                    self.level.player.set_mouse_control()
                    angle_to_update = None

                elif self.control_mode == "gesture":
                    gesture = self.get_gesture_shoot_target()
                    if gesture:
                        angle, is_fist = gesture
                        angle = (angle + 90) % 360
                        self.level.player.set_gesture_angle(angle)
                        if is_fist:
                            self.level.shooting_manager.shoot(angle)
                    angle_to_update = angle if gesture else None

                elif self.control_mode == "voice":
                    self.listen_for_voice_command()
                    angle = self.level.player.get_current_angle()
                    if self.voice_command == "left":
                        angle = (angle - 20) % 360
                        self.level.player.set_voice_angle(angle - 90)
                    elif self.voice_command == "right":
                        angle = (angle + 20) % 360
                        self.level.player.set_voice_angle(angle - 90)
                    elif self.voice_command == "shoot":
                        self.level.shooting_manager.shoot(angle - 90)
                    # 未识别 left/right/shoot 时，不改变 angle
                    self.voice_command = None
                    angle_to_update = self.level.player.get_current_angle()

                elif self.control_mode == "keyboard":
                    # 键盘模式下使用已有角度，无需额外操作
                    angle_to_update = None

                else:
                    angle_to_update = None

                # 更新精灵状态
                self.update_sprites(angle_to_update)

            self.update_display(self.ui_manager.game_display)

            if self.score_manager.is_win:
                game_finished = True
                self.handle_win()
            elif self.score_manager.is_lose:
                game_finished = True
                self.handle_lose()


    def handle_win(self):
        Simulation().run()
        if self.level_num == 3:
            self.win_game()
            folder_to_clear = "lucky"  # 你要清空的文件夹
            clear_folder(folder_to_clear)
            print(f"ALL CLEANED: {folder_to_clear}")

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
        # 在 update_sprites 方法中添加对 None 值的检查，避免将 None 传递给 Player.update 方法
        if angle is not None:
            self.level.player.update(angle)
        else:
            self.level.player.update(0)  # 默认角度为 0
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