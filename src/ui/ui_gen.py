from src.Constants import *
from src.Special_Ball import Bonus
from src.ui.button import Button
import random

BONUS_IMAGES = {
    Bonus.Pause: {
        YELLOW: 'assets/images/pause_yellow.png',
        GREEN: 'assets/images/pause_green.png',
        BLUE: 'assets/images/pause_blue.png',
        RED: 'assets/images/pause_red.png',
    },
    Bonus.Reverse: {
        YELLOW: 'assets/images/reverse_yellow.png',
        GREEN: 'assets/images/reverse_green.png',
        BLUE: 'assets/images/reverse_blue.png',
        RED: 'assets/images/reverse_red.png',
    },
    Bonus.Bomb: {
        YELLOW: 'assets/images/bomb_yellow.png',
        GREEN: 'assets/images/bomb_green.png',
        BLUE: 'assets/images/bomb_blue.png',
        RED: 'assets/images/bomb_red.png',
    },
    Bonus.Speed: {
        YELLOW: 'assets/images/speed_yellow.png',
        GREEN: 'assets/images/speed_green.png',
        BLUE: 'assets/images/speed_blue.png',
        RED: 'assets/images/speed_red.png',
    },
    Bonus.InstantWin: {
        YELLOW: 'assets/images/instant_win_yellow.png',
        GREEN: 'assets/images/instant_win_green.png',
        BLUE: 'assets/images/instant_win_blue.png',
        RED: 'assets/images/instant_win_red.png',
    },
}

# 顶部栏配色方案
PANEL_BG = (245, 245, 220)  # 浅米色面板背景
TEXT_PRIMARY = (80, 80, 120)  # 主要文字颜色
TEXT_SECONDARY = (100, 150, 100)  # 次要文字颜色
TEXT_ACCENT = (200, 80, 80)  # 强调色

class Label:
    def __init__(self, text, position, color=(60, 60, 60), bg_color=(245, 245, 220)):  # 新配色
        self.font = pygame.font.Font('assets/fonts/STCAIYUN.TTF', FONT_SIZE)
        self.color = color
        self.text = self.font.render(text, True, color)
        self.width, self.height = self.font.size(text)
        # 计算带背景的尺寸
        self.bg_width = self.width + 30  # 增加左右边距
        self.bg_height = self.height + 10  # 增加上下边距
        self.x_start = position[0] - self.bg_width // 2  # 以背景中心对齐
        self.y_start = position[1] - self.bg_height // 2
        # 文本在背景中的位置
        self.text_x = self.x_start + (self.bg_width - self.width) // 2
        self.text_y = self.y_start + (self.bg_height - self.height) // 2
        # 背景效果增强
        self.bg_surface = pygame.Surface((self.bg_width, self.bg_height), pygame.SRCALPHA)
        pygame.draw.rect(self.bg_surface, bg_color + (200,),  # 半透明效果
                        (0, 0, self.bg_width, self.bg_height), 
                        border_radius=5)

class Display:
    def __init__(self, background_color=TAUPE, gradient_colors=None,
                 buttons=None, labels=None, sprites=None):
        if buttons is None:
            self.buttons = []
        else:
            self.buttons = buttons

        if sprites is None:
            self.spites = []
        else:
            self.spites = sprites

        if labels is None:
            self.labels = []
        else:
            self.labels = labels

        self.background_color = background_color
        self.gradient_colors = gradient_colors or [background_color, background_color]


