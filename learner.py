import random
import json
from memory import Memory
from constants import *

class Learner:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.mode = "COMMAND" # 'AUTONOMOUS' or 'COMMAND'

    def act(self, robot):
        """
        Determines the next action based on logic or memory.
        If autonomous, consults rules. If no rule applies, chooses random.
        Returns the action (0: L, 1: R, 2: F, 3: B).
        """
        state = robot.get_state()
        perception = state['perception']
        
        # Try to find a rule matching current perception perfectly
        rules = self.memory.get_rules()
        best_action = None
        best_weight = -9999
        
        perc_str = json.dumps(perception)
        
        # Simple exact match (in a more complex one, we'd do partial subset matching)
        for r in rules:
            if r['perception_pattern'] == perc_str:
                if r['weight'] > best_weight:
                    best_weight = r['weight']
                    best_action = r['target_action']
                    
        if best_action is not None and best_weight > 0:
            return best_action
            
        # fallback to random behavior if unknown
        return random.choice([0, 1, 2, 3])

    def sleep_cycle(self):
        """
        Analyzes chronology horizontally and vertically.
        Generates/Generalizes rules.
        """
        history = self.memory.get_all_chrono()
        if not history: return 0
        
        new_rules_count = 0
        
        # 1. Generate Concrete Rules from direct rewards
        for i, record in enumerate(history):
            if record['reward'] > 0:
                perc_pattern = json.loads(record['perception'])
                action = record['action']
                # Add this as a concrete rule
                self.memory.add_rule(perc_pattern, action, weight=5)
                new_rules_count += 1
                
                # 2. Sequential Consolidation (Composite Rules)
                # If the previous step eventually led to this reward, consolidate.
                if i > 0:
                    prev_record = history[i-1]
                    prev_perc = json.loads(prev_record['perception'])
                    # Create a rule marked as composite if it's part of a winning sequence
                    # We store it with is_composite=1
                    cur = self.memory.conn.cursor()
                    cur.execute("SELECT id FROM rules WHERE perception_pattern = ? AND target_action = ?", 
                                (json.dumps(prev_perc), prev_record['action']))
                    row = cur.fetchone()
                    
                    if row:
                        cur.execute("UPDATE rules SET weight = weight + 3, is_composite = 1 WHERE id = ?", (row['id'],))
                    else:
                        cur.execute("INSERT INTO rules (perception_pattern, target_action, weight, is_composite) VALUES (?, ?, ?, 1)", 
                                    (json.dumps(prev_perc), prev_record['action'], 3))
                    new_rules_count += 1

            elif record['reward'] < -5:
                # Penalty rule
                perc_pattern = json.loads(record['perception'])
                self.memory.add_rule(perc_pattern, record['action'], weight=-5)
                new_rules_count += 1

        self.memory.conn.commit()
        return new_rules_count
