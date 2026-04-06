import random
import json
from memory import Memory
from constants import *

class Learner:
    """
    The cognitive core of the robot. Implements the Universal Learner 
    principles (Fritz 1989): Stimulus -> Representation -> Decision -> Action.
    """
    def __init__(self, memory: Memory):
        self.memory = memory
        self.mode = "COMMAND" # 'AUTONOMOUS' or 'COMMAND'
        self.active_plan = [] # List of actions to execute in sequence

    def act(self, robot):
        """
        Determines the next move.
        1. Checks for an active plan.
        2. If no plan, tries to generate one toward a goal situation.
        3. If no plan possible, uses the best reactive rule.
        4. Fallback to random exploration.
        """
        state = robot.get_state()
        perception = state['perception']
        perc_str = json.dumps(perception)

        # 1. Follow active plan if it exists
        if self.active_plan:
            return self.active_plan.pop(0)

        # 2. Try to generate a plan to a goal
        new_plan = self.plan_to_goal(perc_str)
        if new_plan:
            self.active_plan = new_plan
            return self.active_plan.pop(0)

        # 3. Reactive behavior: Find best rule for current situation
        rules = self.memory.get_rules()
        best_action = None
        best_weight = -9999
        
        for r in rules:
            if r['perception_pattern'] == perc_str:
                if r['weight'] > best_weight:
                    best_weight = r['weight']
                    best_action = r['target_action']
                    
        if best_action is not None and best_weight > 0:
            return best_action
            
        # 4. Fallback to random discovery
        return random.choice([0, 1, 2, 3])

    def plan_to_goal(self, start_perc_str, max_depth=5):
        """
        Search for a sequence of actions leading from current situation to 
        a known 'goal' situation (one with a high-weight positive rule).
        Uses a BFS-like search over the known transition rules.
        """
        rules = self.memory.get_rules()
        
        # Build a transition graph from rules: Situation -> (Action, NextSituation, Weight)
        graph = {}
        for r in rules:
            s_from = r['perception_pattern']
            if s_from not in graph: graph[s_from] = []
            graph[s_from].append({
                'action': r['target_action'],
                'next_s': r['next_perception'],
                'weight': r['weight']
            })

        # Find goal situations (those with very high direct weights or objects)
        goals = {r['perception_pattern'] for r in rules if r['weight'] >= 5}
        
        if not goals: return []

        # Simple BFS to find the shortest path to any goal
        queue = [(start_perc_str, [])]
        visited = {start_perc_str}
        
        while queue:
            current_s, path = queue.pop(0)
            if len(path) >= max_depth: continue
            
            if current_s in goals and path:
                return path

            if current_s in graph:
                for transition in graph[current_s]:
                    next_s = transition['next_s']
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        new_path = path + [transition['action']]
                        queue.append((next_s, new_path))
                        
        return []

    def sleep_cycle(self):
        """
        The 'Dream' phase. Analyzes chronological memory to:
        1. Apply the 'Forgetting Curve' (Entropy) to existing rules.
        2. Extract concrete rules from rewards.
        3. Extract 'Situational Transitions': (S1, A) -> S2.
        """
        # Step 1: Forgetting (Biological Pruning)
        self.memory.decay_rules(decay_amount=1)

        history = self.memory.get_all_chrono()
        if not history: return 0
        
        new_rules_count = 0
        
        for i in range(len(history)):
            record = history[i]
            perc_pattern = json.loads(record['perception'])
            action = record['action']
            reward = record['reward']
            
            next_perc = None
            if i < len(history) - 1:
                next_perc = json.loads(history[i+1]['perception'])

            if reward > 0:
                self.memory.add_rule(perc_pattern, action, weight=5, next_perception=next_perc)
                new_rules_count += 1
                
                if i > 0:
                    prev_record = history[i-1]
                    prev_perc = json.loads(prev_record['perception'])
                    self.memory.add_rule(prev_perc, prev_record['action'], weight=3, is_composite=1, next_perception=perc_pattern)
                    new_rules_count += 1

            elif reward < -5:
                self.memory.add_rule(perc_pattern, action, weight=-5, next_perception=next_perc)
                new_rules_count += 1
            
            else:
                self.memory.add_rule(perc_pattern, action, weight=1, next_perception=next_perc)
                new_rules_count += 1

        self.memory.conn.commit()
        return new_rules_count
