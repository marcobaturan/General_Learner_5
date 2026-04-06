import pygame
import sys
import json
import sqlite3
from constants import *
from environment import Environment
from robot import Robot
from memory import Memory
from learner import Learner
import graphics
from graphics import Button, TextBox, create_robot_icon, create_battery_icon, create_wall_icon

class GeneralLearnerApp:
    """
    Main Application class for the General Learner 4.
    Orchestrates the PyGame loop, UI events, and the simulation state.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("General Learner 4 - Cognitive Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 12)
        
        # Initialize Core Components
        self.env = Environment()
        self.memory = Memory()
        self.robot = Robot(self.env)
        self.learner = Learner(self.memory)
        
        self.autonomous = False
        self.guide_mode = False
        self.guide_path = [] # Visualization of the path being taught
        self.total_steps = 0
        self.stats_history = [] # Stores (step, score, rules_count)
        self.show_network = False 

        # Load Graphical Assets (Procedural Bitmaps)
        self.robot_img = create_robot_icon(CELL_SIZE)
        self.battery_img = create_battery_icon(CELL_SIZE)
        self.wall_img = create_wall_icon(CELL_SIZE)

        self.last_action_reward = 0
        self.timer = 0
        self.step_delay = 1500 # Even slower for maximum control (1.5 seconds)

        # UI Layout Setup
        self._init_buttons()

    def _init_buttons(self):
        btn_x = CANVAS_WIDTH + 20
        btn_w = PANEL_WIDTH - 40
        y_off = 20
        
        # Behavior Control
        self.btn_auto = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "AUTONOMOUS", GRAY)
        y_off += 40
        self.btn_comm = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "COMMAND", GRAY)
        y_off += 40
        
        # Direct Command Interface
        self.txt_box = TextBox(btn_x, y_off, btn_w, 25)
        y_off += 35
        self.btn_do = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DO ACTION", GRAY)
        y_off += 40
        
        # Manual Reinforcement
        self.btn_plus = Button(btn_x, y_off, btn_w//2 - 5, BTN_HEIGHT, "+", GREEN)
        self.btn_minus = Button(btn_x + btn_w//2 + 5, y_off, btn_w//2 - 5, BTN_HEIGHT, "-", RED)
        y_off += 40
        
        # Knowledge Management
        self.btn_sleep = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DREAM / SLEEP", BLUE)
        y_off += 40
        self.btn_export = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "EXPORT DATA", GRAY)
        y_off += 40
        self.btn_clear = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "CLEAR MEMORY", RED)
        y_off += 40
        
        # Vicarious Learning
        self.btn_guide = Button(btn_x, y_off, btn_w, 35, "GUIDE MODE", GRAY)
        y_off += 40
        
        # Control & Reporting Buttons
        self.btn_inform = Button(btn_x, y_off, btn_w, 35, "REPORT / INFORM", YELLOW)
        y_off += 40
        self.btn_network = Button(btn_x, y_off, btn_w, 35, "SHOW NETWORK", PURPLE)
        y_off += 40
        self.btn_bayes = Button(btn_x, y_off, btn_w, 35, "TOGGLE BAYES", CYAN)
        y_off += 40
        self.btn_pov = Button(btn_x, y_off, btn_w, 35, "TOGGLE POV", CYAN)

        # POV State
        self.show_pov = False

    def run(self):
        """Standard PyGame simulation loop."""
        running = True
        while running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        """
        - [x] Update `constants.py` with `LIGHT_ORANGE`
        - [x] Implement `decay_rules` in `memory.py`
        - [x] Integrate rule decay into `learner.py`'s `sleep_cycle`
        - [x] Update `main.py` with active-state UI coloring (Light Orange)
        - [x] Final verification and walkthrough
        - [x] Extensive English documentation for all core files:
            - [x] `memory.py`
            - [x] `learner.py`
            - [x] `environment.py`
            - [x] `robot.py`
            - [x] `main.py`
            - [x] `graphics.py`
        - [/] Finalize `README.md` with screenshot and architecture overview
        - [ ] Verify planning behavior in Autonomous mode
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Textbox interaction: only execute step IF 'cmd' is True (when user presses Enter)
            cmd = self.txt_box.handle_event(event)
            if cmd is True:
                self.execute_step()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # Check sidebar button clicks
                if self.btn_auto.is_clicked(pos):
                    self.autonomous = not self.autonomous
                    if self.autonomous: self.guide_mode = False # Mutually exclusive
                elif self.btn_comm.is_clicked(pos):
                    self.autonomous = False
                    self.guide_mode = False
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
                    self.memory.clear()
                    print("Memory wiped.")
                elif self.btn_guide.is_clicked(pos):
                    self.guide_mode = not self.guide_mode
                    if self.guide_mode: self.autonomous = False # Stop auto logic
                    if not self.guide_mode: self.guide_path = []
                elif self.btn_inform.is_clicked(pos):
                    self.export_report()
                elif self.btn_network.is_clicked(pos):
                    self.show_network = not self.show_network
                if self.btn_bayes.is_clicked(event.pos):
                    self.learner.bayesian = not self.learner.bayesian
                if self.btn_pov.is_clicked(event.pos):
                    self.show_pov = not self.show_pov

                # Grid interaction (Guide Mode)
                if pos[0] < CANVAS_WIDTH:
                    gx, gy = pos[0]//CELL_SIZE, pos[1]//CELL_SIZE
                    if self.guide_mode:
                        self.handle_guide_click(gx, gy)

    def execute_step(self):
        """Triggers the robot to perform a single step/decision cycle."""
        state = self.robot.get_state()
        action = self.learner.act(self.robot)
        reward = self.robot.step(action)
        
        self.memory.add_chrono(state['perception'], action, reward)
        self.last_action_reward = reward
        self.guide_path = []
        self.total_steps += 1
        
        # Synchronize stats for reports
        if self.total_steps % 5 == 0:
            self.capture_stats()

    def capture_stats(self):
        """Records current metrics for the reporting dashboard."""
        rules_count = len(self.memory.get_rules())
        self.stats_history.append({
            'step': self.total_steps,
            'score': self.robot.score,
            'rules': rules_count
        })

    def apply_manual_reinforcement(self, amount):
        """Forces reinforcement for the last taken action."""
        history = self.memory.get_all_chrono()
        if history:
            last = history[-1]
            self.memory.add_rule(json.loads(last['perception']), last['action'], weight=amount)
            print(f"Manual reinforcement applied: {amount}")

    def dream(self):
        """Triggers the Sleep Cycle for rules consolidation."""
        # 1. Consolidate new rules
        count = self.learner.sleep_cycle()
        
        # 2. Identify spatial landmarks to protect them from forgetting
        nodes, _ = self.learner.get_situational_graph()
        
        # 3. Apply biological forgetting (Differential Decay)
        self.memory.decay_rules(amount=1, spatial_perceptions=nodes)
        
        self.memory.clear_chrono()
        print(f"Dream complete: Consolidated {count} rules/transitions.")

    def export_db(self):
        """Exports the semantic memory (Rules) to a human-readable text file."""
        with open("db_export.txt", "w") as f:
            f.write("--- LEARNED COGNITIVE RULES ---\n")
            rules = self.memory.get_rules()
            for r in rules:
                trans = str(r['next_perception']) if r['next_perception'] else "None"
                f.write(f"ID: {r['id']} | Action: {r['target_action']} | Success: {r['weight']} | Transition: {trans}...\n")
        print("Knowledge exported to db_export.txt")

    def export_report(self):
        """Generates a text summary of the current learning performance."""
        with open("behavior_report.txt", "w") as f:
            f.write("--- COGNITIVE BEHAVIOR REPORT ---\n")
            f.write(f"Total Steps Simulated: {self.total_steps}\n")
            f.write(f"Final Score: {self.robot.score}\n")
            f.write(f"Knowledge Base Size: {len(self.memory.get_rules())} rules\n")
            f.write("-" * 34 + "\n")
            if self.stats_history:
                f.write("Growth History (Step | Score | Rules):\n")
                for s in self.stats_history:
                    f.write(f"Step {s['step']:04d} | Score {s['score']:04d} | Knowledge {s['rules']:03d}\n")
        print("Performance report exported to behavior_report.txt")

    def handle_guide_click(self, gx, gy):
        """Processes a grid click during Guide Mode to teach the robot a path."""
        action = self.robot.get_action_to(gx, gy)
        if action is not None:
            self.guide_path.append((gx, gy))
            state = self.robot.get_state()
            reward = self.robot.step(action)
            # Guided paths are automatically treated as high-reward examples (+10)
            self.memory.add_chrono(state['perception'], action, 10)

    def update(self, dt):
        """Continuous simulation updates and UI color state."""
        # 1. Update button visual states
        self.btn_auto.color = LIGHT_ORANGE if self.autonomous else GRAY
        self.btn_comm.color = ORANGE if not self.autonomous else GRAY
        self.btn_guide.color = LIGHT_ORANGE if self.guide_mode else GRAY

        if self.autonomous:
            self.timer += dt
            if self.timer >= self.step_delay:
                self.execute_step()
                self.timer = 0
        
        # Homeostasis check: If tired, robot must sleep (dream phase)
        if self.robot.tiredness >= TIREDNESS_MAX:
             print("Homeostasis Alert: Robot is exhausted. Triggering automatic Sleep phase...")
             self.dream()
             self.robot.tiredness = 0
             # Note: We NO LONGER reset the environment or robot position here.
             # This allows the user to see the robot waking up exactly where it was.

    def draw(self):
        """Renders the world and the sidebar HUD."""
        self.screen.fill(BLACK)
        
        # 1. Render World Grid & Objects
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (30, 35, 45), rect, 1)
                
                # Visual guide feedback
                if (x, y) in self.guide_path:
                    overlay = pygame.Surface((CELL_SIZE-2, CELL_SIZE-2))
                    overlay.set_alpha(120)
                    overlay.fill(PINK)
                    self.screen.blit(overlay, (x*CELL_SIZE+1, y*CELL_SIZE+1))

                val = self.env.grid[y][x]
                if val == WALL_ID: self.screen.blit(self.wall_img, rect)
                elif val == BATTERY_ID: self.screen.blit(self.battery_img, rect)

        # 2. Render Robot (with rotation based on direction)
        rob_rect = pygame.Rect(self.robot.x*CELL_SIZE, self.robot.y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rot_deg = {DIR_N: 0, DIR_E: -90, DIR_S: 180, DIR_W: 90}
        rotated_rob = pygame.transform.rotate(self.robot_img, rot_deg[self.robot.direction])
        self.screen.blit(rotated_rob, rob_rect)

        # 3. Sidebar Surface
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
        self.btn_inform.draw(self.screen)
        self.btn_network.draw(self.screen)
        self.btn_bayes.draw(self.screen)
        self.btn_pov.draw(self.screen)
        
        # 3. Cognitive Dashboard
        self.draw_reports()

        # 4. POV (3D Raycasting)
        if self.show_pov:
            # Position at the far right
            pov_rect = pygame.Rect(WINDOW_WIDTH - POV_WIDTH - 10, 150, POV_WIDTH, 400)
            graphics.draw_raycast_view(self.screen, pov_rect, self.robot, self.env)
 
        # 4. HUD Stats & Agenda
        bayes_status = "ENABLED" if self.learner.bayesian else "DISABLED"
        stats = f"Score: {self.robot.score}  Hunger: {self.robot.hunger}  BAYES: {bayes_status}"
        stat_surf = self.font.render(stats, True, BLACK)
        self.screen.blit(stat_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 70))
        
        # VISUOSPATIAL AGENDA (Mental Landmarks)
        agenda_title = self.font.render("VISUOSPATIAL AGENDA:", True, DARK_GRAY)
        self.screen.blit(agenda_title, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 50))
        
        if self.learner.agenda:
            for i, landmark in enumerate(self.learner.agenda[:5]):
                graphics.draw_mini_perception(self.screen, CANVAS_WIDTH + 10 + i*35, WINDOW_HEIGHT - 35, 30, landmark)
        
        if self.learner.active_plan:
            plan_text = f"ACTIVE PLAN: [{len(self.learner.active_plan)} steps]"
            plan_surf = self.font.render(plan_text, True, BLUE)
            self.screen.blit(plan_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 30))

        pygame.display.flip()

    def draw_reports(self):
        """Renders graphical charts or situational network to the right panel."""
        rep_x = CANVAS_WIDTH + PANEL_WIDTH + 20
        rep_w = REPORT_WIDTH - 40
        
        if self.show_network:
            # Render the Situational Map (World Map from Situations)
            nodes, edges = self.learner.get_situational_graph()
            net_rect = pygame.Rect(rep_x, 60, rep_w, 450)
            header_surf = pygame.font.SysFont('Arial', 20, bold=True).render("SITUATIONAL WORLD MAP", True, PURPLE)
            self.screen.blit(header_surf, (rep_x, 20))
            graphics.draw_situational_network(self.screen, net_rect, nodes, edges)
            return

        # Header
        header_surf = pygame.font.SysFont('Arial', 20, bold=True).render("COGNITIVE PERFORMANCE", True, CYAN)
        self.screen.blit(header_surf, (rep_x, 20))

        if not self.stats_history:
            msg = self.font.render("Simulating... Waiting for data points.", True, DARK_GRAY)
            self.screen.blit(msg, (rep_x, 60))
            return

        # Score Chart (Goals Achieved)
        chart_h = 180
        score_data = [s['score'] for s in self.stats_history]
        score_rect = pygame.Rect(rep_x, 60, rep_w, chart_h)
        graphics.draw_scaled_plot(self.screen, score_rect, score_data, GREEN, "GOALS ACHIEVED (Score Trend)", "S")

        # Knowledge Chart (Rules Learned)
        knowledge_data = [s['rules'] for s in self.stats_history]
        rules_rect = pygame.Rect(rep_x, 60 + chart_h + 30, rep_w, chart_h)
        graphics.draw_scaled_plot(self.screen, rules_rect, knowledge_data, PURPLE, "KNOWLEDGE BASE (Semantic Rules)", "R")

        # Session Insights
        insight_y = 60 + (chart_h + 30) * 2
        insights = [
            f"Learning Efficiency: {knowledge_data[-1] / (self.total_steps+1):.2f} rules/step",
            f"Average Reward: {score_data[-1] / (self.total_steps+1):.2f} pts/step",
            f"Total Exploratory Steps: {self.total_steps}"
        ]
        for i, text in enumerate(insights):
            surf = self.font.render(text, True, (180, 180, 180))
            self.screen.blit(surf, (rep_x, insight_y + i*20))

if __name__ == "__main__":
    app = GeneralLearnerApp()
    app.run()
