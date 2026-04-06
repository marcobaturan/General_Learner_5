import random
import json
from memory import Memory
from constants import *

"""
General Learner 4 (GL4) - Artificial Cognitive Engine
Based on Situational Transition Models (S1, A -> S2).
Incorporates:
1.  Bayesian Thompson Sampling for Action Selection.
2.  Visuospatial Working Memory (Agenda).
3.  Hippocampal Cognitive Mapping (Graph Nodes).
"""

class Learner:
    """
    The cognitive core of the robot. Implements the Universal Learner 
    principles (Fritz 1989): Stimulus -> Representation -> Decision -> Action.
    """
    def __init__(self, memory: Memory):
        self.memory = memory
        self.mode = "COMMAND" # 'AUTONOMOUS' or 'COMMAND'
        self.active_plan = [] # List of actions to execute
        self.agenda = []      # List of EXPECTED PERCEPTIONS (Mental Landmarks)
        self.bayesian = True  # Toggle for Bayesian Thompson Sampling
        
        # Stagnation Control (Loop Prevention)
        self.pos_history = []  # Last 10 positions (x, y)
        self.stagnant = False 

    def act(self, robot, text_command=None):
        """
        Determines the next move.
        0. Priotitize Textual Command associations (Macros and Symbols).
        1. Checks for an active plan.
        2. If no plan, tries to generate one.
        3. Best reactive rule.
        """
        state = robot.get_state()
        perception = state['perception']
        perc_str = json.dumps(perception)
        
        # 0. SYMBOLIC COMMAND PROCESSING
        if text_command and text_command.strip():
            cmd = text_command.strip().upper()
            rules = self.memory.get_rules()
            
            # --- PHASE A: EXACT MACRO MATCH ---
            # Search for composite rules (Macros) that match this exact string
            for r in rules:
                if r['command_text'] == cmd and r['is_composite'] == 1 and r['macro_actions']:
                    try:
                        actions = json.loads(r['macro_actions'])
                        if actions:
                            self.active_plan = actions[1:] # Load rest of sequence
                            return actions[0]
                    except: continue

            # --- PHASE B: RECURSIVE DECOMPOSITION ---
            # If no exact macro, split by 'y' or ',' to see if parts are known
            parts = [p.strip() for p in cmd.replace(',', ' Y ').split(' Y ') if p.strip()]
            if len(parts) > 1:
                decomposed_plan = []
                for p in parts:
                    # Find any rule that matches this sub-part (ignoring context for general parts)
                    sub_action = self._get_action_for_symbol(p, rules)
                    if sub_action is not None:
                        decomposed_plan.append(sub_action)
                
                if decomposed_plan:
                    self.active_plan = decomposed_plan[1:]
                    return decomposed_plan[0]

            # --- PHASE C: SIMPLE SYMBOL MATCH ---
            # Priority 1: Context-specific command (Perception + Text)
            for r in rules:
                if r['perception_pattern'] == perc_str and r['command_text'] == cmd:
                    if r['weight'] >= 2: # Minimum confidence
                        return r['target_action']
            
            # Priority 2: General command (Anywhere + Text)
            sub_action = self._get_action_for_symbol(cmd, rules)
            if sub_action is not None: return sub_action

        # 1. Follow active plan and update Visuospatial Agenda
        if self.active_plan:
            if self.agenda: self.agenda.pop(0)
            self._update_stagnation(robot)
            return self.active_plan.pop(0)
  
        # 1.5 Stagnation (Curiosity/Boredom) Check
        self._update_stagnation(robot)
        if self.stagnant:
            # Force random move to break physical loop
            return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # 2. Try to generate a plan to a goal (Cognitive Map check)
        new_plan, full_agenda = self.plan_with_agenda(perc_str)
        if new_plan:
            self.active_plan = new_plan
            self.agenda = full_agenda
            if self.agenda: self.agenda.pop(0)
            return self.active_plan.pop(0)
 
        # 3. Decision Logic: Select best action (Bayesian Thompson Sampling)
        rules = self.memory.get_rules()
        
        # Group rules by action for standard state
        action_options = {}
        for r in rules:
            if r['perception_pattern'] == perc_str:
                a = r['target_action']
                if a not in action_options: action_options[a] = []
                action_options[a].append(r['weight'])

        if not action_options:
            return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # Thompson Sampling: Each action represents a probability distribution.
        # The agent samples from these distributions to balance exploration/exploitation.
        best_action = None
        if self.bayesian:
            best_sample = -1
            for action, weights in action_options.items():
                w = sum(weights) / len(weights)
                # Beta distribution parameters (alpha, beta).
                # Alpha represents successful trials + 1. Beta represents failure context.
                # This mimics the biological 'Confidence' weight in decision units.
                sample = random.betavariate(max(0.1, w + 1), 2)
                if sample > best_sample:
                    best_sample = sample
                    best_action = action
        else:
            # Deterministic Path: Picks the most stabilized rule.
            max_w = -1
            for action, weights in action_options.items():
                w = sum(weights) / len(weights)
                if w > max_w:
                    max_w = w
                    best_action = action
        
        return best_action

    def _get_action_for_symbol(self, symbol, rules):
        """Helper to find the most frequent action associated with a text symbol."""
        sym = symbol.strip().upper()
        sym_actions = {}
        for r in rules:
            if r['command_text'] == sym and not r['is_composite']:
                a = r['target_action']
                sym_actions[a] = sym_actions.get(a, 0) + r['weight']
        
        if sym_actions:
            return max(sym_actions, key=sym_actions.get)
        return None

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

    def plan_with_agenda(self, start_perc_str, max_depth=8):
        """
        Extends planning to return both the actions and the EXPECTED SITUATIONS.
        Implements the 'Visuospatial Agenda' by anticipating landmarks.
        """
        rules = self.memory.get_rules()
        graph = {}
        for r in rules:
            s_from = r['perception_pattern']
            if s_from not in graph: graph[s_from] = []
            graph[s_from].append({
                'action': r['target_action'],
                'next_s': r['next_perception'],
                'weight': r['weight']
            })

        # Find goal situations (high reward)
        goals = {r['perception_pattern'] for r in rules if r['weight'] >= 5}
        if not goals: return [], []

        # BFS for shortest path + landmarks
        queue = [(start_perc_str, [], [start_perc_str])]
        visited = {start_perc_str}
        
        while queue:
            current_s, path, landmarks = queue.pop(0)
            if len(path) >= max_depth: continue
            
            if current_s in goals and path:
                return path, landmarks
 
            if current_s in graph:
                for trans in graph[current_s]:
                    next_s = trans['next_s']
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        queue.append((next_s, path + [trans['action']], landmarks + [next_s]))
                        
        return [], []

    def get_situational_graph(self, limit=20):
        """Returns the most important situational transitions for visualization."""
        rules = self.memory.get_rules()
        nodes = set()
        edges = []
        for r in rules[:limit]:
            s1 = r['perception_pattern']
            s2 = r['next_perception']
            if s2:
                nodes.add(s1)
                nodes.add(s2)
                edges.append((s1, r['target_action'], s2))
        return list(nodes), edges

    def sleep_cycle(self):
        """
        The 'Dream' phase. 
        1. Consolidate rules.
        2. MACRO INDUCTION: Identify sequences under the same command string.
        """
        self.memory.decay_rules(amount=1)
        history = self.memory.get_all_chrono()
        if not history: return 0
        
        new_rules_count = 0
        
        # Phase 1: Group Macro Sequences
        # If a long command persists across multiple lines, it's a sequence candidate
        macros = {} # cmd -> list of action sequences
        i = 0
        while i < len(history):
            cmd = history[i]['command_text']
            if cmd and len(cmd) > 5: # Long enough to be a potential sentence
                seq = []
                start_perc = json.loads(history[i]['perception'])
                while i < len(history) and history[i]['command_text'] == cmd:
                    seq.append(history[i]['action'])
                    i += 1
                if len(seq) > 1:
                    # Found a macro sequence!
                    self.memory.add_rule(start_perc, seq[0], weight=10, is_composite=1, macro_actions=seq, command=cmd)
                    new_rules_count += 1
            else:
                i += 1

        # Phase 2: Standard Rule Consolidation (Episodic to Semantic)
        for i in range(len(history)):
            record = history[i]
            perc_pattern = json.loads(record['perception'])
            action = record['action']
            reward = record['reward']
            cmd = record['command_text'].strip().upper() if record.get('command_text') else None
            
            next_perc = None
            if i < len(history) - 1:
                next_perc = json.loads(history[i+1]['perception'])

            w = 5 if reward > 0 else (1 if reward >= -5 else -5)
            self.memory.add_rule(perc_pattern, action, weight=w, next_perception=next_perc, command=cmd)
            new_rules_count += 1
            
            if reward > 0 and i > 0:
                prev_record = history[i-1]
                prev_perc = json.loads(prev_record['perception'])
                prev_cmd = prev_record['command_text'].strip().upper() if prev_record.get('command_text') else None
                self.memory.add_rule(prev_perc, prev_record['action'], weight=3, is_composite=1, next_perception=perc_pattern, command=prev_cmd)
                new_rules_count += 1

        self.memory.conn.commit()
        return new_rules_count

    def _update_stagnation(self, robot):
        """
        Updates internal position history and flags stagnation if 
        the robot is physically stuck in a loop or corner.
        """
        self.pos_history.append((robot.x, robot.y))
        if len(self.pos_history) > 10:
            self.pos_history.pop(0)

        if len(self.pos_history) < 6:
            self.stagnant = False
            return

        # Check for static (no move in 3 steps)
        if all(p == self.pos_history[-1] for p in self.pos_history[-3:]):
            self.stagnant = True
            return

        # Check for oscillation (back and forth between 2 points)
        last_4 = self.pos_history[-4:]
        if last_4[0] == last_4[2] and last_4[1] == last_4[3]:
            self.stagnant = True
            return

        self.stagnant = False
