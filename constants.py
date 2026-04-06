import pygame

# Grid and window sizing
GRID_W = 10
GRID_H = 10
CELL_SIZE = 40

# Window regions
CANVAS_WIDTH = GRID_W * CELL_SIZE
CANVAS_HEIGHT = GRID_H * CELL_SIZE
WINDOW_WIDTH = 1100 # Enlarged for reporting dashboard
WINDOW_HEIGHT = 600
PANEL_WIDTH = 300
REPORT_WIDTH = 400
CANVAS_WIDTH = 400

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

# UI Constants
BTN_HEIGHT = 40
BTN_MARGIN = 5

# Need thresholds
TIREDNESS_MAX = 150 
HUNGER_MAX = 150
