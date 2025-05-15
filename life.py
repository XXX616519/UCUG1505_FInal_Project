# advanced_cellular_automaton.py
# Requirements: pygame, numpy, scipy
# Install with: pip install pygame numpy scipy

import pygame
import sys
import numpy as np
from pygame.locals import *
import random
from scipy.ndimage import gaussian_filter

# Configuration
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 8
NUM_TYPES = 4
DECAY_RATE = 0.02
FPS = 30

# Rules per type
type_rules = []
for t in range(NUM_TYPES):
    type_rules.append({
        'survive_min': 2,
        'survive_max': 3,
        'revive_prob': 1.0,
        'life_span': random.randint(100, 300)
    })

# Random colors
colors = [
    (random.randint(100,255), random.randint(100,255), random.randint(100,255))
    for _ in range(NUM_TYPES)
]

# Grid size
cols = WIDTH // CELL_SIZE
rows = HEIGHT // CELL_SIZE

def init_grid_with_noise():
    noise = np.random.rand(cols, rows)
    noise = gaussian_filter(noise, sigma=4)
    grid = []
    for i in range(cols):
        col = []
        for j in range(rows):
            n = noise[i, j]
            t = int(n * NUM_TYPES) % NUM_TYPES
            col.append({'type': t, 'strength': n, 'age': 0})
        grid.append(col)
    return grid

grid = init_grid_with_noise()
next_grid = [[{'type': -1, 'strength':0, 'age':0} for _ in range(rows)] for _ in range(cols)]
selected_type = 0

def count_neighbors(x, y):
    cnt = {}
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % cols
            ny = (y + dy) % rows
            c = grid[nx][ny]
            if c['strength'] >= 1:
                cnt[c['type']] = cnt.get(c['type'], 0) + 1
    return cnt

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 18)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.unicode.isdigit():
                k = int(event.unicode)
                if 0 <= k < NUM_TYPES:
                    selected_type = k
        elif event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            i = mx // CELL_SIZE
            j = my // CELL_SIZE
            if 0 <= i < cols and 0 <= j < rows:
                grid[i][j] = {'type': selected_type, 'strength':1, 'age':0}

    screen.fill((0,0,0))

    for i in range(cols):
        for j in range(rows):
            cell = grid[i][j]
            counts = count_neighbors(i, j)
            rule = type_rules[cell['type']]
            same = counts.get(cell['type'], 0)
            new = {'type':cell['type'], 'strength':cell['strength'], 'age':cell['age']}

            # Survival or decay
            if cell['strength'] >= 1 and cell['age'] < rule['life_span']:
                if same < rule['survive_min'] or same > rule['survive_max']:
                    new['strength'] -= DECAY_RATE
                else:
                    new['strength'] = 1
                new['age'] += 1
            else:
                revived = False
                for t in range(NUM_TYPES):
                    if counts.get(t,0) == 3 and random.random() < type_rules[t]['revive_prob']:
                        new = {'type':t, 'strength':1, 'age':0}
                        revived = True
                        break
                if not revived:
                    new['strength'] = max(0, cell['strength'] - DECAY_RATE)

            # Fusion
            present = [t for t,cnt in counts.items() if cnt >= 2]
            if len(present) >= 2:
                a, b = present[0], present[1]
                new['type'] = (a + b) % NUM_TYPES
                new['strength'] = 1
                new['age'] = 0

            # Attack
            attack = sum(cnt * 0.01 for t,cnt in counts.items() if t != new['type'])
            new['strength'] = max(0, new['strength'] - attack)

            next_grid[i][j] = new

            # Draw
            if new['strength'] > 0:
                col = colors[new['type']]
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
                surf.set_alpha(int(new['strength'] * 255))
                surf.fill(col)
                screen.blit(surf, (i*CELL_SIZE, j*CELL_SIZE))

    grid, next_grid = next_grid, grid

    # Display selected type
    text = font.render(f"Selected Type: {selected_type}", True, (255,255,255))
    screen.blit(text, (10, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
