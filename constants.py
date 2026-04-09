"""
Constants Configuration for General Learner 4/5

This module defines all configurable parameters for the cognitive architecture,
categorised by functional domain. Each constant is documented with its purpose,
default value, and (where applicable) the biological or theoretical basis.

Author: Marco
"""

import pygame

# ====================
# Grid & Environment
# ====================

GRID_W = 10
"""Width of the simulation grid in cells."""

GRID_H = 10
"""Height of the simulation grid in cells."""

CELL_SIZE = 40
"""Pixel size of each grid cell for rendering."""

# Window dimensions
CANVAS_WIDTH = GRID_W * CELL_SIZE
CANVAS_HEIGHT = GRID_H * CELL_SIZE
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 1000
PANEL_WIDTH = 220
REPORT_WIDTH = 250
REPORT_HEIGHT = 350  # Increased to show all inference lines
POV_WIDTH = 280
POV_HEIGHT = 380

# ====================
# Visual Configuration
# ====================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
LIGHT_ORANGE = (255, 220, 150)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
PURPLE = (160, 32, 240)
YELLOW = (255, 255, 0)

# ====================
# Entity Identifiers
# ====================

EMPTY_ID = 0
"""Identifier for empty grid cells."""

BATTERY_ID = 1
"""Identifier for reward/charging stations."""

WALL_ID = 2
"""Identifier for obstacles."""

MIRROR_ID = 3
"""GL5: Identifier for mirror (self-recognition surface)."""

RESET_BUTTON_ID = 4
"""GL5 Dual-Bot: Identifier for maze reset tile (psychosis cure)."""

# ====================
# Robot Directions
# ====================

DIR_N = 0  # North (up)
DIR_E = 1  # East (right)
DIR_S = 2  # South (down)
DIR_W = 3  # West (left)

# ====================
# Robot Motor Actions
# ====================
# These represent the primitive motor outputs available to the agent.
# In biological terms, this is the final common pathway — the actual
# motor neurons that execute behaviour.

ACT_LEFT = 0
"""Rotate 90° counter-clockwise."""

ACT_RIGHT = 1
"""Rotate 90° clockwise."""

ACT_FORWARD = 2
"""Move one cell forward in current facing direction."""

ACT_BACKWARD = 3
"""Move one cell backward (reverse direction)."""

# ====================
# UI Configuration
# ====================

BTN_HEIGHT = 30
BTN_MARGIN = 4

# ====================
# Homeostatic Variables
# ====================

TIREDNESS_MAX = 150
"""Maximum tiredness before sleep is triggered."""

HUNGER_MAX = 150
"""Maximum hunger value before agent prioritises feeding."""

# ====================
# Memory Type Hierarchy
# ====================
# Models the brain's multiple memory systems with different
# temporal characteristics. Based on Squire's (1986) taxonomy:
# - Episodic: Fast encoding, fast decay, single events
# - Semantic: Slow encoding, slow decay, abstracted knowledge
# - Derived (GL5): RFT-inferred, medium decay, abstract relations

MEMORY_EPISODIC = 0
"""
Short-term episodic memory.

Biological analogue: The hippocampal formation — rapid encoding
of individual experiences, fast decay without consolidation.

Reference: Squire, L.R. (1986). Mechanisms of memory. Science, 232(4758), 1612-1619.
"""

MEMORY_SEMANTIC = 1
"""
Long-term semantic memory.

Biological analogue: The neocortex — slow consolidation of
abstracted knowledge, slow decay over time.

Reference: Squire, L.R. & Zola, S.M. (1996). Structure and function
of declarative and nondeclarative memory systems. PNAS, 93(24), 13515-13522.
"""

MEMORY_DERIVED = 2
"""
GL5: RFT-derived relational memory.

Biological analogue: The prefrontal cortex's abstract relational
reasoning — deriving new relationships without direct experience.

Reference: Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001).
Relational Frame Theory: A Post-Skinnerian Account of Human Language and Cognition.
"""

# ====================
# GL5 Multi-Store Memory Architecture (2026)
# ====================
# Extended memory hierarchy based on Atkinson-Shiffrin (1968)
# and Baddeley (1974) working memory model
# See GL5_MEMORY_SPEC.md for full specification

MEMORY_SENSORY = 3
"""
GL5: Sensory memory - raw perception buffer.

Biological analogue: Thalamus/neocortex - iconic memory (250ms).
Holds unprocessed fuzzy vectors before attention selection.
Decays very rapidly (90% per cycle).
"""

MEMORY_WORKING = 4
"""
GL5: Working memory - active manipulation.

Biological analogue: Prefrontal cortex - central executive.
Maintains active_plan, agenda, action_history.
Capacity: 4 chunks (Cowan, 2001).
Decay: 30% per cycle without rehearsal.
"""

MEMORY_INTERMEDIATE = 5
"""
GL5: Intermediate-term memory - circadian buffer.

Biological analogue: Hippocampal formation.
Acts as staging area between WM and LTM.
Duration: ~20-30 minutes.
Decay: 15% per cycle (slower than episodic).
"""

# ====================
# Working Memory Parameters (GL5)
# ====================

WM_CAPACITY = 4
"""
Maximum number of chunks in working memory.
Based on Cowan (2001) - magical number 4.
"""

WM_DURATION_CYCLES = 40
"""
Approximate cycles before WM item decays (~20 seconds at 500ms/step).
"""

# ====================
# Concept System
# ====================

