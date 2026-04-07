import pygame

# Grid and window sizing
GRID_W = 10
GRID_H = 10
CELL_SIZE = 40

# Window regions
CANVAS_WIDTH = GRID_W * CELL_SIZE
CANVAS_HEIGHT = GRID_H * CELL_SIZE
WINDOW_WIDTH = 1350 # Slightly wider for more info
WINDOW_HEIGHT = 650 # Slightly taller
PANEL_WIDTH = 220
REPORT_WIDTH = 300
POV_WIDTH = 350
POV_HEIGHT = 450

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHT_ORANGE = (255, 220, 150)
PINK = (255, 182, 193)  # Light pink for guide path
CYAN = (0, 255, 255)
PURPLE = (160, 32, 240)
YELLOW = (255, 255, 0)

# IDs for elements on the grid
EMPTY_ID = 0
BATTERY_ID = 1
WALL_ID = 2

# Robot directions
DIR_N = 0
DIR_E = 1
DIR_S = 2
DIR_W = 3

# Robot motor actions
ACT_LEFT = 0
ACT_RIGHT = 1
ACT_FORWARD = 2
ACT_BACKWARD = 3

# UI Constants
BTN_HEIGHT = 30 # Compactified from 40
BTN_MARGIN = 4

# Need thresholds
TIREDNESS_MAX = 150 
HUNGER_MAX = 150

# Cognitive Logic
DECAY_RATE_EPISODIC = 0.85 # Faster asymptotic decay
DECAY_RATE_SEMANTIC = 0.98 # Slower asymptotic decay
FORGET_THRESHOLD = 0.05
MEMORY_EPISODIC = 0
MEMORY_SEMANTIC = 1
