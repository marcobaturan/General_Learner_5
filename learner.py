import random
import json
import math
from memory import Memory
from fuzzy_logic import FBN
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
        self.agenda = []      # List of EXPECTED PERCEPTIONS (Fuzzy Vectors)
        self.bayesian = True  # Toggle for Bayesian Thompson Sampling
        self.fuzzy_processor = FBN()
        
        # Stagnation Control (Loop Prevention)
        self.pos_history = []  # Last 10 positions (x, y)
        self.stagnant = False 

    def act(self, robot, text_command=None):
        """
        Determines the next move.
        0. Prioritize Textual Command associations (Conceptual IDs).
        1. Checks for an active plan.
        2. Bayesian decision based on Fuzzy Situation vector.
        """
        state = robot.get_state()
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)
        
        # 0. AGNOSTIC COMMAND PROCESSING (Agnostic to language)
        if text_command and text_command.strip():
            concept_ids = self.memory.tokenize(text_command)
            rules = self.memory.get_rules()
            
            # --- PHASE A: EXACT MACRO MATCH ON TOKEN SEQUENCE ---
            # (Simplistic sequence matching for now)
            # Find rules where command_id matches the FIRST token of a macro
            # In GL4, we associate the whole string concept to a macro
            full_text_id = self.memory.get_or_create_concept_id(text_command.strip().upper())
            for r in rules:
                if r['command_id'] == full_text_id and r['is_composite'] == 1 and r['macro_actions']:
                    try:
                        actions = json.loads(r['macro_actions'])
                        if actions:
                            self.active_plan = actions[1:]
                            return actions[0]
                    except: continue

            # --- PHASE B: TOKEN DECOMPOSITION ---
            # If no macro, look at individual concept IDs (words/spaces)
            # Find the most reliable action for each token
            if len(concept_ids) > 1:
                decomposed_plan = []
                for cid in concept_ids:
                    sub_action = self._get_action_for_concept(cid, rules)
                    if sub_action is not None:
                        decomposed_plan.append(sub_action)
                
                if decomposed_plan:
                    self.active_plan = decomposed_plan[1:]
                    return decomposed_plan[0]

            # --- PHASE C: SIMPLE CONCEPT MATCH ---
            # Context-specific (Fuzzy Vector + Concept)
            for r in rules:
                if r['perception_pattern'] == perc_id and r['command_id'] == full_text_id:
                    if r['weight'] >= 2:
                        return r['target_action']
            
            # Priority 2: General concept (Anywhere + Token)
            sub_action = self._get_action_for_concept(full_text_id, rules)
            if sub_action is not None: return sub_action

        # 1. Follow active plan
        if self.active_plan:
            if self.agenda: self.agenda.pop(0)
            self._update_stagnation(robot)
            return self.active_plan.pop(0)
   
        # 1.5 Stagnation (Curiosity/Boredom) Check
        self._update_stagnation(robot)
        if self.stagnant:
            return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # 2. Decision Logic: Select best action (Fuzzy Bayesian TS)
        rules = self.memory.get_rules()
        action_options = {}
        for r in rules:
            if r['perception_pattern'] == perc_id:
                a = r['target_action']
                if a not in action_options: action_options[a] = []
                action_options[a].append(r['weight'])

        if not action_options:
            return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # Thompson Sampling
        best_action = None
        best_sample = -1
        for action, weights in action_options.items():
            w = sum(weights) / len(weights)
            # Asymptotic weights influence the beta distribution
            sample = random.betavariate(max(0.1, w + 1), 2)
            if sample > best_sample:
                best_sample = sample
                best_action = action
        
        return best_action

    def _get_action_for_concept(self, concept_id, rules):
        """Helper to find the most frequent action associated with a conceptual ID."""
        concept_actions = {}
        for r in rules:
            if r['command_id'] == concept_id and not r['is_composite']:
                a = r['target_action']
                concept_actions[a] = concept_actions.get(a, 0) + r['weight']
        
        if concept_actions:
            return max(concept_actions, key=concept_actions.get)
        return None

    def plan_with_agenda(self, start_perc_id, max_depth=8):
        """
        BFS planning over the fuzzy situational graph.
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

        # Find goal situations (high reward/weight)
        goals = {r['perception_pattern'] for r in rules if r['weight'] >= 5}
        if not goals: return [], []

        queue = [(start_perc_id, [], [start_perc_id])]
        visited = {start_perc_id}
        
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

    def get_situational_graph(self, limit=30):
        """Returns situational transitions for visualization, using fuzzy vectors."""
        rules = self.memory.get_rules()
        nodes = set()
        edges = []
        for r in rules:
            if len(edges) >= limit: break
            s1 = r['perception_pattern']
            s2 = r['next_perception']
            if s2:
                nodes.add(s1)
                nodes.add(s2)
                edges.append((s1, r['target_action'], s2, r['weight'], r['command_id']))
        return list(nodes), edges

    def learn(self, robot, action, reward, text_command=None):
        """
        Records an event and updates the Global Territory map.
        Uses raw sensory data for fuzzy processing.
        """
        state = robot.get_state()
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)
        
        # 1. Update Episodic Chrono
        self.memory.add_chrono(fuzzy_vector, action, reward, text_command)
        
        # 2. Update Global Territory Map (Hippocampal Grounding)
        self.memory.update_territory(robot.x, robot.y, perc_id, importance=reward if reward > 0 else 1.0)

    def sleep_cycle(self):
        """
        The 'Consolidation' phase. 
        1. Asymptotic Forgetting (Biological Decay).
        2. Macro Induction.
        3. Transition from Episodic (Fast) to Semantic (Slow) memory.
        """
        # 1. Decay all existing rules
        self.memory.decay_rules()
        
        # Fetch episodic history
        history = self.memory.get_all_chrono() 
        if not history: return 0
        
        new_rules_count = 0
        
        # 2. Sequential Macro Induction
        # Group repeated commands into single composite actions
        i = 0
        while i < len(history):
            cmd_text = history[i]['command_text']
            if cmd_text and len(cmd_text) > 3:
                seq = []
                start_perc = history[i]['perception']
                start_fuzzy = json.loads(start_perc)
                start_perc_id = json.dumps(start_fuzzy)
                
                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())
                
                while i < len(history) and history[i]['command_text'] == cmd_text:
                    seq.append(history[i]['action'])
                    i += 1
                
                if len(seq) > 1:
                    self.memory.add_rule(start_perc_id, seq[0], weight=8.0, 
                                         is_composite=1, macro_actions=seq, 
                                         command_id=cmd_id, memory_type=MEMORY_EPISODIC)
                    new_rules_count += 1
            else:
                i += 1

        # 3. Standard Rule Consolidation
        for i in range(len(history)):
            record = history[i]
            perc_vector = json.loads(record['perception'])
            perc_id = json.dumps(perc_vector)
            action = record['action']
            reward = record['reward']
            cmd_text = record.get('command_text')
            
            cmd_id = None
            if cmd_text:
                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())

            next_perc_id = None
            if i < len(history) - 1:
                next_fuzzy = json.loads(history[i+1]['perception'])
                next_perc_id = json.dumps(next_fuzzy)

            w = 5.0 if reward > 0 else (1.0 if reward >= -5 else -2.0)
            
            # Add as EPISODIC (Short term)
            self.memory.add_rule(perc_id, action, weight=w, 
                                 next_perception=next_perc_id, command_id=cmd_id, 
                                 memory_type=MEMORY_EPISODIC)
            
            # If highly successful, propagate to SEMANTIC (Long term)
            if reward > 5:
                 self.memory.add_rule(perc_id, action, weight=w*0.3, 
                                     next_perception=next_perc_id, command_id=cmd_id, 
                                     memory_type=MEMORY_SEMANTIC)
            
            new_rules_count += 1

        self.memory.clear_chrono()
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
