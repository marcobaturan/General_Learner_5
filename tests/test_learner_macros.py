import unittest
import sys
import json
import os
import sqlite3
# Adjust path to import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory import Memory
from learner import Learner
from robot import Robot
from environment import Environment
from constants import *

class TestLearnerMacros(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_general_learner.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.memory = Memory(self.db_path)
        self.env = Environment()
        self.robot = Robot(self.env)
        self.learner = Learner(self.memory)

    def tearDown(self):
        self.memory.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_macro_induction(self):
        """Tests that sequences under the same command are turned into macros during sleep."""
        # Simulate a sequence of 3 actions under 'L-SHAPE'
        perception = self.env.get_perception_at(5, 5, DIR_N)
        self.memory.add_chrono(perception, ACT_FORWARD, 0, "L-SHAPE")
        self.memory.add_chrono(perception, ACT_FORWARD, 0, "L-SHAPE")
        self.memory.add_chrono(perception, ACT_RIGHT, 0, "L-SHAPE")
        
        # Consolidation
        self.learner.sleep_cycle()
        
        # Check if a macro was created
        rules = self.memory.get_rules()
        macro_rules = [r for r in rules if r['command_text'] == 'L-SHAPE' and r['is_composite'] == 1]
        
        self.assertTrue(len(macro_rules) > 0, "Macro rule should be created for L-SHAPE")
        
        # Verify the sequence
        macro = macro_rules[0]
        actions = json.loads(macro['macro_actions'])
        self.assertEqual(actions, [ACT_FORWARD, ACT_FORWARD, ACT_RIGHT])

    def test_recursive_decomposition(self):
        """Tests that 'A Y B' decomposes into actions for A and B."""
        # 1. Teach 'AVANZA' and 'GIRA'
        perc = json.dumps(self.env.get_perception_at(5, 5, DIR_N))
        # Add basic rules (direct associations)
        # Note: _get_action_for_symbol looks for non-composite rules with matching command_text
        self.memory.add_rule(json.loads(perc), ACT_FORWARD, weight=5, command="AVANZA")
        self.memory.add_rule(json.loads(perc), ACT_RIGHT, weight=5, command="GIRA")
        
        # 2. Execute decomposed command
        action1 = self.learner.act(self.robot, "AVANZA Y GIRA")
        
        self.assertEqual(action1, ACT_FORWARD)
        self.assertEqual(self.learner.active_plan, [ACT_RIGHT])
        
        # 3. Follow up action
        action2 = self.learner.act(self.robot)
        self.assertEqual(action2, ACT_RIGHT)
        self.assertEqual(self.learner.active_plan, [])

    def test_exact_macro_match(self):
        """Tests that a previously learned macro is triggered by its name."""
        # 1. Manually add a macro rule
        perc = self.env.get_perception_at(5, 5, DIR_N)
        seq = [ACT_FORWARD, ACT_LEFT, ACT_FORWARD]
        self.memory.add_rule(perc, seq[0], weight=10, is_composite=1, macro_actions=seq, command="ZIGZAG")
        
        # 2. Trigger it
        action1 = self.learner.act(self.robot, "ZIGZAG")
        
        self.assertEqual(action1, ACT_FORWARD)
        self.assertEqual(self.learner.active_plan, [ACT_LEFT, ACT_FORWARD])
        
        # 3. Continue execution
        action2 = self.learner.act(self.robot)
        self.assertEqual(action2, ACT_LEFT)
        self.assertEqual(self.learner.active_plan, [ACT_FORWARD])

    def test_macro_stability(self):
        """Tests that macros are not overwritten by simple rules even after repeated sleep cycles."""
        # 1. Create a sequence in history
        perc = self.env.get_perception_at(5, 5, DIR_N)
        self.memory.add_chrono(perc, ACT_FORWARD, 0, "REPEAT-ME")
        self.memory.add_chrono(perc, ACT_RIGHT, 0, "REPEAT-ME")
        
        # 2. First sleep cycle: Learned the macro
        self.learner.sleep_cycle()
        
        # Verify macro exists
        rules = self.memory.get_rules()
        macro_rules = [r for r in rules if r['command_text'] == 'REPEAT-ME' and r['is_composite'] == 1]
        self.assertEqual(len(macro_rules), 1)
        self.assertEqual(json.loads(macro_rules[0]['macro_actions']), [ACT_FORWARD, ACT_RIGHT])
        
        # 3. Add SAME sequence again to history (imitating another training session)
        self.memory.add_chrono(perc, ACT_FORWARD, 0, "REPEAT-ME")
        self.memory.add_chrono(perc, ACT_RIGHT, 0, "REPEAT-ME")
        
        # 4. Second sleep cycle
        self.learner.sleep_cycle()
        
        # Verify macro STILL exists and hasn't been corrupted
        rules = self.memory.get_rules()
        macro_rules = [r for r in rules if r['command_text'] == 'REPEAT-ME' and r['is_composite'] == 1]
        self.assertEqual(len(macro_rules), 1)
        self.assertEqual(json.loads(macro_rules[0]['macro_actions']), [ACT_FORWARD, ACT_RIGHT])
        # Weight should have increased
        self.assertTrue(macro_rules[0]['weight'] > 10)

if __name__ == '__main__':
    unittest.main()
