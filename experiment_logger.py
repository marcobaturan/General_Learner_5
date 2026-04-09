"""
GL5.1 Dual-Bot: Experimental Framework Logger
=============================================

Logs emergent social behaviour metrics to experiment_log.csv for analysis.
This module implements the experimental framework specified in GL5.1,
enabling researchers to test hypotheses about emergent social interaction
between two autonomous cognitive agents.

Research Hypotheses Tested:
---------------------------
H1: Bots learn to avoid each other after repeated collisions (competition)
H2: Bots converge on opposite areas of the maze (territory formation)
H3: Bots show no learning from collisions (random behavior persists)
H4: Bots develop implicit cooperation (one charges while other explores)

Metrics Logged:
- collision_count: Total collisions per bot per session
- energy_delta_after_collision: Energy change following each collision
- battery_sharing_ratio: Percentage of batteries consumed by each bot
- proximity_events: Number of times bots are within 2 tiles of each other
- reset_trigger_count: How many times RESET_BUTTON was activated

Theoretical Foundation:
----------------------
This framework enables quantitative testing of emergent social behavior
predictions from:
- Schelling (1971): Segregation from local preferences
- Axelrod (1984): Cooperation from iterated interaction
- Reynolds (1987): Flocking from separation rules

Author: Marco
Collaborators: Claude Code, Antigravity, OpenCode Big Pickle
"""

import csv
import os
from datetime import datetime
from constants import IMPACT_UNITS

LOG_FILE = "experiment_log.csv"

METRIC_COLLISION = "collision"
METRIC_PROXIMITY = "proximity"
METRIC_RESET = "reset"
METRIC_BATTERY = "battery_collected"
METRIC_ENERGY = "energy_delta"


class ExperimentLogger:
    """
    Logs emergent social behaviour metrics for dual-bot experiments.

    This class maintains running counters for collisions, batteries collected,
    and reset triggers. Each event is also logged to a CSV file for
    post-hoc analysis. The logger is designed to have minimal performance
    impact on the main simulation loop.

    Attributes:
        _collision_count: Dict mapping bot_id to collision count
        _battery_count: Dict mapping bot_id to batteries collected
        _reset_count: Total number of maze resets triggered
    """

    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self._collision_count = {1: 0, 2: 0}
        self._battery_count = {1: 0, 2: 0}
        self._reset_count = 0
        self._init_log_file()

    def _init_log_file(self):
        """Creates log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "bot_id", "event_type", "value"])

    def log_event(self, bot_id: int, event_type: str, value: float):
        """Appends an event to the experiment log."""
        timestamp = datetime.now().isoformat()
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, bot_id, event_type, value])

    def log_collision(self, bot_id: int, energy_delta: int):
        """Logs a collision event between bots."""
        self._collision_count[bot_id] += 1
        self.log_event(bot_id, METRIC_COLLISION, energy_delta)

    def log_proximity_event(self, bot_id: int, distance: int):
        """Logs when bots are within 2 tiles of each other."""
        self.log_event(bot_id, METRIC_PROXIMITY, distance)

    def log_battery_collected(self, bot_id: int):
        """Logs when a bot collects a battery."""
        self._battery_count[bot_id] += 1
        self.log_event(bot_id, METRIC_BATTERY, self._battery_count[bot_id])

    def log_reset_trigger(self):
        """Logs when reset button is triggered."""
        self._reset_count += 1
        self.log_event(0, METRIC_RESET, self._reset_count)

    def log_energy_delta(self, bot_id: int, delta: int):
        """Logs energy change for a bot."""
        self.log_event(bot_id, METRIC_ENERGY, delta)

    def get_collision_count(self, bot_id: int) -> int:
        """Returns total collisions for a bot."""
        return self._collision_count[bot_id]

    def get_battery_count(self, bot_id: int) -> int:
        """Returns total batteries collected by a bot."""
        return self._battery_count[bot_id]

    def get_reset_count(self) -> int:
        """Returns total reset button triggers."""
        return self._reset_count

    def get_battery_sharing_ratio(self) -> dict:
        """Returns percentage of batteries collected by each bot."""
        total = sum(self._battery_count.values())
        if total == 0:
            return {1: 0.0, 2: 0.0}
        return {
            1: (self._battery_count[1] / total) * 100,
            2: (self._battery_count[2] / total) * 100,
        }
