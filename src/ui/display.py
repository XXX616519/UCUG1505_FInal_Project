from ..Constants import TAUPE, BROWN


class Display:
    def __init__(self, background_color=TAUPE, buttons=None, labels=None,
                 sprites=None):
        """
        初始化显示对象。

        :param background_color: 显示背景颜色
        :param buttons: 显示的按钮列表
        :param labels: 显示的标签列表
        :param sprites: 显示的精灵列表
        """
        self.buttons = buttons if buttons else []
        self.labels = labels if labels else []
        self.sprites = sprites if sprites else []
        self.background_color = background_color