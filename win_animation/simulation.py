from ._variables import *
from .grid import Grid
from numba import njit
import numpy as np
import pandas as pd
from PIL import Image, ImageFilter
import pygame
import sys
from datetime import datetime



def parse_color(color_str):
    color_str = color_str.strip().strip('"').strip("'").strip("()")
    return tuple(int(c.strip()) for c in color_str.split(','))

def convert_time_to_float(time_str):
    """
    将时间字符串转换成浮点数（时间戳），本例使用秒级的时间戳。
    """
    dt = datetime.fromisoformat(time_str)
    return dt.timestamp()

def min_max_normalize(arr):
    """
    使用最小—最大标准化，将数组转换到 [0, 1] 范围
    """
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val - min_val == 0:
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)


# def construct_matrix_from_csv(csv_file):
#     # 1. 读取 CSV 文件（假设文件包含三列：time, angle, color）
#     df = pd.read_csv(csv_file)
    
#     # 2. 将时间字符串转换为数值（时间戳）
#     df['time_float'] = df['time'].apply(convert_time_to_float)
    
#     # 3. 解析颜色字符串，拆分成 R, G, B 三个新列
#     colors_parsed = df['color'].apply(parse_color)
#     df[['R', 'G', 'B']] = pd.DataFrame(colors_parsed.tolist(), index=df.index)
    
#     # 4. 从所有数据中随机抽取 6 行，用于构造模型输入数据
#     sample_df = df.sample(n=6, random_state=42)  # 固定 random_state 保证可复现性
    
#     # 只保留需要的 5 个特征：时间、角度、R、G、B
#     data = sample_df[['time_float', 'angle', 'R', 'G', 'B']].to_numpy()  # 形状 (6, 5)
    
#     # 5. 对 6×5 的数据按列进行最小—最大标准化
#     normalized_data = np.apply_along_axis(min_max_normalize, 0, data)  # 形状依然 (6, 5)
    
#     # 6. 对每一列数据进行一维线性插值，将 6 个点扩展为 20 个点
#     #    设原始 x 坐标为 0,1,2,3,4,5，新坐标为等间距取 20 个点（0 到 5）
#     x_original = np.arange(normalized_data.shape[0])  # [0,1,2,3,4,5]
#     x_new = np.linspace(0, normalized_data.shape[0] - 1, 20)  # 20 个点
#     interpolated_data = np.zeros((20, normalized_data.shape[1]))  # 初始化 20×5 矩阵
    
#     for col in range(normalized_data.shape[1]):
#         interpolated_data[:, col] = np.interp(x_new, x_original, normalized_data[:, col])
    
#     # 7. 计算每一行前 5 列的平均值，作为第 6 列加入矩阵
#     mean_col = np.mean(interpolated_data, axis=1).reshape(-1, 1)  # 形状 (20, 1)
#     interpolated_data_with_mean = np.hstack([interpolated_data, mean_col])  # 形状 (20, 6)
    
#     # 8. 为了最终构造 6×6 的矩阵，从 20 行中随机抽取 6 行
#     final_indices = np.random.choice(interpolated_data_with_mean.shape[0], size=6, replace=False)
#     final_matrix = interpolated_data_with_mean[final_indices, :]  # 最终矩阵形状 (6, 6)
    
#     # 如果希望用 np.zeros((len(colours), len(colours))) 的格式展示，
#     # 可将矩阵转换为如下格式：
#     final_result = np.zeros((6, 6))
#     final_result[:, :] = final_matrix
    
#     return final_result


