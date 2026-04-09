"""
General Learner 5 (GL5) -- Artificial Cognitive Engine

This module implements the core cognitive architecture of the GL5 agent,
extending GL4's operant conditioning with Relational Frame Theory (RFT)
derived reasoning capabilities.

The architecture implements a multi-phase decision cascade:
- Phase A: Macro execution (procedural memory retrieval)
- Phase B: Token decomposition (word-level parsing)
- Phase C: Associative memory (semantic retrieval)
- Phase D: RFT derived inference (novel contribution of GL5)

Based on:
- Fritz, W. (1989). The General Learner -- modelling neural column behaviour.
- Skinner, B.F. (1938). The Behaviour of Organisms -- operant conditioning.
- Hayes, S.C. et al. (2001). Relational Frame Theory.
- O'Keefe, J. & Nadel, L. (1978). The Hippocampus as a Cognitive Map.

Author: Marco (extending Grey Walter's cybernetic heritage)
"""

import random
import json
import math
import time
from memory import Memory
from fuzzy_logic import FBN
from constants import *
from rft import RelationalFrameEngine


class Learner:
    """
    The cognitive core of the General Learner agent.

    Implements the Universal Learner principle (Fritz, 1989):
        Stimulus → Representation → Decision → Action

    This class orchestrates the complete cognitive loop, from perceptual
    processing through decision making to action execution. It models
    several key brain systems:

    - Prefrontal Cortex: Executive decision-making, action selection
    - Basal Ganglia: Habit formation, action sequencing (procedural memory)
    - Hippocampus: Spatial mapping, episodic memory, pattern completion
    - RFT Module (GL5): Prefrontal abstract relational reasoning

    The decision cascade (Phases A-D) mimics the brain's hierarchical
    processing: from specific habit retrieval (Phase A) through increasingly
    abstract inference (Phases B-D) to ground-state exploration.
    """

    def __init__(self, memory: Memory, environment=None):
        """
        Initialises the cognitive engine with all subsystems.

        Args:
            memory: The Memory subsystem (hippocampal-cortical storage)
            environment: The Environment subsystem (optional, for maze_id)
        """
        self.memory = memory
        self.environment = environment  # GL5: for maze_id in territory

        # Execution mode: 'COMMAND' (human-guided) or 'AUTONOMOUS' (self-directed)
        self.mode = "COMMAND"

        # Procedural memory: sequences of actions awaiting execution
        # Analogous to the basal ganglia's action chunking capability
        self.active_plan = []

        # Visuospatial working memory: expected future perceptions
        # Models the prefrontal cortex's prospective memory -- 'what
        # should I expect to see after this action?'
        self.agenda = []

        # Bayesian action selection toggle
        self.bayesian = True

        # Fuzzy logic processor for perceptual vectorisation
        self.fuzzy_processor = FBN()

        # Real-time cognitive state monitoring
        self.last_inference_info = {"type": "IDLE", "details": ""}

        # GL5: Debug/tracking attributes
        self.last_command_processed = ""
        self._last_tokens = []
        self._last_perception = []

        # GL5: RFT engine for derived relational reasoning
        self.rft_engine = RelationalFrameEngine()

        # Loop prevention: monitors for behavioural stagnation
        # Analogous to the brain's dopamine-mediated novelty-seeking
        # when habitual loops become unrewarding
        self.pos_history = []
        self.action_history = []

        # GL5: Learned Objectives System
        # ================================
        # The agent learns what is rewarding/punishing from experience.
        # Not hardcoded - objectives emerge from accumulated rewards.
        # Maps perception patterns to accumulated reward values.
        self.objective_values = {}
        """
        Dictionary mapping perception patterns to learned reward values.
        Positive values =pleasure seeking (goals). Negative = pain avoidance.
        """

        # Stagnation tracking
        self.stagnant = False
        self._stagnation_cooldown = 0
        self._zero_reward_streak = 0
        self._last_reward = 0

        # Caching for situational graph to prevent overload
        self._situational_graph_cache = None
        self._situational_graph_timestamp = 0

        # Per-cycle rules cache for act() method
        self._act_rules_cache = None
        self._act_rules_timestamp = 0

    def act(self, robot, text_command=None, other_bot=None):
        """
        Determines the next action -- the core decision function.

        Implements a hierarchical cascade of inference pathways,
        each representing increasingly abstract cognitive processes:

        GL5 Dual-Bot: other_bot parameter enables mutual recognition
        in perception (OTHER_BOT_DETECTED concept).

        PHASE A: MACRO MATCH (Basal Ganglia -- Procedural Memory)
        ---------------------------------------------------------
        The most specific cognitive pathway. Retrieves pre-learned
        action sequences (macros) from procedural memory.

        Biological analogue: The basal ganglia's habit system --
        once a behavioural sequence is learned (e.g., 'navigate
        to charger'), it executes automatically without ongoing
        cortical supervision. Represented in the brain by the
        striatum's direct pathway.

        Reference: Graybiel, A.M. (2008). Habits, rituals, and
        the evaluative brain. Annual Review of Neuroscience, 31, 359-387.

        PHASE B: TOKEN DECOMPOSITION (Broca's Area -- Compositional Processing)
        ----------------------------------------------------------------------
        Breaks complex commands into word-level components, executing
        each in sequence. Models the brain's ability to understand
        compositional semantics -- 'forward AND right' becomes two
        separate action selections.

        Biological analogue: Broca's area in the left inferior
        frontal gyrus -- responsible for syntactic parsing and
        compositional language understanding.

        Reference: Friederici, A.D. (2011). The brain's distinct
        network components for language. Nature Reviews Neuroscience, 12, 78-88.

        PHASE C: ASSOCIATIVE MEMORY (Cortex -- Semantic Retrieval)
        ----------------------------------------------------------
        General concept-to-action mappings, ignoring specific
        perceptual context. The 'semantic memory' layer -- knowing
        that 'this concept generally leads to this action'.

        Biological analogue: The neocortex's semantic memory system --
        the distributed store of learned associations, particularly
        in inferior temporal cortex for object concepts and premotor
        cortex for action concepts.

        Reference: Pulvermüller, F. (2012). Meaning and the brain:
        the semantic subsumption of conceptual knowledge. Cortex, 48(5), 641-647.

        PHASE D: RFT DERIVED INFERENCE (Prefrontal Cortex -- Abstract Reasoning)
        ------------------------------------------------------------------------
        GL5's novel contribution. When no direct experience exists,
        uses derived relational networks to infer an action.

        Example: If 'AVANZA' → FORWARD was learned, and GO is coordinate
        with AVANZA, then GO → FORWARD is inferred without direct teaching.

        Biological analogue: The prefrontal cortex's abstract relational
        reasoning -- the ability to see that 'X is like Y' without having
        directly experienced X and Y together. This is the cognitive
        capacity that distinguishes human reasoning from pure conditioning.

        Reference: Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001).
        Relational Frame Theory. Chapter 4: Derived Relational Responding.

        PHASE 1: ACTIVE PLAN EXECUTION (Striatum -- Habitual Sequence)
        --------------------------------------------------------------
        If a plan exists from prior Phase A/B decomposition, execute
        sequentially without re-evaluation. Models the automatic
        execution of learned motor programmes.

        PHASE 1.5: STAGNATION DETECTION (VTA -- Novelty/Exploration)
        -----------------------------------------------------------
        Detects behavioural loops and forces exploration. The brain's
        dopamine system tracks prediction errors -- when outcomes are
        worse than expected (or unchanged despite action), the system
        shifts from exploitation to exploration.

        PHASE 2: THOMPSON SAMPLING (Exploration/Exploitation Balance)
        ---------------------------------------------------------------
        When no plan exists and no direct rule matches, uses Bayesian
        sampling to select actions. Models the brain's exploration-
        exploitation trade-off, balancing familiar rewarding actions
        against novel possibilities.

        Args:
            robot: The Robot instance (provides get_state())
            text_command: Optional human-provided command string

        Returns:
            int: The selected action (ACT_LEFT, ACT_RIGHT, etc.)
        """
        # Get current perceptual state (pass other_bot for collision-aware perception)
        state = robot.get_state(other_bot)
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)

        # Store for debug display
        try:
            if isinstance(fuzzy_vector, list):
                self._last_perception = fuzzy_vector[:5]
            elif isinstance(fuzzy_vector, dict):
                self._last_perception = [
                    f"{k}:{list(v.keys())[0] if v else '?'}"
                    for k, v in list(fuzzy_vector.items())[:5]
                ]
            else:
                self._last_perception = []
        except (json.JSONDecodeError, KeyError, TypeError):
            self._last_perception = []

        # Cache rules for act() to avoid repeated DB queries
        current_time = time.time()
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache

        # 0. COMMAND PROCESSING PATHWAY
        # =============================
        # When a human provides a text command, the agent attempts
        # hierarchical interpretation through Phases A → D
        if text_command and text_command.strip():
            # Track command for debug display
            self.last_command_processed = text_command.strip()
            concept_ids = self.memory.tokenize(text_command)
            self._last_tokens = concept_ids  # Store for debug
            # Use cached rules instead of fetching again
            # rules = self.memory.get_rules() - REMOVED to use cache

            # --- PHASE A: MACRO MATCH ---
            # Exact command-to-sequence retrieval
            full_text_id = self.memory.get_or_create_concept_id(
                text_command.strip().upper()
            )
            for r in rules:
                if (
                    r["command_id"] == full_text_id
                    and r["is_composite"] == 1
                    and r["macro_actions"]
                ):
                    try:
                        actions = json.loads(r["macro_actions"])
                        if actions:
                            self.active_plan = actions[1:]
                            self.last_inference_info = {
                                "type": "MACRO MATCH",
                                "details": f"Command: {text_command}",
                            }
                            return actions[0]
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue

            # --- PHASE B: TOKEN DECOMPOSITION ---
            # Compositional command understanding
            if len(concept_ids) > 1:
                decomposed_plan = []
                for cid in concept_ids:
                    sub_action = self._get_action_for_concept(cid, rules)
                    if sub_action is not None:
                        decomposed_plan.append(sub_action)

                if decomposed_plan:
                    self.active_plan = decomposed_plan[1:]
                    self.last_inference_info = {
                        "type": "DECOMPOSITION",
                        "details": f"Tokens: {len(concept_ids)}",
                    }
                    return decomposed_plan[0]

            # --- PHASE C: SIMPLE CONCEPT MATCH ---
            # Context-specific + general concept retrieval
            # GL5: Priority - first check general command (any perception)
            best_action = None
            best_weight = -999

            for r in rules:
                if r["command_id"] == full_text_id:
                    # GL5: Accept both specific perception OR general command
                    # Specific match (same perception) OR general (no perception filter)
                    is_specific_match = r["perception_pattern"] == perc_id
                    has_perception = (
                        r["perception_pattern"] and r["perception_pattern"] != "None"
                    )

                    # If has perception, need match. If no perception, accept any.
                    if (is_specific_match) or (not has_perception):
                        # Weight threshold: positive = good, negative = avoid
                        if r["weight"] > best_weight:
                            best_weight = r["weight"]
                            best_action = r["target_action"]

            if best_action is not None and best_weight > -5:  # Not heavily punished
                self.last_inference_info = {
                    "type": "ASSOCIATIVE MEMORY",
                    "details": f"Command learned (w={best_weight:.1f})",
                }
                return best_action

            # --- PHASE D: RFT DERIVED INFERENCE ---
            # Only activates when Phases A-C have found no match --
            # the 'shadow reasoning' fallback of GL5
            frames = self.memory.get_frames_for_concept(full_text_id)
            for frame in frames:
                if frame["relation_type"] == "COORD":
                    partner_id = (
                        frame["concept_b"]
                        if frame["concept_a"] == full_text_id
                        else frame["concept_a"]
                    )
                    derived_action = self._get_action_for_concept(partner_id, rules)
                    if derived_action is not None:
                        self.last_inference_info = {
                            "type": "RFT DERIVED (Coord)",
                            "details": f"Frame strength: {frame['strength']:.2f}",
                        }
                        return derived_action

        # 0.5 AUTONOMOUS PLANNING (GL5)
        # ============================
        # If no command given and no active_plan, try to plan a path to goal
        # This implements prospective coding - mentally simulating future states
        if not text_command and not self.active_plan:
            plan_path, agenda_nodes = self.plan_with_agenda(perc_id, max_depth=6)
            if plan_path and agenda_nodes:
                self.active_plan = plan_path[1:] if len(plan_path) > 1 else []
                self.agenda = agenda_nodes[1:] if len(agenda_nodes) > 1 else []
                self.last_inference_info = {
                    "type": "PLANNED PATH",
                    "details": f"Steps: {len(plan_path)}, Goals: {len(agenda_nodes)}",
                }
                return plan_path[0] if plan_path else None

        # 1. PLAN EXECUTION
        # ================
        # Execute pre-loaded action sequence from Phase A/B
        if self.active_plan:
            if self.agenda:
                self.agenda.pop(0)
            self.last_inference_info = {
                "type": "Executing Plan",
                "details": f"Remaining: {len(self.active_plan)}",
            }

            # Check stagnation BEFORE executing next action in plan
            self._update_stagnation(robot)
            if self.stagnant:
                self.active_plan = []  # Abort plan on stagnation
                self.last_inference_info = {
                    "type": "PLAN ABORTED (Stagnation)",
                    "details": "Forced exploration",
                }
            else:
                return self.active_plan.pop(0)

        # 1.5 STAGNATION CHECK
        # ====================
        # Detects behavioural loops -- analogous to the brain's
        # detection of prediction error when actions produce
        # no novel outcomes
        self._update_stagnation(robot)

        # Cooldown: if we just broke a stagnation, don't re-trigger immediately
        # This prevents TOC (touch-of-contract / obsessive-compulsive loops)
        if (
            self.stagnant
            and hasattr(self, "_stagnation_cooldown")
            and self._stagnation_cooldown > 0
        ):
            self.stagnant = False
            self._stagnation_cooldown -= 1

        if self.stagnant:
            self.last_inference_info = {
                "type": "STAGNANT (Obsession)",
                "details": "Forced Loop Break",
            }

            # Break loops by forcing opposite action type
            last_act = self.action_history[-1] if self.action_history else None
            last_pos = self.pos_history[-1] if self.pos_history else None

            # Determine break action based on what got us stuck
            break_action = ACT_FORWARD
            if last_act == ACT_FORWARD:
                # Stuck moving forward (wall) -> turn
                break_action = random.choice([ACT_LEFT, ACT_RIGHT])
            elif last_act == ACT_BACKWARD:
                # Stuck moving backward -> turn
                break_action = random.choice([ACT_LEFT, ACT_RIGHT])
            elif last_act in [ACT_LEFT, ACT_RIGHT]:
                # Stuck spinning -> move forward
                break_action = ACT_FORWARD
            else:
                # No history -> random exploration
                break_action = random.choice(
                    [ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD]
                )

            # 70% forced break, 30% random exploration (reduced from 80/20 for more variety)
            if random.random() < 0.7:
                chosen = break_action
            else:
                chosen = random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

            self.action_history.append(chosen)
            self._stagnation_cooldown = (
                3  # 3 cycles before stagnation can trigger again
            )
            return chosen

        # 2. THOMPSON SAMPLING
        # ===================
        # Bayesian action selection under uncertainty
        # Use cached rules for performance
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache
        action_options = {}
        for r in rules:
            if r["perception_pattern"] == perc_id:
                a = r["target_action"]
                if a not in action_options:
                    action_options[a] = []
                action_options[a].append(r["weight"])

        if not action_options:
            self.last_inference_info = {
                "type": "UNKNOWN SITUATION",
                "details": "Random Action",
            }
            return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # Sample from posterior distribution
        best_action = None
        best_sample = -1
        for action, weights in action_options.items():
            w = sum(weights) / len(weights)
            sample = random.betavariate(max(0.1, w + 1), 2)
            if sample > best_sample:
                best_sample = sample
                best_action = action

        if best_action is not None:
            opts_str = ", ".join(
                [f"A{k}:{sum(v) / len(v):.1f}" for k, v in action_options.items()]
            )
            self.last_inference_info = {
                "type": "THOMPSON SAMPLING",
                "details": opts_str,
            }

        if best_action is not None:
            self.action_history.append(best_action)
            if len(self.action_history) > 10:
                self.action_history.pop(0)

        return best_action

    def _get_action_for_concept(self, concept_id, rules):
        """
        Retrieves the most strongly associated action for a concept.

        Computes total weight per action for a given conceptual ID,
        returning the highest-weighted action. This implements the
        brain's pattern completion -- given a concept, retrieve
        the most frequently reinforced associated action.

        Biological analogue: The hippocampal CA3 auto-associative
        network's pattern completion -- given a partial cue (concept),
        retrieving the most strongly associated complete pattern (action).

        Args:
            concept_id: The conceptual ID to query
            rules: Pre-fetched rules list

        Returns:
            int: The highest-weight action, or None
        """
        concept_actions = {}
        for r in rules:
            if r["command_id"] == concept_id and not r["is_composite"]:
                a = r["target_action"]
                concept_actions[a] = concept_actions.get(a, 0) + r["weight"]

        if concept_actions:
            return max(concept_actions, key=concept_actions.get)
        return None

    def plan_with_agenda(self, start_perc_id, max_depth=8):
        """
        BFS planning over the situational transition graph.

        Constructs a mental model of the world as a graph of
        perception-action-perception transitions, then searches
        for a path from the current situation to a goal state.

        Biological analogue: The prefrontal cortex's prospective
        coding -- mentally simulating future states and planning
        multi-step trajectories. The 'agenda' stores expected
        perceptual outcomes of planned actions.

        Reference: Rushworth, M.F.S. & Behrens, T.E.J. (2008).
        Choice, uncertainty and value in prefrontal and cingulate
        cortex. Nature Neuroscience, 11, 389-397.

        Args:
            start_perc_id: Starting perception pattern JSON
            max_depth: Maximum plan length

        Returns:
            tuple: (action_path, landmark_perceptions)
        """
        import time

        current_time = time.time()

        # Use cached rules for performance
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache
        graph = {}
        for r in rules:
            s_from = r["perception_pattern"]
            if s_from not in graph:
                graph[s_from] = []
            graph[s_from].append(
                {
                    "action": r["target_action"],
                    "next_s": r["next_perception"],
                    "weight": r["weight"],
                }
            )

        goals = {r["perception_pattern"] for r in rules if r["weight"] >= 5}
        # GL5: Also include learned objectives (perceptions with high accumulated value)
        for perc, value in self.objective_values.items():
            if value >= 3.0:  # OBJECTIVE_THRESHOLD
                goals.add(perc)
        if not goals:
            return [], []

        queue = [(start_perc_id, [], [start_perc_id])]
        visited = {start_perc_id}

        while queue:
            current_s, path, landmarks = queue.pop(0)
            if len(path) >= max_depth:
                continue

            if current_s in goals and path:
                return path, landmarks

            if current_s in graph:
                for trans in graph[current_s]:
                    next_s = trans["next_s"]
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        queue.append(
                            (next_s, path + [trans["action"]], landmarks + [next_s])
                        )

        return [], []

    def get_situational_graph(self, limit=30):
        """
        Returns the situational transition graph for visualisation.

        Used by the UI to display the agent's internal model of
        the world -- a cognitive map of perception-action links.

        Uses caching to prevent repeated heavy database queries.
        """
        import time

        current_time = time.time()

        if self._situational_graph_cache is not None:
            if current_time - self._situational_graph_timestamp < 2.0:
                return self._situational_graph_cache

        rules = self.memory.get_rules(limit=100)
        nodes = set()
        edges = []

        # First pass: collect all perception patterns as nodes
        for r in rules:
            perc = r["perception_pattern"]
            if perc:
                nodes.add(perc)

        # Second pass: create edges from transitions (sleep-cycle created)
        transition_count = 0
        for r in rules:
            if len(edges) >= limit:
                break
            s1 = r["perception_pattern"]
            s2 = r["next_perception"]
            if s1 and s2:
                nodes.add(s2)
                edges.append((s1, r["target_action"], s2, r["weight"], r["command_id"]))
                transition_count += 1

        # If no transitions (no sleep yet), show action-based associations instead
        if transition_count == 0 and nodes:
            for r in rules:
                if len(edges) >= limit:
                    break
                perc = r["perception_pattern"]
                action = r["target_action"]
                if perc:
                    # Create virtual "action node" for visualization
                    action_node = f"ACTION_{action}"
                    nodes.add(action_node)
                    edges.append(
                        (perc, action, action_node, r["weight"], r["command_id"])
                    )

        self._situational_graph_cache = (list(nodes), edges)
        self._situational_graph_timestamp = current_time
        return list(nodes), edges

    def learn(self, robot, action, reward, text_command=None, other_bot=None):
        """
        Records an experience in episodic memory.

        This is the 'encoding' function -- every perception-action-outcome
        triplet is stored in the episodic buffer for later consolidation.

        Also updates the spatial cognitive map (territory), modelling
        the hippocampal formation's dual function: what happened
        (episodic) and where it happened (spatial).

        GL5 Dual-Bot: other_bot parameter enables collision event recording.

        Biological analogue: The hippocampal CA1 region's place cells
        -- simultaneously encoding 'what' (event) and 'where' (location)
        in the same neural ensemble.

        Reference: Eichenbaum, H. (2014). Time cells in the hippocampus:
        a temporal basis for episodic memory. Hippocampus, 24(12), 1365-1379.

        Args:
            robot: The Robot instance
            action: The action performed
            reward: The reinforcement received
            text_command: Optional command that triggered action
            other_bot: Optional other robot for collision detection
        """
        state = robot.get_state(other_bot)
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)

        # Track reward for stagnation detection
        if not hasattr(self, "_last_reward"):
            self._last_reward = 0
        self._last_reward = reward
        if not hasattr(self, "_zero_reward_streak"):
            self._zero_reward_streak = 0
        if reward == 0:
            self._zero_reward_streak += 1
        else:
            self._zero_reward_streak = 0

        # Invalidate situational graph cache when new learning occurs
        self._situational_graph_cache = None

        # 1. Episodic encoding
        self.memory.add_chrono(fuzzy_vector, action, reward, text_command)

        # 1.1 GL5: Force command-to-action association in semantic memory
        # ================================================================
        # When a human gives a command and the robot executes an action,
        # immediately create a direct rule in semantic memory (strong association).
        # This ensures the robot learns commands quickly instead of being "stupid".
        if text_command and text_command.strip():
            cmd_id = self.memory.get_or_create_concept_id(text_command.strip().upper())

            # GL5: Learning by reinforcement (operant conditioning)
            # ====================================================
            # - reward > 0: ACCIÖN CORRECTA →-premiar (peso positivo)
            # - reward < 0: ACCIÖN INCORRECTA →castigar (peso negativo)
            # - guided_mode: reforzar más la asociación guíada

            # Base weight from actual reward (positive=reward, negative=punish)
            base_weight = reward if reward != 0 else 5.0

            # In guided mode, strengthen the association more (facilitated learning)
            is_guided = getattr(self, "_guided_this_step", False)
            if is_guided and base_weight > 0:
                base_weight = 15.0  # Guided = stronger positive
            elif is_guided and base_weight <= 0:
                base_weight = -15.0  # Guided punishment = stronger negative

            self.memory.add_rule(
                perc_id,
                action,
                weight=base_weight,
                next_perception=None,
                command_id=cmd_id,
                memory_type=MEMORY_SEMANTIC,
            )

        # 1.5 GL5: Learn objectives from experience
        # ==========================================
        # The agent learns what is rewarding/punishing from accumulated experience.
        # This replaces hardcoded battery goals with learned value associations.
        from constants import OBJECTIVE_LEARNING_RATE, NOVELTY_BONUS

        # Track novelty (new perception = intrinsic reward)
        is_novel = perc_id not in self.objective_values

        # Update the objective value for this perception
        if perc_id not in self.objective_values:
            self.objective_values[perc_id] = reward
        else:
            # Learning rate - gradually adjust based on new evidence
            self.objective_values[perc_id] = (
                self.objective_values[perc_id] * (1 - OBJECTIVE_LEARNING_RATE)
                + reward * OBJECTIVE_LEARNING_RATE
            )

        # Bonus for novel situations (exploration drive)
        if is_novel and reward >= 0:
            self.objective_values[perc_id] += NOVELTY_BONUS

        # 1.6 GL5: Homeostatic pain signals
        # ================================
        # The agent learns that hunger/tiredness are painful and seeks relief.
        from constants import HUNGER_PAIN, TIRED_PAIN

        # Create homeostatic state perception
        homeo_key = f"homeo_h{robot.hunger}_t{robot.tiredness}"

        if homeo_key not in self.objective_values:
            self.objective_values[homeo_key] = 0

        # Pain increases with hunger/tiredness (avoidance drive)
        pain_signal = (robot.hunger * HUNGER_PAIN / 50) + (
            robot.tiredness * TIRED_PAIN / 50
        )
        self.objective_values[homeo_key] = pain_signal

        # 1.7 GL5: Mirror Self-Recognition
        # ================================
        # The robot can recognize itself in a mirror.
        # This is the basis for self-concept and theory of mind.
        from constants import MIRROR_ID, MIRROR_RECOGNITION_REWARD

        # Check if robot sees a mirror in the 3x3 perception grid
        perception = state.get("perception", [])
        has_mirror = False
        if perception:
            for row in perception:
                for cell in row:
                    if cell == MIRROR_ID:
                        has_mirror = True
                        break
                if has_mirror:
                    break

        if has_mirror:
            # Self-recognition! The robot sees itself.
            # This reinforces the self-concept (autobiographical memory)
            self.last_inference_info = {
                "type": "SELF-RECOGNITION",
                "details": f"Mirror seen! Self-ID: {robot.self_id}",
            }

            # Learn that "seeing self" is rewarding (self-preservation)
            # But limit the learning to avoid obsessive mirror-seeking loops
            mirror_perc = f"mirror_self_{robot.self_id}"
            if mirror_perc not in self.objective_values:
                self.objective_values[mirror_perc] = 0

            # Only reinforce moderately - prevent obsessive self-admiration loops
            # The robot can enjoy seeing itself but must move on
            self.objective_values[mirror_perc] += MIRROR_RECOGNITION_REWARD * 0.05

            # Cap the mirror reward to prevent obsession
            if self.objective_values[mirror_perc] > 8.0:
                self.objective_values[mirror_perc] = 8.0

        # 1.8 GL5 Dual-Bot: Other Bot Recognition
        # =======================================
        # When a bot sees another robot in perception, it detects the
        # other bot's ID and compares it with its own self_id.
        # This enables mutual recognition and prevents self-confusion.
        OTHER_BOT_ID = 99  # Magic number for other bot in perception grid

        has_other_bot = False
        other_bot_direction = None
        if perception:
            directions = [
                (-1, -1),
                (0, -1),
                (1, -1),  # North row
                (-1, 0),
                (1, 0),  # Middle row
                (-1, 1),
                (0, 1),
                (1, 1),
            ]  # South row
            dir_names = {
                (-1, -1): "NW",
                (0, -1): "N",
                (1, -1): "NE",
                (-1, 0): "W",
                (1, 0): "E",
                (-1, 1): "SW",
                (0, 1): "S",
                (1, 1): "SE",
            }
            for dy in range(3):
                for dx in range(3):
                    if dy == 1 and dx == 1:
                        continue  # Skip center (self position)
                    if dy == 1 and dx == 1:
                        continue
                    if dy == 1 and dx == 1:
                        continue
                    if perception[dy][dx] == OTHER_BOT_ID:
                        has_other_bot = True
                        other_bot_direction = dir_names.get((dx - 1, dy - 1), "?")

        if has_other_bot and other_bot is not None:
            # Other bot detected! Compare self_id
            perceived_id = other_bot.self_id
            self_id = robot.self_id

            if perceived_id != self_id:
                # OTHER BOT RECOGNIZED - different from self
                # This is the foundation for theory of mind
                self.last_inference_info = {
                    "type": "OTHER_BOT_DETECTED",
                    "details": f"Bot{perceived_id} seen at {other_bot_direction} (I'm Bot{self_id})",
                }

                # Learn that seeing OTHER bot is different from self
                # This prevents self-confusion - important for social behavior
                other_perc_key = f"other_bot_{perceived_id}_{other_bot_direction}"
                if other_perc_key not in self.objective_values:
                    self.objective_values[other_perc_key] = 0

                # Neutral-to-slightly-positive learning from social contact
                # (not as rewarding as self-recognition, but valuable)
                self.objective_values[other_perc_key] += 0.3

                # Cap to prevent obsession
                if self.objective_values[other_perc_key] > 5.0:
                    self.objective_values[other_perc_key] = 5.0

            else:
                # This would be a bug - two bots shouldn't have same ID
                self.last_inference_info = {
                    "type": "ERROR",
                    "details": "ID collision detected!",
                }

        # 2. Spatial map update (GL5: with maze_id for multi-maze support)
        maze_id = (
            getattr(getattr(self, "environment", None), "maze_id", "default")
            if self.environment
            else "default"
        )
        self.memory.update_territory(
            robot.x,
            robot.y,
            perc_id,
            importance=reward if reward > 0 else 1.0,
            maze_id=maze_id,
        )

    def sleep_cycle(self):
        """
        The consolidation phase -- memory reprocessing during downtime.

        Called when the robot's battery is low and movement ceases.
        Triggers the 'systems consolidation' process analogous to
        slow-wave sleep in biological brains:

        1. DECAY (Synaptic downscaling)
        ---------------------------------
        All rule weights are multiplied by their decay rate. This
        models the brain's selective weakening of unused synapses
        during sleep, making room for new learning.

        Biological analogue: The 'synaptic homeostasis hypothesis'
        -- Tononi & Pedersen (2003) argue that sleep downscales
        the entire synaptic network, compensating for the day's
        net synaptic strengthening.

        Reference: Tononi, G. & Cicardone, C. (2003). Sleep and
        consolidation. Nature, 425, 594-595.

        2. MACRO INDUCTION (Chunk formation)
        -----------------------------------
        Repeated command sequences are collapsed into single macro
        actions. Models the basal ganglia's habit formation --
        converting multi-step deliberative sequences into automatic
        motor programmes.

        Reference: Graybiel, A.M. (2008). Habits, rituals, and the
        evaluative brain. Annual Review of Neuroscience, 31, 359-387.

        3. CONSOLIDATION (Episodic → Semantic)
        -----------------------------------------
        Episodic traces are strengthened into semantic rules. High-
        reward episodes are additionally promoted to semantic storage.
        Models the hippocampal-neocortical dialogue during sleep --
        the 'replay' of day's events that consolidates them into
        long-term memory.

        Reference: Rasch, B. & Born, J. (2013). About sleep's role
        in memory. Physiological Reviews, 93(2), 681-766.

        4. RFT DERIVATION (GL5 -- Abstract inference)
        ---------------------------------------------
        Runs the Relational Frame Theory engine to detect new
        coordinations, derive transitive relationships, and apply
        transformation of functions. This is the 'dreaming' phase
        in GL5 -- abstract relational reasoning occurring during
        the consolidation window.

        Reference: Hayes, S.C. et al. (2001). Relational Frame Theory.

        Returns:
            int: Number of new rules created
        """
        # 1. Apply forgetting
        self.memory.decay_rules()

        # Fetch episodic history
        history = self.memory.get_all_chrono()
        if not history:
            return 0

        new_rules_count = 0

        # 2. Macro induction
        i = 0
        while i < len(history):
            cmd_text = history[i]["command_text"]
            if cmd_text and len(cmd_text) > 3:
                seq = []
                start_perc = history[i]["perception"]
                start_fuzzy = json.loads(start_perc)
                start_perc_id = json.dumps(start_fuzzy)

                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())

                while i < len(history) and history[i]["command_text"] == cmd_text:
                    seq.append(history[i]["action"])
                    i += 1

                if len(seq) > 1:
                    self.memory.add_rule(
                        start_perc_id,
                        seq[0],
                        weight=8.0,
                        is_composite=1,
                        macro_actions=seq,
                        command_id=cmd_id,
                        memory_type=MEMORY_EPISODIC,
                    )
                    new_rules_count += 1
            else:
                i += 1

        # 3. Standard consolidation (limited per cycle)
        max_per_cycle = MAX_RULES_PER_SLEEP_CYCLE - new_rules_count
        for i in range(len(history)):
            if new_rules_count >= MAX_RULES_PER_SLEEP_CYCLE:
                break
            record = history[i]
            perc_vector = json.loads(record["perception"])
            perc_id = json.dumps(perc_vector)
            action = record["action"]
            reward = record["reward"]
            cmd_text = record.get("command_text")

            cmd_id = None
            if cmd_text:
                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())

            next_perc_id = None
            if i < len(history) - 1:
                next_fuzzy = json.loads(history[i + 1]["perception"])
                next_perc_id = json.dumps(next_fuzzy)

            w = 5.0 if reward > 0 else (1.0 if reward >= -5 else -2.0)

            # Episodic storage
            self.memory.add_rule(
                perc_id,
                action,
                weight=w,
                next_perception=next_perc_id,
                command_id=cmd_id,
                memory_type=MEMORY_EPISODIC,
            )

            # Semantic promotion for highly rewarding experiences
            if reward > 5:
                self.memory.add_rule(
                    perc_id,
                    action,
                    weight=w * 0.3,
                    next_perception=next_perc_id,
                    command_id=cmd_id,
                    memory_type=MEMORY_SEMANTIC,
                )

            new_rules_count += 1

        self.memory.clear_chrono()

        # 4. GL5: RFT derivation cycle
        rft_result = self.rft_engine.run_cycle(self.memory)

        return new_rules_count

    def _update_stagnation(self, robot):
        """
        Detects behavioural loops and flags for intervention.

        Monitors three indicators of pathological behaviour:
        1. Static position -- not moving despite repeated action
        2. Oscillation -- cycling between two positions
        3. Action obsession -- repeatedly executing same action

        When detected, the system shifts to exploration mode,
        analogous to the brain's dopamine-mediated response to
        prediction error -- trying something new because the
        expected reward is not occurring.

        Biological analogue: The mesolimbic dopamine pathway's
        role in novelty-seeking and the switching between
        exploitation (current best) and exploration (new options).

        Reference: Kakade, S. & Dayan, P. (2002). Dopamine: generalisation
        and lookahead. Neural Networks, 15(4-6), 549-559.

        Args:
            robot: The Robot instance
        """
        # Track consecutive zero-reward actions (predicts stagnation risk)
        if not hasattr(self, "_zero_reward_streak"):
            self._zero_reward_streak = 0
        if not hasattr(self, "_last_reward"):
            self._last_reward = 0

        if self._last_reward == 0:
            self._zero_reward_streak += 1
        else:
            self._zero_reward_streak = 0
        self._last_reward = 0  # Reset, will be updated in learn()

        # Early warning: 5+ zero-reward cycles predicts stagnation
        if self._zero_reward_streak >= 5:
            self.stagnant = True
            return

        # Position tracking
        self.pos_history.append((robot.x, robot.y))
        if len(self.pos_history) > 15:  # Extended history
            self.pos_history.pop(0)

        if len(self.pos_history) < 8:  # More history needed
            self.stagnant = False
            return

        # Check: same action repeated 6+ times (more than 4)
        if len(self.action_history) >= 6:
            if len(set(self.action_history[-6:])) == 1:
                self.stagnant = True
                return

        # Check: oscillation between 2 positions (A-B-A-B pattern)
        last_6 = self.pos_history[-6:]
        # Check for back-and-forth between same two spots
        unique_positions = list(set(last_6))
        if len(unique_positions) == 2:
            # Check if alternating
            alternating = all(
                last_6[i] != last_6[i + 1] for i in range(len(last_6) - 1)
            )
            if alternating:
                self.stagnant = True
                return

        # Check: trapped in small area (3 positions or less in last 8)
        if len(set(self.pos_history[-8:])) <= 3:
            # But only if also taking same actions frequently
            if len(self.action_history) >= 4:
                recent_actions = self.action_history[-4:]
                if len(set(recent_actions)) <= 2:
                    self.stagnant = True
                    return

        self.stagnant = False
