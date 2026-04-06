# General Learner 4 - Cognitive Simulation

![Project Preview](preview.png)

An implementation of the **Universal Learner** concept based on the theories of Fritz et al. (1989). This simulation explores autonomous learning, situational awareness, and goal-oriented planning in a restricted 2D grid world.

## 🚀 Key Features

- **Autonomous Planning**: The robot doesn't just react to immediate stimuli; it uses BFS-based planning to find sequences of actions that lead to known rewards (Batteries).
- **Homeostatic Regulation**: The agent is driven by internal needs (Hunger and Tiredness). Tiredness triggers a "Dreaming" phase where episodic memories are consolidated into semantic rules.
- **Vicarious Learning (Guide Mode)**: Users can manually "teach" the robot by clicking on the grid, creating high-reward associations for specific paths.
- **Semantic Memory**: Uses a SQLite backend to store learned rules, including transitions ($S_1, A \rightarrow S_2$) and composite sequential patterns.
- **Visual Analytics**: Real-time feedback on current perceptions, active plans, and homeostasis levels.

## 🧠 Core Architecture

The system is modularized into specialized components:

1. **`learner.py`**: The cognitive core. Manages the decision engine (Planning vs. Reaction) and the Sleep Cycle (Consolidation).
2. **`memory.py`**: The persistent storage layer. Handles SQLite migrations and queries for Episodic and Semantic knowledge.
3. **`robot.py`**: The physical agent model. Manages movement, collisions, and internal biological variables.
4. **`environment.py`**: The world model. Handles procedural generation of obstacles and resources.
5. **`main.py`**: Orchestration and UI event handling using PyGame.

## 🛠️ Installation & Usage

1. **Requirements**: Python 3.11+, PyGame.
2. **Run**: 
   ```bash
   python main.py
   ```
3. **Controls**:
   - **Autonomous**: Toggles the agent's self-directed behavior.
   - **Guide Mode**: Click on tiles adjacent to the robot to lead it to a goal.
   - **Dream / Sleep**: Manually trigger rule consolidation (happens automatically when Tiredness reaches 50).
   - **Clear Memory**: Reset the SQLite database.

## 🧪 Experimentation Guide

- **Phase 1: Exploration**: Turn on Autonomous mode. The robot will move randomly, occasionally hitting walls or finding batteries.
- **Phase 2: Reinforcement**: Use the `+` and `-` buttons to give immediate feedback on the robot's last action in a specific situation.
- **Phase 3: Consolidation**: Let the robot "Sleep". You will see "New rules" in the console as it builds its internal world map.
- **Phase 4: Planning**: Once enough transitions are learned, the robot will display `ACTIVE PLAN` when it sees a situation it knows can lead to a battery.

---
*Developed by Antigravity AI for research in Intelligent Systems.*
