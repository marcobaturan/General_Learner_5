import random
from constants import *

class Environment:
    def __init__(self):
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.batteries = [] # List of (x,y)
        self.walls = [] # List of (x,y)
        self.reset()
        
    def reset(self):
        """Resets the environment setting random walls and 1-3 batteries, ensuring the center is free."""
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.batteries.clear()
        self.walls.clear()
        
        center_x, center_y = GRID_W // 2, GRID_H // 2
        
        # Place random walls (let's say ~10 walls)
        num_walls = random.randint(5, 15)
        for _ in range(num_walls):
            self._place_random_item(WALL_ID, [(center_x, center_y)])
            
        # Place 1 to 3 batteries
        num_batteries = random.randint(1, 3)
        for _ in range(num_batteries):
            self._place_random_item(BATTERY_ID, [(center_x, center_y)])

    def _place_random_item(self, item_id, exclude_list):
        placed = False
        while not placed:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            # Conditions for placing: empty and not in excluded positions
            if self.grid[y][x] == EMPTY_ID and (x, y) not in exclude_list:
                self.grid[y][x] = item_id
                placed = True
                if item_id == WALL_ID:
                    self.walls.append((x, y))
                elif item_id == BATTERY_ID:
                    self.batteries.append((x, y))
                    
    def remove_battery(self, x, y):
        if (x, y) in self.batteries:
            self.batteries.remove((x, y))
            self.grid[y][x] = EMPTY_ID

    def get_cell(self, x, y):
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            return self.grid[y][x]
        return WALL_ID # Out of bounds acts like a wall

    def get_perception_matrix(self, pos_x, pos_y, direction):
        """
        Returns the perception array based on relative orientation:
        3 cells ahead, 2 to sides, 0 behind.
        Returns a simplified representation (flattened or structured).
        Let's define rows 0 to 3 relative to robot.
        Row 0 is distance 0 (the robot's row), which includes side cells distance 1 and 2.
        Row 1 is 1 block ahead, width 5 (2 left, center, 2 right)
        Row 2 is 2 blocks ahead.
        Row 3 is 3 blocks ahead.
        Total cells = 4 rows x 5 columns = 20 cells.
        """
        # Direction mappings for dy, dx (relative 'ahead')
        # North: y decreases
        dir_offsets = {
            DIR_N: (0, -1),
            DIR_E: (1, 0),
            DIR_S: (0, 1),
            DIR_W: (-1, 0)
        }
        
        forward_vec = dir_offsets[direction]
        # Right vector is 90 degrees clockwise
        right_vec = (-forward_vec[1], forward_vec[0]) 

        perception = []
        for dist_fwd in range(0, 4):  # 0 to 3 ahead
            for dist_right in range(-2, 3): # -2 (left) to 2 (right)
                # Ignore the robot's own cell (0,0) or include it as special?
                # The user wants "tacto a 0 metros", which means the adjacent blocks or its own.
                cell_x = pos_x + forward_vec[0] * dist_fwd + right_vec[0] * dist_right
                cell_y = pos_y + forward_vec[1] * dist_fwd + right_vec[1] * dist_right
                cell_val = self.get_cell(cell_x, cell_y)
                perception.append(cell_val)
                
        return perception