MACRO_INDUCTION_THRESHOLD = 3
"""
Minimum occurrences of a command sequence before macro induction.
A command sequence appearing 3+ times during a sleep cycle is
converted into a single composite action (macro).

Biological analogue: The basal ganglia's habit formation —
repeated action sequences become 'chunked' into automatic
motor programmes, reducing cognitive load.

Reference: Graybiel, A.M. (2008). Habits, rituals, and the
evaluative brain. Annual Review of Neuroscience, 31, 359-387.
"""

MAX_RULES_PER_SLEEP_CYCLE = 50
"""
Maximum number of rules to consolidate per sleep cycle.
Limits memory processing to prevent system overload.
Higher values = more consolidation but slower processing.
"""

# ====================
# Reinforcement Values
# ====================

PUNISH_MOVE = -1
"""Penalty for wasted movement (no progress made)."""

REWARD_BATT = 10
"""Reward for reaching charging station (only a default, can be learned)."""

# ====================
# GL5: Learned Objectives System
# ====================
# The agent learns what is rewarding/punishing through experience.
# Objectives are not hardcoded - they emerge from reinforcement history.
# This implements the brain's reward system (dopamine, pleasure/pain).

OBJECTIVE_LEARNING_RATE = 0.2
"""
Rate at which the agent learns what is rewarding.
New positive outcomes increase the perceived value of similar stimuli.
"""

OBJECTIVE_THRESHOLD = 3.0
"""
Minimum accumulated value for a perception to become a goal.
Once a stimulus exceeds this, the agent actively seeks it.
"""

NOVELTY_BONUS = 2.0
"""
Reward for encountering new situations.
This drives exploration - the agent is intrinsically motivated
to discover new patterns and territories.
"""

HUNGER_PAIN = -3
"""Internal drive for energy (homeostasis) - pain when hungry."""

TIRED_PAIN = -3
"""Internal drive for rest (homeostasis) - pain when tired."""

# ====================
# GL5: Autobiographical Memory (Self-Model)
# ====================
# The robot has a unique self-identity (2-digit ID).
# This implements the "mirror test" capability - self-recognition.
# Reference: QBO robot (Yale) - recognizes itself in mirror.

SELF_ID_RANGE = (10, 99)
"""
Range for unique self-identifier (2-digit).
Lower bound ensures no single-digit IDs.
"""

MIRROR_RECOGNITION_REWARD = 5
"""
Reward when robot recognizes itself in mirror.
This reinforces self-concept preservation.
"""

SUBJECT_CONCEPT_WEIGHT = 3.0
"""
Weight for learned 'subject' concept (other autonomous agents).
When two robots meet and recognize each other as similar,
this creates the abstract concept of 'another self'.
"""

# ====================
# Memory Decay & Forgetting
# ====================
# Implements the Ebbinghaus forgetting curve with type-specific rates.
# Decay is multiplicative (asymptotic), not subtractive.
#
# Biological basis: Synaptic downscaling during slow-wave sleep.
# Reference: Tononi, G. & Pedersen, M. (2003). Sleep and consolidation.
# Nature, 425, 594-595.

FORGET_THRESHOLD = 0.5
"""Weight below which rules are permanently pruned."""

DECAY_RATE_EPISODIC = 0.8
"""
Fast decay for episodic memories.
Biologically, episodic traces in the hippocampus decay rapidly
unless consolidated to neocortex.
"""

DECAY_RATE_SEMANTIC = 0.95
"""
Slow decay for semantic knowledge.
Semantic memories (consolidated in neocortex) are relatively stable
once formed, representing crystallised knowledge.
"""

DECAY_RATE_DERIVED = 0.92
"""
Medium decay for RFT-derived relations.
Derived inferences are less stable than directly learned
semantic knowledge but more stable than raw episodic traces.
"""

# GL5 Multi-Store Decay Rates
DECAY_RATE_SENSORY = 0.1
"""
Very fast decay for sensory memory.
Biological: Iconic memory decays in ~250ms.
90% loss per cycle - nearly immediate forgetting.
"""

DECAY_RATE_WORKING = 0.7
"""
Fast decay for working memory without rehearsal.
Biological: Prefrontal cortex - items decay without rehearsal.
30% loss per cycle (protected if rehearsed).
"""

DECAY_RATE_INTERMEDIATE = 0.85
"""
Medium decay for intermediate-term memory.
Biological: Hippocampal buffer - 20-30 minute window.
15% loss per cycle - faster than semantic but slower than episodic.
"""

# ====================
# Relational Frame Theory (RFT) Parameters
# ====================
# GL5 extension: Parameters for derived relational reasoning.
# Reference: Hayes, S.C. et al. (2001). Relational Frame Theory.

RFT_WEIGHT_FACTOR = 0.4
"""
Weight multiplier for derived rules.
When deriving actions through RFT (mutual entailment), the
derived rule receives 40% of the original rule's weight.
This prevents derived inferences from overwhelming directly
experienced knowledge while still enabling generalisation.
"""

RFT_COORD_THRESHOLD = 3
"""
Minimum co-occurrences to establish a COORD (coordination/synonymy) frame.
Two concepts must be associated with the same action in at least
3 separate rule instances before a coordination frame is created.
"""

# ====================
# Motor Action Constants (for reference)
# ====================
# This section provides context for the action space.
# The action space is deliberately small (4 actions) to allow
# rapid learning with limited data — analogous to the 'small
# action space' assumption in reinforcement learning theory.
#
# Reference: Sutton, R.S. & Barto, A.G. (2018). Reinforcement Learning:
# An Introduction. MIT Press. Chapter 3.

# ====================
# GL5 Dual-Bot Physical Interaction Constants
# ====================

IMPACT_UNITS = 5
"""
GL5 Dual-Bot: Energy penalty for collision between bots.
Both attacker and defender receive this penalty on impact.
"""
