import pygame


def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """
    检查两个矩形是否发生碰撞。

    :param rect1: 第一个矩形
    :param rect2: 第二个矩形
    :return: 如果发生碰撞则返回 True，否则返回 False
    """
    return rect1.colliderect(rect2)


def check_point_in_rect(point: tuple, rect: pygame.Rect) -> bool:
    """
    检查一个点是否在矩形内。

    :param point: 点的坐标 (x, y)
    :param rect: 矩形
    :return: 如果点在矩形内则返回 True，否则返回 False
    """
    return rect.collidepoint(point)


def check_circle_collision(circle1: dict, circle2: dict) -> bool:
    """
    检查两个圆是否发生碰撞。

    :param circle1: 第一个圆的属性，包含 "center" (x, y) 和 "radius"
    :param circle2: 第二个圆的属性，包含 "center" (x, y) 和 "radius"
    :return: 如果两个圆发生碰撞则返回 True，否则返回 False
    """
    dx = circle1["center"][0] - circle2["center"][0]
    dy = circle1["center"][1] - circle2["center"][1]
    distance_squared = dx ** 2 + dy ** 2
    radius_sum = circle1["radius"] + circle2["radius"]
    return distance_squared <= radius_sum ** 2