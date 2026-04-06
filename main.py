import pygame
import sys
import json
from constants import *
from environment import Environment
from robot import Robot
from memory import Memory
from learner import Learner
from graphics import Button, TextBox, create_robot_icon, create_battery_icon, create_wall_icon

class GeneralLearnerApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("General Learner 4 - Cognitive Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 12) # Smaller font

        self.env = Environment()
        self.memory = Memory()
        self.robot = Robot(self.env)
        self.learner = Learner(self.memory)
        
        # Migration: Add is_composite if not exists
        try:
            self.memory.conn.execute("ALTER TABLE rules ADD COLUMN is_composite INTEGER DEFAULT 0")
            self.memory.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        self.autonomous = False
        self.guide_mode = False
        self.guide_path = [] # List of (gx, gy) coordinates for visual feedback

        # Assets
        self.robot_img = create_robot_icon(CELL_SIZE)
        self.battery_img = create_battery_icon(CELL_SIZE)
        self.wall_img = create_wall_icon(CELL_SIZE)

        # UI State
        self.last_action_reward = 0
        self.timer = 0
        self.step_delay = 500  # ms for autonomous steps

        # Buttons
        btn_x = CANVAS_WIDTH + 20
        btn_w = PANEL_WIDTH - 40
        y_off = 50
        
        self.btn_auto = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "AUTONOMOUS", GRAY)
        y_off += 45
        self.btn_comm = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "COMMAND", GRAY)
        y_off += 50
        
        self.txt_box = TextBox(btn_x, y_off, btn_w, 25)
        y_off += 35
        self.btn_do = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DO ACTION", GRAY)
        y_off += 45
        
        self.btn_plus = Button(btn_x, y_off, btn_w//2 - 5, BTN_HEIGHT, "+", GREEN)
        self.btn_minus = Button(btn_x + btn_w//2 + 5, y_off, btn_w//2 - 5, BTN_HEIGHT, "-", RED)
        y_off += 45
        
        self.btn_sleep = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DREAM / SLEEP", BLUE)
        y_off += 45
        self.btn_export = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "EXPORT DATA", GRAY)
        y_off += 45
        self.btn_clear = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "CLEAR MEMORY", RED)
        y_off += 45
        self.btn_guide = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "GUIDE MODE", GRAY)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Textbox events
            if self.txt_box.handle_event(event):
                # If Enter is pressed in text box
                self.execute_step()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # Mode Buttons
                if self.btn_auto.is_clicked(pos):
                    self.autonomous = not self.autonomous
                    self.btn_auto.color = GREEN if self.autonomous else GRAY
                    if self.autonomous: self.learner.mode = "AUTONOMOUS"

                elif self.btn_comm.is_clicked(pos):
                    self.learner.mode = "COMMAND"
                    self.autonomous = False
                    self.btn_auto.color = GRAY
                
                # Action Buttons
                elif self.btn_do.is_clicked(pos):
                    self.execute_step()
                elif self.btn_plus.is_clicked(pos):
                    self.apply_manual_reinforcement(10)
                elif self.btn_minus.is_clicked(pos):
                    self.apply_manual_reinforcement(-10)
                elif self.btn_sleep.is_clicked(pos):
                    self.dream()
                elif self.btn_export.is_clicked(pos):
                    self.export_db()
                elif self.btn_clear.is_clicked(pos):
                    self.memory.clear_rules()
                    self.memory.clear_chrono()
                    print("Memory cleared.")
                elif self.btn_guide.is_clicked(pos):
                    self.guide_mode = not self.guide_mode
                    self.btn_guide.color = ORANGE if self.guide_mode else GRAY
                    if not self.guide_mode:
                        self.guide_path = []

                # Grid interaction for Guide Mode
                elif pos[0] < CANVAS_WIDTH:
                    gx, gy = pos[0]//CELL_SIZE, pos[1]//CELL_SIZE
                    if self.guide_mode:
                        self.handle_guide_click(gx, gy)

    def execute_step(self):
        # In command mode, we can use the text from the box to influence the learner (simple association)
        # For now, it just triggers an action from the learner
        state = self.robot.get_state()
        action = self.learner.act(self.robot)
        reward = self.robot.step(action)
        self.memory.add_chrono(json.dumps(state['perception']), action, reward)
        self.last_action_reward = reward
        # Reset guide path when a 'real' step is executed
        self.guide_path = []

    def apply_manual_reinforcement(self, amount):
        history = self.memory.get_all_chrono()
        if history:
            last = history[-1]
            self.memory.add_rule(json.loads(last['perception']), last['action'], weight=amount)
            print(f"Manually reinforced last action with {amount}")

    def dream(self):
        new_rules = self.learner.sleep_cycle()
        print(f"Dream finished. New rules: {new_rules}")

    def export_db(self):
        with open("db_export.txt", "w") as f:
            f.write("--- LEARNED RULES ---\n")
            cur = self.memory.conn.cursor()
            cur.execute("SELECT * FROM rules ORDER BY weight DESC")
            for row in cur.fetchall():
                f.write(f"ID: {row['id']} | Action: {row['target_action']} | Weight: {row['weight']} | Composite: {row['is_composite']} | Pattern: {row['perception_pattern']}\n")
        print("Knowledge exported to db_export.txt")

    def handle_guide_click(self, gx, gy):
        action = self.robot.get_action_to(gx, gy)
        if action is not None:
            # Store in sequence
            self.guide_path.append((gx, gy))
            # Execute immediately as a "guided step"
            state = self.robot.get_state()
            reward = self.robot.step(action)
            # High reward association for guided steps
            self.memory.add_chrono(json.dumps(state['perception']), action, 10)
            self.last_action_reward = 10

    def update(self, dt):
        if self.autonomous:
            self.timer += dt
            if self.timer >= self.step_delay:
                self.execute_step()
                self.timer = 0
        
        if self.robot.tiredness >= TIREDNESS_MAX:
             print("Robot is tired, going to sleep.")
             self.dream()
             self.robot.tiredness = 0
             self.robot.reset()
             self.env.reset()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw Grid
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)
                
                # Render Guide Path
                if (x, y) in self.guide_path:
                    # Draw a semi-transparent pink rectangle
                    s = pygame.Surface((CELL_SIZE-2, CELL_SIZE-2))
                    s.set_alpha(150)
                    s.fill(PINK)
                    self.screen.blit(s, (x*CELL_SIZE+1, y*CELL_SIZE+1))

                val = self.env.grid[y][x]
                if val == WALL_ID:
                    self.screen.blit(self.wall_img, rect)
                elif val == BATTERY_ID:
                    self.screen.blit(self.battery_img, rect)

        # Draw Robot
        rob_rect = pygame.Rect(self.robot.x*CELL_SIZE, self.robot.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rot_deg = {DIR_N: 0, DIR_E: -90, DIR_S: 180, DIR_W: 90}
        rotated_rob = pygame.transform.rotate(self.robot_img, rot_deg[self.robot.direction])
        self.screen.blit(rotated_rob, rob_rect)

        # Draw Sidebar
        pygame.draw.rect(self.screen, LIGHT_GRAY, (CANVAS_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        self.btn_auto.draw(self.screen)
        self.btn_comm.draw(self.screen)
        self.txt_box.draw(self.screen)
        self.btn_do.draw(self.screen)
        self.btn_plus.draw(self.screen)
        self.btn_minus.draw(self.screen)
        self.btn_sleep.draw(self.screen)
        self.btn_export.draw(self.screen)
        self.btn_clear.draw(self.screen)
        self.btn_guide.draw(self.screen)

        # HUD / Status
        stats = f"Score: {self.robot.score}  Tired: {self.robot.tiredness}/{TIREDNESS_MAX}  Hunger: {self.robot.hunger}/{HUNGER_MAX}"
        stat_surf = self.font.render(stats, True, BLACK)
        self.screen.blit(stat_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 30))

        pygame.display.flip()

if __name__ == "__main__":
    app = GeneralLearnerApp()
    app.run()
