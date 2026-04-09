import random
import hashlib
from constants import *


class Environment:
    """
    Manages the 2D grid world where the robot lives.
    Handles walls, batteries, mirrors, and the robot's spatial awareness.

    GL5.1 Extensions:
    ----------------
    - RESET_BUTTON: Special tile that appears when all batteries consumed
      to prevent agent psychosis (endless search loop / TOC)
    - Other bot detection: get_perception_at() can detect other robots
      via the other_bot parameter, returning ID 99 for the other bot

    Grid Coordinate System:
    ----------------------
    (0,0) top-left to (GRID_W-1, GRID_H-1) bottom-right
    Each cell contains: EMPTY_ID, WALL_ID, BATTERY_ID, MIRROR_ID, RESET_BUTTON_ID
    """

    def __init__(self):
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.maze_id = None
        self.original_battery_positions = []
        self.reset_button_pos = None
        self.reset()

    def reset(self):
        """
        Clears the grid and regenerates a new random configuration of walls
        and batteries for the next experimental cycle.

        GL5: Generates a unique maze_id based on the wall/battery configuration
        to enable multi-maze learning.
        """
        # Reset to empty state
        self.grid = [[EMPTY_ID for _ in range(GRID_W)] for _ in range(GRID_H)]

        # 1. Place Walls: Static obstacles that the robot cannot pass.
        wall_positions = []
        for _ in range(15):
            wx, wy = random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1)
            # Avoid placing walls at the robot's starting position (center)
            if (wx, wy) != (GRID_W // 2, GRID_H // 2):
                self.grid[wy][wx] = WALL_ID
                wall_positions.append((wx, wy))

        # GL5: Place one mirror on a random wall (for self-recognition test)
        # The mirror acts as a reflective surface the robot can "see" itself in
        if wall_positions:
            mirror_pos = random.choice(wall_positions)
            mx, my = mirror_pos
            self.grid[my][mx] = MIRROR_ID

        # 2. Place Batteries: Resource entities that provide +10 reinforcement points.
        target_batteries = random.randint(1, 3)
        placed = 0
        battery_positions = []
        while placed < target_batteries:
            bx, by = random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1)
            # Ensure placement on an empty tile and away from the starting position
            if self.grid[by][bx] == EMPTY_ID and (bx, by) != (GRID_W // 2, GRID_H // 2):
                self.grid[by][bx] = BATTERY_ID
                placed += 1
                battery_positions.append((bx, by))

        # Store original battery positions for reset functionality
        self.original_battery_positions = battery_positions.copy()

        # Reset button tracking (initially None)
        self.reset_button_pos = None

        # Generate unique maze_id based on configuration
        # This enables the agent to store separate maps for different mazes
        config_str = f"{sorted(wall_positions)}{sorted(battery_positions)}"
        self.maze_id = hashlib.md5(config_str.encode()).hexdigest()[:8]

    def count_batteries(self):
        """Returns the number of batteries currently on the grid."""
        count = 0
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == BATTERY_ID:
                    count += 1
        return count

    def spawn_reset_button(self):
        """
        Spawns a RESET_BUTTON at a random valid position.
        Called when all batteries are consumed (psychosis prevention).

        This implements the "Psychosis Cure" mechanism: when an agent
        consumes all available goals (batteries), it enters a pathological
        state of random movement with no learning signal (analogous to
        TOC/Touch-of-Contract in obsessive behavior). The reset button
        provides a new goal, creating an endless search loop.

        Constraints:
        - Only one RESET_BUTTON active at a time
        - Cannot spawn on wall, battery, or center position
        - Must spawn on reachable tile (has at least one empty neighbor)

        See: WHITE_PAPER.md Section 5.2
        """
        if self.reset_button_pos is not None:
            return  # Only one reset button at a time

        # Find all valid empty positions (not wall, not battery, not center)
        valid_positions = []
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == EMPTY_ID and (x, y) != (GRID_W // 2, GRID_H // 2):
                    # Check if reachable (not isolated by walls) - simple check: has at least one empty neighbor
                    has_empty_neighbor = any(
                        self.get_at(x + dx, y + dy) == EMPTY_ID
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    )
                    if has_empty_neighbor:
                        valid_positions.append((x, y))

        if valid_positions:
            rx, ry = random.choice(valid_positions)
            self.grid[ry][rx] = RESET_BUTTON_ID
            self.reset_button_pos = (rx, ry)

    def respawn_batteries(self):
        """Respawns all batteries at their original positions after reset button trigger."""
        # Remove reset button
        if self.reset_button_pos:
            rx, ry = self.reset_button_pos
            if 0 <= rx < GRID_W and 0 <= ry < GRID_H:
                self.grid[ry][rx] = EMPTY_ID
            self.reset_button_pos = None

        # Respawn batteries at original positions
        for bx, by in self.original_battery_positions:
            if 0 <= bx < GRID_W and 0 <= by < GRID_H:
                self.grid[by][bx] = BATTERY_ID

    def get_at(self, x, y):
        """
        Safely returns the ID of the object at (x, y).
        Returns WALL_ID if the coordinates are out of bounds.
        """
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            return self.grid[y][x]
        return WALL_ID  # Out of bounds is treated as an impenetrable wall

    def remove_at(self, x, y):
        """Sets the cell at (x, y) to EMPTY_ID. Used when a battery is consumed."""
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            self.grid[y][x] = EMPTY_ID

    def get_perception_at(self, rx, ry, direction, other_bot=None):
        """
        Calculates the robot's local view (Situational Awareness).

        GL5 Dual-Bot: other_bot parameter adds OTHER_BOT detection to perception.
        """
        perception = []
        for dy in range(-1, 2):
            row = []
            for dx in range(-1, 2):
                tx, ty = rx + dx, ry + dy

                # GL5 Dual-Bot: Detect other bot in perception
                if other_bot is not None and tx == other_bot.x and ty == other_bot.y:
                    row.append(99)  # Special ID for other bot
                else:
                    row.append(self.get_at(tx, ty))
            perception.append(row)
        return perception
