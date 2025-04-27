from src.Constants import *
from src.Special_Ball import Bonus
from src.ui.button import Button

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
}


class Label:
    def __init__(self, text, position, color=(0, 0, 0)):  # 默认字体颜色为黑色
        self.font = pygame.font.Font('assets/fonts/STCAIYUN.TTF', FONT_SIZE)
        self.color = color  # 字体颜色
        self.text = self.font.render(text, True, color)
        self.width, self.height = self.font.size(text)
        self.x_start, self.y_start = position[0] - self.width // 2, \
                                     position[1] - self.height // 2

class Display:
    def __init__(self, background_color=TAUPE, buttons=None, labels=None,
                 sprites=None):
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


class UiManager:
    def __init__(self, screen, level):
        self.screen = screen
        self.level = level

        self.start_game_btn = Button('Start', SCREEN_CENTER)
        self.start_game_display = Display(buttons=[self.start_game_btn])

        self.level_label = Label('Level {}'.format(level.number),
                                   (WIDTH // 2, 40))
        sprites = [level.player, level.path, level.ball_generator,
                   level.finish, level.shooting_manager]
        self.game_display = Display(sprites=[sprite for sprite in sprites],
                                    labels=[self.level_label])

        self.continue_btn = Button('Continue', SCREEN_CENTER)
        self.win_level_display = Display(buttons=[self.continue_btn])

        self.start_level_again_btn = Button('Restart', SCREEN_CENTER,
                                            background_color=TAUPE,
                                            font_color=BROWN)
        self.lose_level_display = Display(BROWN,
                                          buttons=[self.start_level_again_btn])

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

    def draw_window(self, window):
        self.screen.fill(window.background_color)
        for button in window.buttons:
            self.draw_button(button)
        for label in window.labels:
            self.put_label(label)
        for sprite in window.spites:
            sprite.draw(self.screen)

    def show_score(self, points):
        points_label = Label('Score: {}'.format(points), (WIDTH // 4, 40))
        self.put_label(points_label)

    def show_lives(self, lives):

        self.put_label(Label(str(lives), (3 * WIDTH // 4 + 30, 40)))
        self.screen.blit(pygame.transform.smoothscale(
            pygame.image.load("assets/images/life.png"), (20, 20)),
            (3 * WIDTH // 4, 30))

    def put_label(self, label, color=TAUPE):
        pygame.draw.rect(self.screen, color, (label.x_start - label.width / 2,
                                              label.y_start, label.width,
                                              label.height))
        self.screen.blit(label.text, (label.x_start, label.y_start))
