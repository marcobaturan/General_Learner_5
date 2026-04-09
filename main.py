import pygame
import sys
import json
import sqlite3
import psutil
import os
from constants import *
from environment import Environment
from robot import Robot
from memory import Memory
from learner import Learner
from experiment_logger import ExperimentLogger
import graphics
from graphics import (
    Button,
    TextBox,
    create_robot_icon,
    create_battery_icon,
    create_wall_icon,
    create_mirror_icon,
    create_reset_button_icon,
)


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
        self.font = pygame.font.SysFont("Arial", 12)

        # Initialize Core Components
        self.env = Environment()

        # Bot 1 (primary) - starts at center
        self.memory_bot1 = Memory("bot1_memory.db")
        self.robot1 = Robot(self.env, self_id=1)
        self.robot1.x = GRID_W // 2
        self.robot1.y = GRID_H // 2
        self.learner1 = Learner(self.memory_bot1, self.env)

        # Bot 2 (dual-bot) - starts offset from center to respect Pauli Exclusion
        self.memory_bot2 = Memory("bot2_memory.db")
        self.robot2 = Robot(self.env, self_id=2)
        self.robot2.x = GRID_W // 2
        self.robot2.y = GRID_H // 2 + 1  # Offset by 1 tile
        self.learner2 = Learner(self.memory_bot2, self.env)

        # Active bot selector
        self.active_bot = 1  # 1 or 2

        # Per-bot step tracking for experimental framework
        self.bot1_steps = 0
        self.bot2_steps = 0

        # GL5 Dual-Bot: Experimental framework logger (Spec 5)
        self.experiment_logger = ExperimentLogger()

        # Helper properties for active bot access
        self.last_action_reward = 0

        self.autonomous = False
        self.guide_mode = False
        self.guide_path = []  # Visualization of the path being taught
        self.total_steps = 0
        self.stats_history = []  # Stores (step, score, rules_count)
        self.show_network = False
        self.view_mode = "SITUATIONAL"  # 'SITUATIONAL' or 'TERRITORY'

        # Load Graphical Assets (Procedural Bitmaps)
        self.robot_img = create_robot_icon(CELL_SIZE)
        self.robot1_img = create_robot_icon(
            CELL_SIZE, (50, 100, 200)
        )  # Bot 1: darker blue
        self.robot2_img = create_robot_icon(CELL_SIZE, (200, 100, 50))  # Bot 2: orange
        self.battery_img = create_battery_icon(CELL_SIZE)
        self.wall_img = create_wall_icon(CELL_SIZE)
        self.mirror_img = create_mirror_icon(CELL_SIZE)
        self.reset_button_img = create_reset_button_icon(CELL_SIZE)

        self.last_action_reward = 0
        self.timer = 0
        self.step_delay = 500  # Autonomous mode step delay in ms

        # Dream/sleep cooldown to prevent overload
        self._dream_cooldown = 0
        self._in_dream = False

        # UI Layout Setup
        self._init_buttons()

        # Performance caching
        self._cache_timestamp = 0
        self._cache_rules = None
        self._cache_frames = None
        self._cache_graph = None
        self._cache_interval = 10  # Refresh every 10 frames

    def _init_buttons(self):
        btn_x = CANVAS_WIDTH + 20
        btn_w = PANEL_WIDTH - 40
        y_off = 20
        step_y = BTN_HEIGHT + BTN_MARGIN

        # Behavior Control
        self.btn_auto = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "AUTONOMOUS", GRAY)
        y_off += step_y
        self.btn_comm = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "COMMAND", GRAY)
        y_off += step_y

        # Direct Command Interface
        self.txt_box = TextBox(btn_x, y_off, btn_w, 25)
        y_off += 30
        self.btn_do = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DO ACTION", GRAY)
        y_off += step_y

        # Manual Reinforcement
        self.btn_plus = Button(btn_x, y_off, btn_w // 2 - 5, BTN_HEIGHT, "+", GREEN)
        self.btn_minus = Button(
            btn_x + btn_w // 2 + 5, y_off, btn_w // 2 - 5, BTN_HEIGHT, "-", RED
        )
        y_off += step_y

        # Knowledge Management
        self.btn_sleep = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DREAM / SLEEP", BLUE)
        y_off += step_y
        self.btn_clear = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "CLEAR MEMORY", RED)
        y_off += step_y

        # Vicarious Learning
        self.btn_guide = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "GUIDE MODE", GRAY)
        y_off += step_y

        # Control & Reporting Buttons
        self.btn_network = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "SHOW NETWORK", PURPLE
        )
        y_off += step_y
        self.btn_territory = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "TERRITORY MAP", BLUE
        )
        y_off += step_y
        self.btn_bayes = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "TOGGLE BAYES", CYAN)
        y_off += step_y
        self.btn_pov = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "TOGGLE POV", CYAN)
        y_off += step_y
        self.btn_inform = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "EXPORT REPORT", YELLOW
        )
        y_off += step_y
        self.btn_inferences = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "INFERENCES", ORANGE
        )
        y_off += step_y
        self.btn_new_maze = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "NEW MAZE", RED)
        y_off += step_y
        self.btn_reset_stagnation = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "RESET STAGNATION", PINK
        )
        y_off += step_y

        # GL5 Dual-Bot: Bot Selector Buttons (spec 4)
        self.btn_bot1 = Button(btn_x, y_off, btn_w // 2 - 5, BTN_HEIGHT, "BOT 1", GRAY)
        self.btn_bot2 = Button(
            btn_x + btn_w // 2 + 5, y_off, btn_w // 2 - 5, BTN_HEIGHT, "BOT 2", GRAY
        )

        # UI States
        self.show_pov = False
        self.show_inferences = False

    @property
    def robot(self):
        """Returns the active robot based on active_bot selection."""
        return self.robot1 if self.active_bot == 1 else self.robot2

    @property
    def memory(self):
        """Returns the active memory based on active_bot selection."""
        return self.memory_bot1 if self.active_bot == 1 else self.memory_bot2

    @property
    def learner(self):
        """Returns the active learner based on active_bot selection."""
        return self.learner1 if self.active_bot == 1 else self.learner2

    def get_active_robot(self):
        """Returns the active robot instance (for direct access)."""
        return self.robot1 if self.active_bot == 1 else self.robot2

    def get_other_robot(self):
        """Returns the other robot instance (for physics interaction)."""
        return self.robot2 if self.active_bot == 1 else self.robot1

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
                    if self.autonomous:
                        self.guide_mode = False  # Mutually exclusive
                elif self.btn_comm.is_clicked(pos):
                    self.autonomous = False
                    self.guide_mode = False
                elif self.btn_do.is_clicked(pos):
                    # Manual Step / Command Execution
                    self.execute_step()
                elif self.btn_plus.is_clicked(pos):
                    self.apply_manual_reinforcement(10)
                elif self.btn_minus.is_clicked(pos):
                    self.apply_manual_reinforcement(-10)
                elif self.btn_sleep.is_clicked(pos):
                    self.dream()
                elif self.btn_clear.is_clicked(pos):
                    self.memory.clear()
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Memory wiped.")
                elif self.btn_guide.is_clicked(pos):
                    self.guide_mode = not self.guide_mode
                    if self.guide_mode:
                        self.autonomous = False  # Stop auto logic
                    if not self.guide_mode:
                        self.guide_path = []
                elif self.btn_inform.is_clicked(pos):
                    self.export_report()
                elif self.btn_network.is_clicked(pos):
                    self.show_network = not self.show_network
                    self.view_mode = "SITUATIONAL"
                elif self.btn_territory.is_clicked(pos):
                    self.show_network = True
                    self.view_mode = "TERRITORY"
                if self.btn_bayes.is_clicked(event.pos):
                    self.learner.bayesian = not self.learner.bayesian
                if self.btn_pov.is_clicked(event.pos):
                    self.show_pov = not self.show_pov
                if self.btn_inferences.is_clicked(event.pos):
                    self.show_inferences = not self.show_inferences
                if self.btn_new_maze.is_clicked(event.pos):
                    self.env.reset()
                    self.robot.x, self.robot.y = GRID_W // 2, GRID_H // 2
                    self.robot.direction = DIR_N
                    self.learner.pos_history.clear()
                    self.learner.action_history.clear()
                    self.learner.active_plan.clear()
                    self._cache_graph = None
                    print("Maze regenerated and robot position reset.")
                if self.btn_reset_stagnation.is_clicked(event.pos):
                    self.learner.stagnant = False
                    self.learner.pos_history.clear()
                    self.learner.action_history.clear()
                    self.learner.active_plan.clear()
                    self.learner.agenda.clear()
                    print("Stagnation reset! Robot is free to move again.")

                # GL5 Dual-Bot: Bot selector buttons (Spec 4)
                if self.btn_bot1.is_clicked(event.pos):
                    self.active_bot = 1
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Switched to Bot 1")
                elif self.btn_bot2.is_clicked(event.pos):
                    self.active_bot = 2
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Switched to Bot 2")

                # Grid interaction (Guide Mode)
                if pos[0] < CANVAS_WIDTH and pos[1] < CANVAS_HEIGHT:
                    gx, gy = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        if self.guide_mode:
                            self.handle_guide_click(gx, gy)

    def execute_step(self, forced_action=None):
        """Triggers the robot to perform a single step/decision cycle."""
        text_cmd = self.txt_box.text.strip() if self.txt_box.text else None

        # Check if guided (forced action = guided mode)
        is_guided = forced_action is not None
        if is_guided:
            self.learner._guided_this_step = True
        else:
            self.learner._guided_this_step = False

        other_robot = self.robot2 if self.active_bot == 1 else self.robot1
        state = self.robot.get_state(other_robot)

        # Determine action: either the user-forced one (Guided) or the learner's act
        if forced_action is not None:
            action = forced_action
        else:
            action = self.learner.act(
                self.robot, text_command=text_cmd, other_bot=other_robot
            )

        reward = self.robot.step(action, other_robot)

        # GL5 Dual-Bot: Check if all batteries consumed → spawn reset button
        if self.env.count_batteries() == 0 and self.env.reset_button_pos is None:
            self.env.spawn_reset_button()

        # GL5 Dual-Bot: Check if robot stepped on reset button → respawn batteries
        current_tile = self.env.get_at(self.robot.x, self.robot.y)
        if current_tile == RESET_BUTTON_ID:
            self.env.respawn_batteries()
            print("Maze reset! Batteries respawned.")
            # GL5 Dual-Bot: Log reset trigger (Spec 5)
            self.experiment_logger.log_reset_trigger()

        # GL5 Dual-Bot: Log battery collection (Spec 5)
        if current_tile == BATTERY_ID:
            active_robot = self.robot1 if self.active_bot == 1 else self.robot2
            self.experiment_logger.log_battery_collected(active_robot.self_id)

        # GL5 Dual-Bot: Log collision events in manual mode (Spec 3 & 5)
        if getattr(self.robot, "last_collision", False):
            self.experiment_logger.log_collision(self.active_bot, -IMPACT_UNITS)
            self.experiment_logger.log_energy_delta(self.active_bot, -IMPACT_UNITS)

        # GL5 Dual-Bot: Log proximity events (within 2 tiles)
        dist = abs(self.robot.x - other_robot.x) + abs(self.robot.y - other_robot.y)
        if dist <= 2:
            self.experiment_logger.log_proximity_event(self.active_bot, dist)

        # 3. USE THE NEW AGNOSTIC LEARNING FLOW
        self.learner.learn(
            self.robot, action, reward, text_command=text_cmd, other_bot=other_robot
        )

        self.last_action_reward = reward
        self.guide_path = []
        self.total_steps += 1

        # Invalidate cache after learning
        self._cache_rules = None

        # Synchronize stats for reports
        if self.total_steps % 5 == 0:
            self.capture_stats()

    def _execute_bot_step(self, bot_id):
        """
        Executes a step for a specific bot in autonomous mode.

        Args:
            bot_id: 1 or 2, indicating which bot to step
        """
        robot = self.robot1 if bot_id == 1 else self.robot2
        other_robot = self.robot2 if bot_id == 1 else self.robot1
        memory = self.memory_bot1 if bot_id == 1 else self.memory_bot2
        learner = self.learner1 if bot_id == 1 else self.learner2

        # Get action from learner (pass other_bot for collision-aware perception)
        action = learner.act(robot, other_bot=other_robot)

        # Execute step with other bot for collision detection (Pauli Exclusion)
        reward = robot.step(action, other_robot)

        # GL5 Dual-Bot: Check if all batteries consumed → spawn reset button
        if self.env.count_batteries() == 0 and self.env.reset_button_pos is None:
            self.env.spawn_reset_button()

        # GL5 Dual-Bot: Check if robot stepped on reset button → respawn batteries
        current_tile = self.env.get_at(robot.x, robot.y)
        if current_tile == RESET_BUTTON_ID:
            self.env.respawn_batteries()
            print(f"Bot {bot_id} triggered maze reset! Batteries respawned.")
            # GL5 Dual-Bot: Log reset trigger (Spec 5)
            self.experiment_logger.log_reset_trigger()

        # GL5 Dual-Bot: Log battery collection (Spec 5)
        if current_tile == BATTERY_ID:
            self.experiment_logger.log_battery_collected(robot.self_id)

        # GL5 Dual-Bot: Log collision events (Spec 3 & 5)
        if getattr(robot, "last_collision", False):
            self.experiment_logger.log_collision(bot_id, -IMPACT_UNITS)
            self.experiment_logger.log_energy_delta(bot_id, -IMPACT_UNITS)

        # GL5 Dual-Bot: Log proximity events (within 2 tiles)
        dist = abs(robot.x - other_robot.x) + abs(robot.y - other_robot.y)
        if dist <= 2:
            self.experiment_logger.log_proximity_event(bot_id, dist)

        # Learn
        learner.learn(robot, action, reward, other_bot=other_robot)

        # Update step counts
        if bot_id == 1:
            self.bot1_steps += 1
        else:
            self.bot2_steps += 1
        self.total_steps += 1

    def capture_stats(self):
        """Records current metrics for the reporting dashboard."""
        rules_count = len(self._cache_rules) if self._cache_rules is not None else 0
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        cpu_percent = process.cpu_percent()
        self.stats_history.append(
            {
                "step": self.total_steps,
                "score": self.robot.score,
                "rules": rules_count,
                "memory_mb": round(mem_mb, 1),
                "cpu_percent": round(cpu_percent, 1),
            }
        )

    def apply_manual_reinforcement(self, amount):
        """Forces reinforcement for the last taken action using conceptual IDs."""
        history = self.memory.get_all_chrono()
        if history:
            last = history[-1]
            perc_id = json.dumps(last["perception"])
            cmd_id = None
            if last.get("command_text"):
                cmd_id = self.memory.get_or_create_concept_id(
                    last["command_text"].upper()
                )

            self.memory.add_rule(
                perc_id, last["action"], weight=amount, command_id=cmd_id
            )
            print(f"Manual reinforcement applied: {amount}")
            self._cache_rules = None

    def dream(self):
        """Triggers the Sleep Cycle for rules consolidation."""
        if self._in_dream:
            print("Dream already in progress, skipping...")
            return

        self._in_dream = True

        # 1. Consolidate new rules
        count = self.learner.sleep_cycle()

        # 2. Identify spatial landmarks to protect them from forgetting
        nodes, _ = self.learner.get_situational_graph()

        # 3. Apply biological forgetting (Differential Decay)
        self.memory.decay_rules()

        self.memory.clear_chrono()
        print(f"Dream complete: Consolidated {count} rules/transitions.")

        self._in_dream = False
        self._dream_cooldown = 60

    def export_db(self):
        """Exports the semantic memory (Rules) to a human-readable text file."""
        with open("db_export.txt", "w") as f:
            f.write("--- LEARNED COGNITIVE RULES ---\n")
            rules = self.memory.get_rules()
            for r in rules:
                trans = str(r["next_perception"]) if r["next_perception"] else "None"
                f.write(
                    f"ID: {r['id']} | Action: {r['target_action']} | Success: {r['weight']} | Transition: {trans}...\n"
                )
        print("Knowledge exported to db_export.txt")

    def export_report(self):
        """Generates a comprehensive research-quality report of the learning performance."""
        import datetime
        from constants import MEMORY_EPISODIC, MEMORY_SEMANTIC, MEMORY_DERIVED

        rules = self.memory.get_rules()

        # Memory breakdown by type
        episodic = [r for r in rules if r.get("memory_type") == MEMORY_EPISODIC]
        semantic = [r for r in rules if r.get("memory_type") == MEMORY_SEMANTIC]
        derived = [r for r in rules if r.get("memory_type") == MEMORY_DERIVED]

        # Weight statistics
        weights = [r["weight"] for r in rules]
        avg_weight = sum(weights) / len(weights) if weights else 0
        max_weight = max(weights) if weights else 0
        min_weight = min(weights) if weights else 0

        # Action distribution
        action_counts = {}
        for r in rules:
            a = r["target_action"]
            action_counts[a] = action_counts.get(a, 0) + 1
        action_names = {0: "A0", 1: "A1", 2: "A2", 3: "A3"}

        # Learning curve analysis
        score_data = [s["score"] for s in self.stats_history]
        rule_data = [s["rules"] for s in self.stats_history]

        # Efficiency metrics
        if self.total_steps > 0:
            score_per_step = self.robot.score / self.total_steps
            rules_per_step = len(rules) / self.total_steps
        else:
            score_per_step = 0
            rules_per_step = 0

        # RFT frames
        frames = self.memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]
        opp_frames = [f for f in frames if f["relation_type"] == "OPP"]

        with open("behavior_report.txt", "w") as f:
            f.write("=" * 60 + "\n")
            f.write("       GENERAL LEARNER 4/5 - RESEARCH REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Session Duration: {self.total_steps} steps\n")
            f.write("-" * 60 + "\n")

            f.write("\n### EXECUTIVE SUMMARY\n")
            f.write(f"  Total Steps:         {self.total_steps}\n")
            f.write(f"  Final Score:        {self.robot.score}\n")
            f.write(f"  Total Rules:         {len(rules)}\n")
            f.write(f"  Battery Found:      {self.robot.score // 10} units\n")

            f.write("\n### MEMORY HIERARCHY\n")
            f.write(
                f"  Episodic (short-term):  {len(episodic):4d} rules  (fast decay)\n"
            )
            f.write(
                f"  Semantic (long-term):   {len(semantic):4d} rules  (slow decay)\n"
            )
            f.write(f"  Derived (RFT-inferred): {len(derived):4d} rules  (GL5)\n")

            f.write("\n### RULE STATISTICS\n")
            f.write(f"  Avg Weight:    {avg_weight:+.2f}\n")
            f.write(f"  Max Weight:    {max_weight:+.2f}\n")
            f.write(f"  Min Weight:    {min_weight:+.2f}\n")

            f.write("\n### ACTION DISTRIBUTION\n")
            for act, count in sorted(action_counts.items()):
                name = action_names.get(act, f"ACT_{act}")
                pct = (count / len(rules) * 100) if rules else 0
                f.write(f"  {name:8s}: {count:4d} ({pct:5.1f}%)\n")

            f.write("\n### LEARNING EFFICIENCY\n")
            f.write(f"  Score/Step:    {score_per_step:.4f}\n")
            f.write(f"  Rules/Step:    {rules_per_step:.4f}\n")
            f.write(f"  Exploration:   {self.total_steps - self.robot.score} steps\n")

            f.write("\n### RFT NETWORK (GL5)\n")
            f.write(f"  Total Frames:      {len(frames)}\n")
            f.write(f"  Coordination:      {len(coord_frames)}\n")
            f.write(f"  Opposition:        {len(opp_frames)}\n")

            f.write("\n### HOMEOSTASIS\n")
            f.write(f"  Final Hunger:      {self.robot.hunger}\n")
            f.write(f"  Final Tiredness:   {self.robot.tiredness}\n")
            f.write(
                f"  Bayesian Mode:     {'ENABLED' if self.learner.bayesian else 'DISABLED'}\n"
            )
            f.write(
                f"  Autonomous Mode:   {'ACTIVE' if self.autonomous else 'INACTIVE'}\n"
            )
            f.write(
                f"  Guide Mode:        {'ACTIVE' if self.guide_mode else 'INACTIVE'}\n"
            )

            f.write("\n### GROWTH TRAJECTORY\n")
            if len(score_data) >= 2:
                f.write(f"  Initial Score: {score_data[0]}\n")
                f.write(f"  Final Score:   {score_data[-1]}\n")
                f.write(f"  Initial Rules: {rule_data[0]}\n")
                f.write(f"  Peak Rules:    {max(rule_data)}\n")
                f.write(f"  Final Rules:   {rule_data[-1]}\n")

            f.write("\n### TIME SERIES (Step | Score | Rules)\n")
            f.write("-" * 40 + "\n")
            if self.stats_history:
                # Show sampled data points (every 10th)
                for i, s in enumerate(self.stats_history):
                    if i % 10 == 0:
                        f.write(
                            f"  {s['step']:04d} | {s['score']:04d} | {s['rules']:03d}\n"
                        )

            f.write("\n" + "=" * 60 + "\n")
            f.write("                    END OF REPORT\n")
            f.write("=" * 60 + "\n")

        print("Performance report exported to behavior_report.txt")

    def handle_guide_click(self, gx, gy):
        """
        Processes a grid click during Guide Mode.
        FORCED: Immediately moves the robot and associates text.
        """
        target_action = self.robot.get_action_to(gx, gy)
        if target_action is not None:
            # Immediate forced movement
            self.execute_step(forced_action=target_action)
            # Add visual feedback for the clicked target (briefly)
            self.guide_path = [(gx, gy)]

    def update(self, dt):
        """Continuous simulation updates and UI color state."""
        # 1. Update button visual states
        self.btn_auto.color = LIGHT_ORANGE if self.autonomous else GRAY
        self.btn_comm.color = ORANGE if not self.autonomous else GRAY
        self.btn_guide.color = LIGHT_ORANGE if self.guide_mode else GRAY
        self.btn_bayes.text = "BAYES: ON" if self.learner.bayesian else "BAYES: OFF"
        self.btn_bayes.color = LIGHT_ORANGE if self.learner.bayesian else GRAY

        if self.autonomous:
            self.timer += dt
            if self.timer >= self.step_delay:
                # GL5 Dual-Bot: Both bots take turns in autonomous mode
                # Execute step for both bots each cycle
                self._execute_bot_step(1)
                self._execute_bot_step(2)
                # Note: Display stays on manually selected bot (no auto-switch)
                self.timer = 0

        # Decrement dream cooldown
        if self._dream_cooldown > 0:
            self._dream_cooldown -= 1

        # Homeostasis check: If tired, active robot must sleep (dream phase)
        if self.robot.tiredness >= TIREDNESS_MAX and self._dream_cooldown == 0:
            print(
                "Homeostasis Alert: Robot is exhausted. Triggering automatic Sleep phase..."
            )
            self.dream()
            self.robot.tiredness = 0

    def draw(self):
        """Renders the world and the sidebar HUD."""
        self.screen.fill(BLACK)

        # 1. Render World Grid & Objects
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (30, 35, 45), rect, 1)

                # Visual guide feedback
                if (x, y) in self.guide_path:
                    overlay = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2))
                    overlay.set_alpha(120)
                    overlay.fill(PINK)
                    self.screen.blit(overlay, (x * CELL_SIZE + 1, y * CELL_SIZE + 1))

                val = self.env.grid[y][x]
                if val == WALL_ID:
                    self.screen.blit(self.wall_img, rect)
                elif val == BATTERY_ID:
                    self.screen.blit(self.battery_img, rect)
                elif val == MIRROR_ID:
                    self.screen.blit(self.mirror_img, rect)
                elif val == RESET_BUTTON_ID:
                    self.screen.blit(self.reset_button_img, rect)

        # 2. Render Robot 1 (with rotation based on direction)
        r1 = self.robot1
        r1_rect = pygame.Rect(r1.x * CELL_SIZE, r1.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rot_deg = {DIR_N: 0, DIR_E: -90, DIR_S: 180, DIR_W: 90}
        rotated_r1 = pygame.transform.rotate(self.robot1_img, rot_deg[r1.direction])
        self.screen.blit(rotated_r1, r1_rect)

        # 2b. Render Robot 2 (with rotation based on direction)
        r2 = self.robot2
        r2_rect = pygame.Rect(r2.x * CELL_SIZE, r2.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rotated_r2 = pygame.transform.rotate(self.robot2_img, rot_deg[r2.direction])
        self.screen.blit(rotated_r2, r2_rect)

        # 3. Sidebar Surface
        pygame.draw.rect(
            self.screen, LIGHT_GRAY, (CANVAS_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        )
        self.btn_auto.draw(self.screen)
        self.btn_comm.draw(self.screen)
        self.txt_box.draw(self.screen)
        self.btn_do.draw(self.screen)
        self.btn_plus.draw(self.screen)
        self.btn_minus.draw(self.screen)
        self.btn_sleep.draw(self.screen)
        self.btn_clear.draw(self.screen)
        self.btn_guide.draw(self.screen)
        self.btn_inform.draw(self.screen)
        self.btn_network.draw(self.screen)
        self.btn_territory.draw(self.screen)
        self.btn_bayes.draw(self.screen)
        self.btn_pov.draw(self.screen)
        self.btn_inferences.draw(self.screen)
        self.btn_new_maze.draw(self.screen)
        self.btn_reset_stagnation.draw(self.screen)

        # GL5 Dual-Bot: Bot selector buttons (Spec 4)
        self.btn_bot1.color = LIGHT_ORANGE if self.active_bot == 1 else GRAY
        self.btn_bot2.color = LIGHT_ORANGE if self.active_bot == 2 else GRAY
        self.btn_bot1.draw(self.screen)
        self.btn_bot2.draw(self.screen)

        # 3. Cognitive Dashboard
        self.draw_reports()

        # 4. POV (3D Raycasting) - Positioned to the right of cognitive performance
        if self.show_pov:
            rep_x = CANVAS_WIDTH + PANEL_WIDTH + 10
            rep_w = REPORT_WIDTH - 30
            pov_rect = pygame.Rect(rep_x + rep_w + 10, 60, POV_WIDTH, POV_HEIGHT)
            graphics.draw_raycast_view(
                self.screen,
                pov_rect,
                self.robot,
                self.env,
                self.learner,
                other_bot=self.robot2 if self.active_bot == 1 else self.robot1,
                active_bot=self.active_bot,
            )

        # 4. HUD Stats & Agenda (with caching - only update when needed)
        if self._cache_rules is None:
            self._cache_rules = self.memory.get_rules()
            self._cache_frames = self.memory.get_all_frames()
            self._cache_graph = self.learner.get_situational_graph()
            self._cache_timestamp = self.total_steps

        rules_count = len(self._cache_rules) if self._cache_rules else 0
        rft_count = len(self._cache_frames) if self._cache_frames else 0
        bayes_status = "ENABLED" if self.learner.bayesian else "DISABLED"
        auto_status = "AUTO" if self.autonomous else "MANUAL"
        guide_status = "GUIDE" if self.guide_mode else "FREE"

        # GL5 Dual-Bot: Include bot ID in stats
        stats = f"Bot{self.active_bot} | Score: {self.robot.score} | Rules: {rules_count} | BAYES: {bayes_status} | {auto_status} | {guide_status} | RFT: {rft_count}"
        stat_surf = self.font.render(stats, True, BLACK)
        self.screen.blit(stat_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 70))

        # VISUOSPATIAL AGENDA (Mental Landmarks)
        agenda_title = self.font.render("VISUOSPATIAL AGENDA:", True, DARK_GRAY)
        self.screen.blit(agenda_title, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 50))

        if self.learner.agenda:
            for i, landmark in enumerate(self.learner.agenda[:5]):
                graphics.draw_mini_perception(
                    self.screen,
                    CANVAS_WIDTH + 10 + i * 35,
                    WINDOW_HEIGHT - 35,
                    30,
                    landmark,
                )

        if self.learner.active_plan:
            plan_text = f"ACTIVE PLAN: [{len(self.learner.active_plan)} steps]"
            plan_surf = self.font.render(plan_text, True, BLUE)
            self.screen.blit(plan_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 30))

        # 5. Inferences Sub-Window (Below 2D World)
        if self.show_inferences:
            inf_rect = pygame.Rect(10, CANVAS_HEIGHT + 15, CANVAS_WIDTH - 20, 250)
            graphics.draw_inferences_window(
                self.screen, inf_rect, self.learner, self.robot
            )

        pygame.display.flip()

    def draw_reports(self):
        """Renders graphical charts or situational network to the right panel."""
        rep_x = CANVAS_WIDTH + PANEL_WIDTH + 10
        rep_w = REPORT_WIDTH - 30

        if self.show_network:
            rep_rect = pygame.Rect(rep_x, 60, rep_w, 450)
            if self.view_mode == "SITUATIONAL":
                if self._cache_graph:
                    nodes, edges = self._cache_graph
                else:
                    nodes, edges = self.learner.get_situational_graph()
                header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
                    "SITUATIONAL WORLD MAP", True, PURPLE
                )
                self.screen.blit(header_surf, (rep_x, 20))
                graphics.draw_situational_network(
                    self.screen, rep_rect, nodes, edges, self.memory
                )
            else:
                territory = self.memory.get_territory()
                header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
                    "GLOBAL TERRITORY MAP", True, BLUE
                )
                self.screen.blit(header_surf, (rep_x, 20))
                graphics.draw_territory_map(self.screen, rep_rect, territory)
            return

        # Header
        header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
            "COGNITIVE PERFORMANCE", True, CYAN
        )
        self.screen.blit(header_surf, (rep_x, 20))

        if not self.stats_history:
            msg = self.font.render(
                "Simulating... Waiting for data points.", True, DARK_GRAY
            )
            self.screen.blit(msg, (rep_x, 60))
            return

        # Score Chart (Goals Achieved)
        chart_h = 180
        score_data = [s["score"] for s in self.stats_history]
        score_rect = pygame.Rect(rep_x, 60, rep_w, chart_h)
        graphics.draw_scaled_plot(
            self.screen,
            score_rect,
            score_data,
            GREEN,
            "GOALS ACHIEVED (Score Trend)",
            "S",
        )

        # Knowledge Chart (Rules Learned)
        knowledge_data = [s["rules"] for s in self.stats_history]
        rules_rect = pygame.Rect(rep_x, 60 + chart_h + 30, rep_w, chart_h)
        graphics.draw_scaled_plot(
            self.screen,
            rules_rect,
            knowledge_data,
            PURPLE,
            "KNOWLEDGE BASE (Semantic Rules)",
            "R",
        )

        # Resource Monitor (Memory & CPU)
        mem_data = [s.get("memory_mb", 0) for s in self.stats_history]
        cpu_data = [s.get("cpu_percent", 0) for s in self.stats_history]
        res_rect = pygame.Rect(rep_x, 60 + (chart_h + 30) * 2, rep_w, 100)
        graphics.draw_resource_monitor(self.screen, res_rect, mem_data, cpu_data)

        # Session Insights
        insight_y = 60 + (chart_h + 30) * 3
        insights = [
            f"Learning Efficiency: {knowledge_data[-1] / (self.total_steps + 1):.2f} rules/step",
            f"Average Reward: {score_data[-1] / (self.total_steps + 1):.2f} pts/step",
            f"Total Exploratory Steps: {self.total_steps}",
            f"Memory: {mem_data[-1]:.1f} MB | CPU: {cpu_data[-1]:.1f}%",
        ]
        for i, text in enumerate(insights):
            surf = self.font.render(text, True, (180, 180, 180))
            self.screen.blit(surf, (rep_x, insight_y + i * 20))


if __name__ == "__main__":
    app = GeneralLearnerApp()
    app.run()
