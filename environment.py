import random
from constants import *

class Environment:
    """
    Manages the 2D grid world where the robot lives.
    Handles walls, batteries, and the robot's spatial awareness.
    """
    def __init__(self):
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.reset()

    def reset(self):
        """
        Clears the grid and regenerates a new random configuration of walls 
        and batteries for the next experimental cycle.
        """
        # Reset to empty state
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]
        
        # 1. Place Walls: Static obstacles that the robot cannot pass.
        for _ in range(15):
            wx, wy = random.randint(0, GRID_W-1), random.randint(0, GRID_H-1)
            # Avoid placing walls at the robot's starting position (center)
            if (wx, wy) != (GRID_W//2, GRID_H//2):
                self.grid[wy][wx] = WALL_ID
        
        # 2. Place Batteries: Resource entities that provide +10 reinforcement points.
        target_batteries = random.randint(1, 3)
        placed = 0
        while placed < target_batteries:
            bx, by = random.randint(0, GRID_W-1), random.randint(0, GRID_H-1)
            # Ensure placement on an empty tile and away from the starting position
            if self.grid[by][bx] == EMPTY_ID and (bx, by) != (GRID_W//2, GRID_H//2):
                self.grid[by][bx] = BATTERY_ID
                placed += 1

    def get_at(self, x, y):
        """
        Safely returns the ID of the object at (x, y). 
        Returns WALL_ID if the coordinates are out of bounds.
        """
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            return self.grid[y][x]
        return WALL_ID # Out of bounds is treated as an impenetrable wall

    def remove_at(self, x, y):
        """Sets the cell at (x, y) to EMPTY_ID. Used when a battery is consumed."""
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            self.grid[y][x] = EMPTY_ID

    def get_perception_at(self, rx, ry, direction):
        """
        Calculates the robot's local view (Situational Awareness).
        The robot perceives a 3x3 local grid centered on itself.
        """
        perception = []
        for dy in range(-1, 2):
            row = []
            for dx in range(-1, 2):
                tx, ty = rx + dx, ry + dy
                row.append(self.get_at(tx, ty))
            perception.append(row)
        return perception