def construct_matrix_from_csv(csv_file):
    # 1. 读取 CSV 文件（假设文件包含三列：time, angle, color）
    df = pd.read_csv(csv_file)
    
    # 2. 将时间字符串转换为数值（时间戳）
    df['time_float'] = df['time'].apply(convert_time_to_float)
    
    # 3. 解析颜色字符串，拆分成 R, G, B 三个新列
    colors_parsed = df['color'].apply(parse_color)
    df[['R', 'G', 'B']] = pd.DataFrame(colors_parsed.tolist(), index=df.index)
    
    # 4. 从所有数据中随机抽取 6 行，用于构造模型输入数据
    sample_df = df.sample(n=6, random_state=42)  # 固定 random_state 保证可复现性
    
    # 只保留需要的 5 个特征：时间、角度、R、G、B
    data = sample_df[['time_float', 'angle', 'R', 'G', 'B']].to_numpy()  # 形状 (6, 5)
    
    # 5. 对 6×5 的数据按列进行最小—最大标准化
    normalized_data = np.apply_along_axis(min_max_normalize, 0, data)  # 形状依然 (6, 5)
    
    # 6. 对每一列数据进行一维线性插值，将 6 个点扩展为 20 个点
    #    设原始 x 坐标为 0,1,2,3,4,5，新坐标为等间距取 20 个点（0 到 5）
    x_original = np.arange(normalized_data.shape[0])  # [0,1,2,3,4,5]
    x_new = np.linspace(0, normalized_data.shape[0] - 1, 20)  # 20 个点
    interpolated_data = np.zeros((20, normalized_data.shape[1]))  # 初始化 20×5 矩阵
    
    for col in range(normalized_data.shape[1]):
        interpolated_data[:, col] = np.interp(x_new, x_original, normalized_data[:, col])
    
    # 7. 计算每一行前 5 列的平均值，作为第 6 列加入矩阵
    mean_col = np.mean(interpolated_data, axis=1).reshape(-1, 1)  # 形状 (20, 1)
    interpolated_data_with_mean = np.hstack([interpolated_data, mean_col])  # 形状 (20, 6)
    
    # 8. 为了最终构造 6×6 的矩阵，从 20 行中随机抽取 6 行
    final_indices = np.random.choice(interpolated_data_with_mean.shape[0], size=6, replace=False)
    final_matrix = interpolated_data_with_mean[final_indices, :]  # 最终矩阵形状 (6, 6)
    
    # 9. 随机将矩阵中的一些元素设置为负数
    # 假设随机选择 10% 到 30% 的元素（即大约 4 到 11 个元素）
    num_elements = final_matrix.size  # 6x6 = 36 个元素
    num_negatives = np.random.randint(int(0.1 * num_elements), int(0.3 * num_elements) + 1)  # 随机选择 4 到 11 个元素
    # 获取随机索引
    indices = np.random.choice(num_elements, size=num_negatives, replace=False)
    # 将一维索引转换为二维索引
    rows, cols = np.unravel_index(indices, final_matrix.shape)
    # 将选中的元素设置为负数
    final_matrix[rows, cols] = -final_matrix[rows, cols]
    
    # 10. 转换为最终格式
    final_result = np.zeros((6, 6))
    final_result[:, :] = final_matrix
    
    return final_result



def blur(surface, strength=7, scale=0.5):
    """Takes in a surface and returns a blurred version of it"""
    size = (int(WIDTH * scale), int(HEIGHT * scale))  #size of scaled down surface
    small_surface = pygame.transform.scale(surface, size)  #scaled down surface
    image = Image.frombytes('RGB', size, pygame.image.tostring(small_surface, "RGB"))  #converts surface to an image
    blurred = image.filter(ImageFilter.GaussianBlur(strength))  #adds a blur filter to the image
    return pygame.transform.scale(pygame.image.fromstring(blurred.tobytes(), size, "RGB"), (WIDTH, HEIGHT))  #converts the image into a pygame Surface and scales up

N = config.count



