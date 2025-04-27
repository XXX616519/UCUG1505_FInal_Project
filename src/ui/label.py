import pygame
from ..Constants import FONT_SIZE, BROWN



class Label:
    def __init__(self, text: str, position: tuple, font_color=(255, 255, 255), font_size=24):
        """
        初始化标签对象。

        :param text: 标签的文本内容
        :param position: 标签的中心位置 (x, y)
        :param font_color: 标签字体颜色
        :param font_size: 标签字体大小
        """
        self.font = pygame.font.Font('assets/fonts/STCAIYUN.TTF', font_size)  # 使用自定义字体大小
        self.font_color = font_color  # 使用自定义字体颜色
        self.text = self.font.render(text, True, self.font_color)  # 渲染字体时使用 font_color
        self.width, self.height = self.font.size(text)
        self.x_start = position[0] - self.width // 2
        self.y_start = position[1] - self.height // 2

    def draw(self, screen: pygame.Surface):
        """
        绘制标签。

        :param screen: Pygame 的屏幕对象。
        """
        screen.blit(self.text, (self.x_start, self.y_start))