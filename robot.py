from constants import *
from environment import Environment

class Robot:
    def __init__(self, env: Environment):
        self.env = env
        self.reset()
        
    def reset(self):
        self.x = GRID_W // 2
        self.y = GRID_H // 2
        self.direction = DIR_N
        self.score = 0
        self.tiredness = 0 
        self.hunger = HUNGER_MAX  # starts hungry or full? Let's say hunger increases to max.
        
    def get_state(self):
        # State includes perception and internal needs
        perception = self.env.get_perception_matrix(self.x, self.y, self.direction)
        # 1 if very hungry, 0 if not
        is_hungry = 1 if self.hunger > (HUNGER_MAX // 2) else 0
        return {
            'perception': perception,
            'is_hungry': is_hungry
        }

    def can_move(self, target_x, target_y):
        cell = self.env.get_cell(target_x, target_y)
        if cell == WALL_ID:
            return False
        return True

    def step(self, action):
        """
        Actions:
        0 = Turn Left
        1 = Turn Right
        2 = Move Forward
        3 = Move Backward
        Returns: reward gained
        """
        reward = -1  # every cycle costs 1
        self.tiredness += 1
        self.hunger += 1
        
        target_x, target_y = self.x, self.y
        dir_offsets = {
            DIR_N: (0, -1),
            DIR_E: (1, 0),
            DIR_S: (0, 1),
            DIR_W: (-1, 0)
        }
        
        if action == 0:
            self.direction = (self.direction - 1) % 4
        elif action == 1:
            self.direction = (self.direction + 1) % 4
        elif action == 2: # Forward
            dx, dy = dir_offsets[self.direction]
            target_x += dx
            target_y += dy
        elif action == 3: # Backward
            dx, dy = dir_offsets[self.direction]
            target_x -= dx
            target_y -= dy

        if action in [2, 3]:
            # Try to move
            cell = self.env.get_cell(target_x, target_y)
            if cell == WALL_ID:
                # Collision
                reward += -10
            else:
                self.x, self.y = target_x, target_y
                if cell == BATTERY_ID:
                    reward += 10
                    self.hunger = 0 # reset hunger
                    self.env.remove_battery(self.x, self.y)
                    # If all batteries are consumed, we could add more
                    
        self.score += reward
        return reward

    def get_action_to(self, target_x, target_y):
        """
        Returns the action required to move to an adjacent cell (target_x, target_y).
        Calculates rotation and forward movement.
        """
        dx, dy = target_x - self.x, target_y - self.y
        if abs(dx) + abs(dy) != 1: return None
        
        # Determine target direction
        target_dir = None
        if dx == 1: target_dir = DIR_E
        elif dx == -1: target_dir = DIR_W
        elif dy == 1: target_dir = DIR_S
        elif dy == -1: target_dir = DIR_N
        
        if target_dir is None: return None
        
        # If already facing that way, move forward
        if self.direction == target_dir:
            return 2 # Forward
        else:
            # Turn towards target
            diff = (target_dir - self.direction) % 4
            if diff == 1: return 1 # Right
            elif diff == 3: return 0 # Left
            else: return 1 # Turn around (either side)