class Simulation:
    def __init__(self):
        """Initialisation of Simulation environment"""
        self.positions = np.random.rand(N, 2) * np.array([WIDTH, HEIGHT])  #the positions of all the particles
        self.velocities = np.zeros((N, 2))  #the velocities of all the particles
        self.particles = np.random.randint(0, len(colours), size=N)  #the particle types - determines their nature towards each other
        #result_matrix = construct_matrix_from_csv(self.file)
        #self.attraction_matrix = np.zeros((len(colours), len(colours)))  #the attraction matrix - determines how one type interacts with another
        self.attraction_matrix=construct_matrix_from_csv(r"D:\PDF\UCUG1505_FInal_Project\lucky\lucky.csv")

        self.grid = Grid(WIDTH, HEIGHT, 2 * config.influence)  #the grid - spacial partitioning technique to optimise detection of nearby particles
        self.running=True
        #self.file=r"D:\Vscode\python_code\UCUG1505_FInal_Project\lucky\lucky.csv"

    @njit()  #numba's just-in-time compiler decorator
    def force(pos_a, pos_b, type_a, type_b, attraction_matrix, influence, beta=0.3):
        """Calculates the force between two particles"""
        dx = pos_b[0] - pos_a[0]  #difference in x co-ordinates
        dy = pos_b[1] - pos_a[1]  #difference in y co-ordinates
        distance = (dx * dx + dy * dy) ** 0.5  #eucleudian distance between the particles
        unit_dx = dx / distance  #unit distance in the x-direction
        unit_dy = dy / distance  #unit distance in the y-direction
        distance /= influence  #normalised distance
        force_magnitude = 0  #as default | when normalised distance > 1, i.e: when distance > interaction radius
        if distance < beta: force_magnitude = -1 + (distance / beta)  #universal repulsive force - to prevent collapse of particle structures
        elif beta < distance < 1: force_magnitude = (distance - beta) / (1 - beta) * attraction_matrix[type_a, type_b]  #linear interpolation of force dependant on distance
        return np.array([force_magnitude * unit_dx, force_magnitude * unit_dy])  #scaled force

    def update(self):
        """Logic to update positions and velocities of particles"""
        accelerations = np.zeros((N, 2))  #accelerations calculated every frame, therefore set to 0
        self.grid.clear()  #reset the grid
        for i in range(N): self.grid.insert(self.positions[i], i)  #populate the grid with the particle positions
        for i in range(N):  #for each particle, query neighbors within a square of side 2 * interaction radius - to get a full list of particles within its range
            position = self.positions[i]
            query = (
                max(position[0] - config.influence, 0),
                max(position[1] - config.influence, 0),
                2 * config.influence,
                2 * config.influence
            )
            nearby_particles = self.grid.query(query)  #list of particles within range that it could be affected by
            
            force = np.zeros(2)  #force initialised to 0
            for (_, j) in nearby_particles:  #loops over the nearby indexes
                if j == i:  #if the particle is itself
                    continue
                force += Simulation.force(
                    position,
                    self.positions[j],
                    self.particles[i],
                    self.particles[j],
                    self.attraction_matrix,
                    config.influence
                )
            accelerations[i] = force * config.influence 

        for i in range(N):  #adds the effect of the edge force - to prevent particles from escaping the simulation space
            position = self.positions[i]
            force = np.array([0.0, 0.0])
            if position[0] < config.fringe: force[0] = (config.fringe - position[0]) / config.fringe * config.repulsion  #left 
            elif position[0] > WIDTH - config.fringe: force[0] = - (position[0] - (WIDTH - config.fringe)) / config.fringe * config.repulsion  #right
            if position[1] < config.fringe: force[1] = (config.fringe - position[1]) / config.fringe * config.repulsion  #top
            elif position[1] > HEIGHT - config.fringe: force[1] = - (position[1] - (HEIGHT - config.fringe)) / config.fringe * config.repulsion  #bottom
            accelerations[i] += force

        self.velocities[:] = self.velocities * config.friction + accelerations * config.dt  #v = u + at 
        self.positions[:] = self.positions + self.velocities * config.dt  #r = r0 + vt

    def draw(self):
        """Iterates through the particles and draws them as circles"""
        for i in range(N):
            x, y = self.positions[i]
            pygame.draw.circle(screen, colours[self.particles[i] % len(colours)], (x, y), config.radius)

    def draw_menu(self, mouse, scroll, size = 50, font = pygame.font.SysFont("Consolas", 15), colour = (255, 253, 219)):
        """Draws the menu to edit the value of attraction between any pair of particle type/colour"""
        text = font.render(f"FPS: {int(clock.get_fps())}", True, colour)  #FPS of the program
        screen.blit(text, (10, 10))

        n = len(colours)
        for i in range(n):
            for j in range(n):
                box = pygame.Rect(WIDTH / 2 - (n * size) / 2 + j * size, HEIGHT / 2 - (n * size) / 2 + i * size, size, size)
                pygame.draw.rect(screen, colour, box, 1)

                text = font.render(f"{round(self.attraction_matrix[i][j], 1)}", True, colour)  #the attraction factor
                rect = text.get_rect(center=box.center)  #centre text in the box
                screen.blit(text, rect)  #draws it in correct place

                if box.collidepoint(mouse[0], mouse[1]):  #if the cursor is hovering over a box
                    self.attraction_matrix[i][j] += scroll  #move the value up or down depending on scroll direction
                    self.attraction_matrix[i][j] = min(1, max(-1, self.attraction_matrix[i][j]))  #clamp the value between 0 and 1

                if i == 0:  #top row of circles
                    pygame.draw.circle(screen, colours[j], (box.left + size / 2, box.top - size / 2), config.radius * 2)
                    pygame.draw.circle(screen, colour, (box.left + size / 2, box.top - size / 2), config.radius * 2, 1)  #outline
                if j == 0:  #left row of circles
                    pygame.draw.circle(screen, colours[i], (box.left - size / 2, box.top + size / 2), config.radius * 2)
                    pygame.draw.circle(screen, colour, (box.left - size / 2, box.top + size / 2), config.radius * 2, 1)  #outline

        rect = pygame.Rect(WIDTH / 2 - (n * size) / 2, HEIGHT / 2 - (n * size) / 2 + n * size, size * n, size)  #box underneath matrix
        text = font.render("Random", True, colour)
        rect = text.get_rect(center=rect.center)  #centre text in the rectangle
        if rect.collidepoint(mouse[0], mouse[1]) and scroll: self.attraction_matrix = np.random.uniform(-1, 1, (len(colours), len(colours)))  #if scroll when hovering over this box, randomly sets the attraction values
        screen.blit(text, rect)

    def run(self):
        """Runs the main simulation loop; handling events, updates and rendering"""
        menu = False  #menu to change attraction values
        #runnning =True
        while self.running:
            screen.fill(background)
            clock.tick(fps)
            scroll = 0  #value of scroll
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  #quit program if ESC key pressed
                    # pygame.quit()
                    # sys.exit()
                    self.running=False
                    return
                 
                if event.type == pygame.MOUSEBUTTONDOWN:  #if the mouse is pressed down
                    if event.button == 1: menu = not menu  #toggle menu
                if event.type == pygame.MOUSEWHEEL: scroll += event.y / 50  #amount to change attraction factor by

            self.update()  #update the system
            self.draw()  #draw the system

            if menu: self.draw_menu(pygame.mouse.get_pos(), scroll)  #menu to alter attraction matrix

            screen.blit(blur(screen), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)  #draws the blurred screen to add a bloom effect
    
            pygame.display.update()