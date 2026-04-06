from constants import *

class Robot:
    """
    Autonomous agent that learns to survive by finding batteries and avoiding walls.
    Maintains internal homeostasis variables (Hunger, Tiredness).
    """
    def __init__(self, env):
        self.env = env
        self.reset()
        self.score = 0
        self.direction = DIR_N
        self.hunger = 0      # Increases every move, reset by battery
        self.tiredness = 0   # Increases every move, triggers Sleep Cycle (Dreaming)

    def reset(self):
        """Positions the robot back in the center of the world."""
        self.x = GRID_W // 2
        self.y = GRID_H // 2
        self.direction = DIR_N

    def get_state(self):
        """Returns the robot's complete current 'Situation'."""
        return {
            'pos': (self.x, self.y),
            'dir': self.direction,
            'perception': self.env.get_perception_at(self.x, self.y, self.direction),
            'needs': {'hunger': self.hunger, 'tiredness': self.tiredness}
        }

    def step(self, action):
        """
        Executes a discrete motor command and returns its reinforcement value.
        Actions: 0:Turn Left, 1:Turn Right, 2:Move Forward, 3:Move Backward
        """
        reward = -1 # Small penalty per step to encourage efficiency
        self.hunger += 1
        self.tiredness += 1

        if action == 0: # Turn Left
            self.direction = (self.direction - 1) % 4
        elif action == 1: # Turn Right
            self.direction = (self.direction + 1) % 4
        elif action == 2: # Move Forward
            self.move_forward()
        elif action == 3: # Move Backward
            self.move_backward()
            
        # Check current cell for objects (Batteries)
        obj = self.env.get_at(self.x, self.y)
        if obj == BATTERY_ID:
            reward = 10     # Positive reinforcement
            self.score += 10
            self.hunger = 0 # Satisfaction of biological need
            self.env.remove_at(self.x, self.y)
            
        return reward

    def move_forward(self):
        """Attempts to move in the current facing direction."""
        nx, ny = self.x, self.y
        if self.direction == DIR_N: ny -= 1
        elif self.direction == DIR_E: nx += 1
        elif self.direction == DIR_S: ny += 1
        elif self.direction == DIR_W: nx -= 1
        
        # Collision detection: Walls prevent movement
        if self.env.get_at(nx, ny) != WALL_ID:
            self.x, self.y = nx, ny

    def move_backward(self):
        """Attempts to move opposite to the current facing direction."""
        nx, ny = self.x, self.y
        if self.direction == DIR_N: ny += 1
        elif self.direction == DIR_E: nx -= 1
        elif self.direction == DIR_S: ny -= 1
        elif self.direction == DIR_W: nx += 1
        
        if self.env.get_at(nx, ny) != WALL_ID:
            self.x, self.y = nx, ny

    def get_action_to(self, target_x, target_y):
        """
        Vicarious Learning helper: Determines which motor command 
        is needed to reach an adjacent cell (target_x, target_y).
        Used by the UI's Guide Mode.
        """
        if target_x == self.x and target_y == self.y: return None
        
        # Simple heuristic: If we can reach it by moving forward, do so.
        # Otherwise, rotate to face the target.
        dx = target_x - self.x
        dy = target_y - self.y
        
        target_dir = None
        if dx == 1: target_dir = DIR_E
        elif dx == -1: target_dir = DIR_W
        elif dy == 1: target_dir = DIR_S
        elif dy == -1: target_dir = DIR_N
        
        if target_dir is not None:
            if target_dir == self.direction:
                return 2 # Forward
            else:
                # Rotate toward it
                diff = (target_dir - self.direction + 4) % 4
                if diff == 1: return 1 # Right
                return 0 # Left
        return None