class UiManager:
    def __init__(self, screen, level):
        self.screen = screen
        self.level = level

        # 先初始化按钮
        self.pause_btn = Button('Pause', (WIDTH-60, 40), small=True)
        self.restart_btn = Button('Restart', (60, 40), small=True)
        # 新增：切换控制模式按钮（位于顶部中央）
        self.change_mode_btn = Button('Change Mode', (WIDTH//2, 40), small=True)

        # 再初始化其他组件
        self.load_grass_images()
        self.grass_positions = []
        for _ in range(30):
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 50)
            self.grass_positions.append((
                x, y,
                random.choice(self.grass_images),
                random.randint(-5, 5),
                random.uniform(0.8, 1.2)
            ))

        self.start_game_btn = Button('Start', SCREEN_CENTER)
        self.start_game_display = Display(
            gradient_colors=[(245, 222, 179), (210, 180, 140)],  # 米色渐变
            buttons=[self.start_game_btn]
        )

        # 关卡标签
        self.level_label = Label(f'Level {level.number}', 
                                (WIDTH // 2, 30), 
                                color=(80, 80, 120),  # 深蓝灰色
                                bg_color=(255, 248, 220))  # 米白色
        
        sprites = [level.player,  # 恢复玩家坦克
                   level.path, 
                   level.ball_generator,
                   level.finish, 
                   level.shooting_manager]  # 确保包含发射器
        
        self.game_display = Display(
            gradient_colors=[(173, 216, 230), (135, 206, 250)],
            sprites=[sprite for sprite in sprites],  # 现在包含所有必要元素
            labels=[self.level_label],
            buttons=[self.pause_btn, self.restart_btn, self.change_mode_btn]
        )

        self.continue_btn = Button('Continue', SCREEN_CENTER)
        self.win_level_display = Display(
            gradient_colors=[(152, 251, 152), (50, 205, 50)],  # 绿色渐变
            buttons=[self.continue_btn]
        )

        self.start_level_again_btn = Button('Restart', SCREEN_CENTER,
                                            background_color=TAUPE,
                                            font_color=BROWN)
        self.lose_level_display = Display(
            gradient_colors=[(255, 182, 193), (220, 20, 60)],  # 红色渐变
            buttons=[self.start_level_again_btn]
        )

        self.finish_btn = Button('Finish', (WIDTH // 2, HEIGHT // 2 +
                                               2 * BTN_HEIGHT))
        self.start_game_again_btn = Button('Restart', SCREEN_CENTER)
        self.win_label = Label('Win！', (WIDTH // 2, HEIGHT // 2 -
                                               2 * BTN_HEIGHT))
        self.win_game_display = Display(buttons=[self.start_game_again_btn,
                                                 self.finish_btn],
                                        labels=[self.win_label])

        self.new_game_button = Button('Start again', SCREEN_CENTER,
                                      background_color=TAUPE,
                                      font_color=BROWN)
        self.lose_game_display = Display(BROWN,
                                         buttons=[self.new_game_button])

    def draw_button(self, button):
        width, height = button.width, button.height
        x_start, y_start = button.x_start, button.y_start
        title_params = (x_start + width / 2 - button.title_width / 2,
                        y_start + height / 2 - button.title_height / 2)
        pygame.draw.rect(self.screen, button.background_color,
                         (x_start, y_start, width, height))
        self.screen.blit(button.font.render(button.title, True,
                                            button.font_color), title_params)
        button.rect = pygame.Rect((x_start, y_start, width, height))

    def draw_window(self, window: Display):
        """
        绘制窗口。

        :param window: 显示对象
        """
        if window.gradient_colors:
            # 创建垂直渐变
            height = HEIGHT
            for y in range(height):
                ratio = y / height
                r = int(window.gradient_colors[0][0] * (1 - ratio) + window.gradient_colors[1][0] * ratio)
                g = int(window.gradient_colors[0][1] * (1 - ratio) + window.gradient_colors[1][1] * ratio)
                b = int(window.gradient_colors[0][2] * (1 - ratio) + window.gradient_colors[1][2] * ratio)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        else:
            self.screen.fill(window.background_color)
        self.draw_grass()  # 直接绘制固定草地，不再更新
        for button in window.buttons:
            self.draw_button(button)
        for label in window.labels:
            self.put_label(label)
        for sprite in window.spites:
            sprite.draw(self.screen)

    def show_score(self, points):
        points_label = Label(f'Score: {points}', 
                            (WIDTH // 4, 30),
                            color=(100, 150, 100),  # 叶绿色
                            bg_color=(245, 245, 220))  # 浅米色
        self.put_label(points_label)

    def show_lives(self, lives):
        lives_label = Label(str(lives), 
                           (3 * WIDTH // 4, 30),
                           color=(200, 80, 80),  # 暗红色
                           bg_color=(245, 245, 220))
        self.put_label(lives_label)
        # 图标位置微调
        self.screen.blit(pygame.transform.smoothscale(
            pygame.image.load("assets/images/life.png"), (25, 25)),
            (3 * WIDTH // 4 - 35, 20))  # 左移35像素

    def put_label(self, label):
        # 绘制带圆角的半透明背景
        self.screen.blit(label.bg_surface, (label.x_start, label.y_start))
        # 绘制文字
        self.screen.blit(label.text, (label.text_x, label.text_y))

    def load_grass_images(self):
        self.grass_images = [
            pygame.image.load("assets/images/background_1.png"),
            pygame.image.load("assets/images/background_2.png"),
            pygame.image.load("assets/images/background_3.png"),
            pygame.image.load("assets/images/background_4.png"),
            pygame.image.load("assets/images/background_5.png"),
            pygame.image.load("assets/images/background_6.png"),
            pygame.image.load("assets/images/background_7.png"),
            pygame.image.load("assets/images/background_8.png")
        ]

    def draw_grass(self):

        for pos in self.grass_positions:
            x, y, img, angle, scale = pos
            final_img = pygame.transform.rotozoom(img, angle, scale)
            self.screen.blit(final_img, (x, y))

    def draw_start_menu_buttons(self):
        # 绘制背景图
        try:
            bg = pygame.image.load(r"assets/background/Paris.jpg").convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            self.screen.blit(bg, (0, 0))
        except Exception:
            pass
        # 渐变背景覆盖
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 200))
        self.screen.blit(overlay, (0, 0))
        # 标题
        font_title = pygame.font.Font(None, 64)
        title_surf = font_title.render("Select Control Mode", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_surf, title_rect)
        # 按钮样式
        btn_font = pygame.font.Font(None, 36)
        btn_w, btn_h = BTN_WIDTH, BTN_HEIGHT
        start_y = HEIGHT//2
        gap = btn_h + 20
        mouse_pos = pygame.mouse.get_pos()
        # 鼠标控制按钮
        self.mouse_control_btn = pygame.Rect((WIDTH-btn_w)//2, start_y, btn_w, btn_h)
        color_mouse = RED if not self.mouse_control_btn.collidepoint(mouse_pos) else (255, 100, 100)
        pygame.draw.rect(self.screen, color_mouse, self.mouse_control_btn, border_radius=8)
        txt = btn_font.render("Mouse Control", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.mouse_control_btn.center))
        # 手势控制按钮
        self.gesture_control_btn = pygame.Rect((WIDTH-btn_w)//2, start_y+gap, btn_w, btn_h)
        color_gesture = GREEN if not self.gesture_control_btn.collidepoint(mouse_pos) else (100, 255, 100)
        pygame.draw.rect(self.screen, color_gesture, self.gesture_control_btn, border_radius=8)
        txt = btn_font.render("Gesture Control", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.gesture_control_btn.center))
        # 语音控制按钮
        self.voice_control_btn = pygame.Rect((WIDTH-btn_w)//2, start_y+2*gap, btn_w, btn_h)
        color_voice = BLUE if not self.voice_control_btn.collidepoint(mouse_pos) else (100, 100, 255)
        pygame.draw.rect(self.screen, color_voice, self.voice_control_btn, border_radius=8)
        txt = btn_font.render("Voice Control", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.voice_control_btn.center))
        # 新增：键盘控制按钮
        self.keyboard_control_btn = pygame.Rect((WIDTH-btn_w)//2, start_y+3*gap, btn_w, btn_h)
        color_keyboard = GREY if not self.keyboard_control_btn.collidepoint(mouse_pos) else (180, 180, 180)
        pygame.draw.rect(self.screen, color_keyboard, self.keyboard_control_btn, border_radius=8)
        txt = btn_font.render("Keyboard Control", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.keyboard_control_btn.center))
