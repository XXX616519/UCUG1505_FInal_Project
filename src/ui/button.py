import pygame
from src.Constants import BTN_WIDTH, BTN_HEIGHT, FONT_SIZE, BROWN, TAUPE

class Button:
    def __init__(self, button_title, position, width=BTN_WIDTH,
                 height=BTN_HEIGHT, background_color=BROWN, font_color=(0, 0, 0), 
                 small=False, corner_radius=8):
        self.title = button_title
        self.font = pygame.font.Font('assets/fonts/STCAIYUN.TTF', FONT_SIZE)
        self.title_width, self.title_height = self.font.size(self.title)
        self.center = (position[0], position[1])
        
        # 先处理small参数
        if small:
            width = 80
            height = 30
            self.font = pygame.font.Font('assets/fonts/STCAIYUN.TTF', 20)
            
        self.width, self.height = width, height
        self.x_start, self.y_start = self.center[0] - self.width // 2, \
                                     self.center[1] - self.height // 2
        self.rect = pygame.Rect((self.x_start, self.y_start,
                                 width, height))
        self.background_color = background_color
        self.font_color = font_color
        self.corner_radius = corner_radius
        self.hover_color = tuple(max(0, c-30) for c in background_color)
