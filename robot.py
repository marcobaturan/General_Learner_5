import math
import random
from constants import *


class Robot:
    """
    Autonomous agent that learns to survive by finding batteries and avoiding walls.
    Maintains internal homeostasis variables (Hunger, Tiredness).

    GL5: Has autobiographical memory with unique self-identity (2-digit ID).
    Implements self-recognition capability (mirror test).

    GL5.1 Dual-Bot Physical Interaction Principles:
    -----------------------------------------------
    1. Pauli Exclusion: Two bots cannot occupy same tile. Movement blocked.
    2. Pain on Impact: Collision triggers -IMPACT_UNITS energy penalty to both.
    3. Mutual Recognition: Each bot has self_id for differentiating self from other.

    The collision detection system implements fundamental physics of agent interaction,
    creating emergent avoidance behavior without explicit "avoid other bot" programming.

    Attributes:
        self_id: Unique identifier (1 or 2) for mutual recognition
        last_collision: Flag for learning from collision events
    """

    def __init__(self, env, self_id=None):
        self.env = env
        self.reset()
        self.score = 0
        self.direction = DIR_N
        self.hunger = 0  # Increases every move, reset by battery
        self.tiredness = 0  # Increases every move, triggers Sleep Cycle (Dreaming)

        # GL5: Autobiographical memory - unique self-identity
        # Generated once per robot instance, persists across sessions
        # GL5 Dual-Bot: Use provided self_id or generate new
        if self_id is not None:
            self.self_id = self_id
        else:
            self.self_id = random.randint(*SELF_ID_RANGE)

    def reset(self):
        """Positions the robot back in the center of the world."""
        self.x = GRID_W // 2
        self.y = GRID_H // 2
        self.direction = DIR_N
        self.last_collision = False

    def get_state(self, other_bot=None):
        """
        Returns the robot's complete current 'Situation', including
        raw numerical sensory data for the Fuzzy Logic layer.

        GL5 Dual-Bot: other_bot parameter enables mutual recognition.
        """
        raw_distances = {
            "N": self._dist_to_wall(DIR_N),
            "E": self._dist_to_wall(DIR_E),
            "S": self._dist_to_wall(DIR_S),
            "W": self._dist_to_wall(DIR_W),
        }

        # Calculate distance to nearest battery
        batt_dist = self._dist_to_nearest_battery()

        return {
            "pos": (self.x, self.y),
            "dir": self.direction,
            "perception": self.env.get_perception_at(
                self.x, self.y, self.direction, other_bot
            ),
            "raw_distances": raw_distances,
            "batt_distance": batt_dist,
            "needs": {"hunger": self.hunger, "tiredness": self.tiredness},
            "self_id": self.self_id,
        }

    def _dist_to_wall(self, direction):
        """Calculates numerical distance to the nearest wall in a given direction."""
        d = 0
        cx, cy = self.x, self.y
        while d < 15:  # Sensory limit
            d += 1
            if direction == DIR_N:
                cy -= 1
            elif direction == DIR_E:
                cx += 1
            elif direction == DIR_S:
                cy += 1
            elif direction == DIR_W:
                cx -= 1

            if self.env.get_at(cx, cy) == WALL_ID:
                return float(d)
        return float(d)

    def _dist_to_nearest_battery(self):
        """Calculates Euclidean distance to the nearest battery in the environment."""
        min_dist = float("inf")
        found = False
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.env.grid[y][x] == BATTERY_ID:
                    dist = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        found = True
        return min_dist if found else None

    def step(self, action, other_bot=None):
        """
        Executes a discrete motor command and returns its reinforcement value.
        Actions: 0:Turn Left, 1:Turn Right, 2:Move Forward, 3:Move Backward

        GL5 Dual-Bot: other_bot parameter enables collision detection.
        """
        from constants import IMPACT_UNITS

        reward = -1  # Small penalty per step to encourage efficiency
        self.hunger += 1
        self.tiredness += 1

        if action == 0:  # Turn Left
            self.direction = (self.direction - 1) % 4
        elif action == 1:  # Turn Right
            self.direction = (self.direction + 1) % 4
        elif action == 2:  # Move Forward
            reward = self.move_forward(other_bot)
        elif action == 3:  # Move Backward
            reward = self.move_backward(other_bot)

        # Check current cell for objects (Batteries, Reset Button)
        obj = self.env.get_at(self.x, self.y)
        if obj == BATTERY_ID:
            reward = 10  # Positive reinforcement
            self.score += 10
            self.hunger = 0  # Satisfaction of biological need
            self.env.remove_at(self.x, self.y)

        return reward

    def move_forward(self, other_bot=None):
        """Attempts to move in the current facing direction."""
        from constants import IMPACT_UNITS, WALL_ID

        nx, ny = self.x, self.y
        if self.direction == DIR_N:
            ny -= 1
        elif self.direction == DIR_E:
            nx += 1
        elif self.direction == DIR_S:
            ny += 1
        elif self.direction == DIR_W:
            nx -= 1

        # Collision detection: Walls prevent movement
        target_obj = self.env.get_at(nx, ny)

        # GL5 Dual-Bot: Pauli Exclusion - check for other bot
        collision = False
        impact_penalty = 0
        if other_bot is not None:
            if nx == other_bot.x and ny == other_bot.y:
                collision = True
                impact_penalty = IMPACT_UNITS
                # Record collision event for learning
                self.last_collision = True
                other_bot.last_collision = True

        if collision:
            # Pain on impact: both bots receive penalty
            return -1 - impact_penalty
        elif target_obj != WALL_ID:
            self.x, self.y = nx, ny
            return -1

        # No collision
        self.last_collision = False
        return -1  # Wall hit

    def move_backward(self, other_bot=None):
        """Attempts to move opposite to the current facing direction."""
        from constants import IMPACT_UNITS, WALL_ID

        nx, ny = self.x, self.y
        if self.direction == DIR_N:
            ny += 1
        elif self.direction == DIR_E:
            nx -= 1
        elif self.direction == DIR_S:
            ny -= 1
        elif self.direction == DIR_W:
            nx += 1

        # GL5 Dual-Bot: Pauli Exclusion - check for other bot
        collision = False
        impact_penalty = 0
        if other_bot is not None:
            if nx == other_bot.x and ny == other_bot.y:
                collision = True
                impact_penalty = IMPACT_UNITS

        target_obj = self.env.get_at(nx, ny)
        if collision:
            return -1 - impact_penalty
        elif target_obj != WALL_ID:
            self.x, self.y = nx, ny
            return -1

        return -1

    def get_action_to(self, target_x, target_y):
        """
        Vicarious Learning helper: Determines which motor command
        is needed to reach an adjacent cell (target_x, target_y).
        Used by the UI's Guide Mode.
        """
        if target_x == self.x and target_y == self.y:
            return None

        # Simple heuristic: If we can reach it by moving forward, do so.
        # Otherwise, rotate to face the target.
        dx = target_x - self.x
        dy = target_y - self.y

        target_dir = None
        if dx == 1:
            target_dir = DIR_E
        elif dx == -1:
            target_dir = DIR_W
        elif dy == 1:
            target_dir = DIR_S
        elif dy == -1:
            target_dir = DIR_N

        if target_dir is not None:
            if target_dir == self.direction:
                return 2  # Forward
            else:
                # Rotate toward it
                diff = (target_dir - self.direction + 4) % 4
                if diff == 1:
                    return 1  # Right
                return 0  # Left
        return None
