# Symbolic Cognitive Architecture: A Fuzzy Bayesian Approach to Autonomous Agents

**Authors**: Marco, W. Grey Walter (in memoriam), W. Fritz (in memoriam)

## Abstract
![GL5 Architectual Preview](assets/preview.png)

This paper details the evolution and mechanics of the *General Learner 5 (GL5)*, an autonomous intelligent system exploring the intersection of Fuzzy Logic, Bayesian Action Selection, and Asymptotic Memory Decay. Built upon the pioneering cybernetic frameworks of W. Grey Walter's tortoises and W. Fritz's General Learner series, GL5 demonstrates how an agent can iteratively construct a functional understanding of its environment through symbolic grounding and reinforcement learning, free of hardcoded linguistic keywords.

[**Watch the Live GL5 System Demonstration**](assets/GL5-2026-05-06.mp5)

---

## 1. Introduction & Cybernetic Lineage

The history of autonomous mobile robotics is deeply rooted in attempts to replicate biological homeostasis and stimulus-response arcs. In the late 1950s, **W. Grey Walter** developed autonomous robotic "tortoises" (Machina speculatrix), designed to demonstrate that complex behavior can emerge from simple, interconnected analog circuits prioritizing survival mechanisms like light-seeking and battery recharging [1]. 

Extending this biological analogy into the computational realm, **W. Fritz** introduced the *General Learner* program in the 1990s [2]. Fritz sought to model cognitive architectures not through monolithic expert systems, but through dynamic, biologically-inspired processes mimicking the neural column behavior of organic brains experiencing conditioning.

Furthermore, we heavily rely on the pedagogical and foundational cybernetics exploration provided by **J. Andrade** in *Thinking with the Teachable Machine* [3], which posits that machine intelligence is best incubated through interactive, iterative teaching loops between the agent and its environment, rather than a priori rule programming.

The General Learner 5 serves as the modern culmination of these philosophies.

---

## 2. Core Architectural Components

### 2.1 Fuzzy Perceptual Vectors (Fuzzification)
Biological agents do not perceive the world in strict binary measurements. In 1965, **Lotfi A. Zadeh** developed **Fuzzy Logic** to formally represent degrees of truth [5]. 

In GL5, the agent's ultrasonic distance sensors and internal homeostatic needs (e.g., tiredness) are not processed as absolute integers. A dedicated `FBN` (Fuzzy Bayesian Network) module maps these raw values to linguistic concepts (e.g., `MURO_NORTE:CERCA`, `CANSANCIO:ALTO`) using specific membership functions (Triangular and Trapezoidal). 

### 2.2 Agnostic Symbolic Grounding
A fundamental leap in GL5 is its language agnosticism. Previous iterations relied on English or Spanish keywords. GL5 employs a `Tokenizer` that parses arbitrary strings into internal `conceptual_ids`. Meaning is not pre-assigned; it is derived via positive reinforcement when an arbitrary sound/text correlates with an action that decreases homeostatic stress.

### 2.3 Thompson Sampling (Exploration vs. Exploitation)
Action selection in uncertain environments represents a classic multi-armed bandit problem. Rather than employing purely greedy or epsilon-greedy strategies, GL5 utilizes **Thompson Sampling** [5]. 

Proposed initially by William R. Thompson in 1933, this heuristic algorithm maintains a probability distribution representing the agent's "belief" regarding the expected reward of actions. Actions with high uncertainty have wider distributions (encouraging exploration), while repeatedly successful actions narrow in variance (encouraging exploitation). GL5 calculates the probability of rule success using the Beta distribution, $B(\alpha, \beta)$, formed by historic successes and failures.

### 2.5 Asymptotic Forgetting Curve
To prevent database bloat and ensure cognitive flexibility, GL5 simulates the **Ebbinghaus Forgetting Curve** [6].

First theorized by Hermann Ebbinghaus in 1885, the forgetting curve demonstrates the exponential loss of memory retention over time. During GL5's "sleep cycles" (consolidation events triggered by low battery), the weights of associative rules are diminished asymptotically (`weight * DECAY_RATE`). Synaptic connections (rules) that fall below the `FORGET_THRESHOLD` are permanently pruned from the SQLite cortex, ensuring the agent adapts to dynamic environments rather than remaining paralyzed by outdated information.

---

## 3. System Analysis and Visual Evidence

The architecture provides a robust suite of diagnostic visualizers to monitor the agent's cognitive state.

### 3.1 The Synthesized Reality Engine (POV)
The agent operates within a grid, but localizes using a pseudo-3D raycasting technique mimicking optical perception.
![POV Rendering](assets/GL5_pov.jpg)

### 3.2 Situational Concept Network
This represents the agent's short-term working memory. Nodes represent fuzzy state vectors, and edges denote the semantic paths (actions and parsed text commands) connecting them. 
![Situational Concept Agenda](assets/GL5_situation_concept_viso_spatial_agenda.jpg)

### 3.3 Global Hippocampal Territory Map
The global map visualization records spatial exploration, utilizing a heat-map overlay to denote visit frequency (`visits`) and experiential relevance (`importance`), serving as the robot's functional Hippocampus.
![Global Territory Map](assets/GL5_global_map.jpg)

### 3.5 Command Induction and Consolidation
Through the sleep cycle, sequences of basic atomic actions are synthesized into composite macro commands, significantly reducing processing overhead for recurring navigation sequences.
![Command Interface](assets/GL5_command.jpg)

### 3.5 System Interaction & Vicarious Modes
The UI provides detailed feedback arrays, exporting full behavioral analytics when required.
![Vicarious Guided Mode](assets/GL5_vicarious_guided_mode.jpg)

### 3.6 Performance Inform & Telemetry
The integrated cognitive dashboard continuously renders the state of the agent's memory banks, allowing observers to visualize weight changes during active Thompson Sampling.
![Cognitive Analytics Dashboard](assets/GL5_inform.jpg)

### 3.7 Core Architectural Codebase State
![Codebase Snippet & Execution](assets/Captura%20de%20pantalla_2026-05-06_21-37-15.jpg)

### 3.8 Real-Time Cognitive Inferences Monitor
A dedicated sub-window below the 2D world view surfaces the agent's internal decision logic on every cycle. The monitor exposes which cognitive pathway is currently driving behavior: **Thompson Sampling** (with per-action Bayesian weights), **Macro Pattern Execution**, **Token Decomposition**, **Associative Memory**, or **Obsession Loop Break**. This provides a direct, interpretable window into the agent's moment-to-moment reasoning process.
![Real-Time Inference Processing](assets/GL5_show_inner_state_processing_inferences.jpg)

### 3.9 Anti-Obsession Saturation Mechanism & Maze Regeneration
To prevent behavioral fixation (analogous to pathological conditioning loops), GL5 incorporates an **Action Saturation Detector**. When 5 or more identical consecutive actions are registered in `action_history`, the system classifies the agent as `STAGNANT (Obsession)` and applies a deterministic counter-action (e.g., FORWARD breaks rotation loops; a TURN breaks wall-collision loops), with an 80% / 20% forced/random split. 

The **NEW MAZE** button allows the researcher to regenerate the environment entirely in place, testing the agent's ability to transfer prior learned rules to novel topologies without resetting memory — a critical test of cognitive generalization.
![NEW MAZE Button & Environment Regeneration](assets/GL5_button_new_maze.jpg)

---

## 5. Future Research Directions

GL5 represents a functional cognitive substrate. The following theoretical extensions are proposed as a roadmap for the next research phase.

### 5.1 Relational Frame Theory (RFT): From Behaviorism to Cognitivism — **IMPLEMENTED**

The dominant paradigm underlying GL5's current learning engine is **Operant Conditioning** (Skinner, 1938): the agent increases or decreases the frequency of behaviours based on environmental consequences (rewards and punishments via `weight` updates). While sufficient for generating adaptive behaviour, this paradigm cannot model the full scope of human-level symbolic cognition.

**Relational Frame Theory (RFT)**, developed by **Steven C. Hayes et al. (2001)** [7], proposes that the defining feature of human cognition is the capacity for *derived relational responding* — the ability to frame stimuli in terms of **arbitrarily applicable relations** (e.g., *same as*, *opposite of*, *more than*, *part of*) without direct conditioning.

This represents the critical bridge from behaviourism into cognitivism: the agent does not need to directly experience that `A > B` and `B > C` to derive that `A > C`. It constructs this transitivity from its relational repertoire. This "bidirectionality" of derived relations (if trainer conditions `A→B`, the agent derives `B→A` without training) is a fundamental distinction between biological cognition and current GL5 behaviour.

---

### 5.1.1 GL5 Implementation: The RFT Layer

General Learner 5 (GL5) extends GL5 with a complete RFT module. The implementation preserves all existing GL5 learning pathways while adding a "shadow reasoning" capability activated only during `sleep_cycle()`.

#### 5.1.1.1 Architecture Summary

| Component | GL5 Function | GL5 Enhancement |
|-----------|--------------|-----------------|
| **Database** | `rules`, `chrono_memory`, `conceptual_ids` | New `relational_frames` table (coordination, opposition) |
| **Memory Types** | `MEMORY_EPISODIC (0)`, `MEMORY_SEMANTIC (1)` | Added `MEMORY_DERIVED (2)` — rules inferred via RFT |
| **Decay Rates** | `DECAY_RATE_EPISODIC=0.8`, `DECAY_RATE_SEMANTIC=0.95` | New `DECAY_RATE_DERIVED=0.92` |
| **Inference** | Direct experience only (Phase A-C) | Added Phase D: RFT Derived Frame Lookup |

#### 5.1.1.2 The Three Core RFT Mechanisms Implemented

1. **Mutual Entailment (Coordination)**
   - If concept A maps to action X with high weight, and A is coordinate with B (synonym), then B inherits the same action with reduced weight (`RFT_WEIGHT_FACTOR = 0.5`).
   - This mimics **semantic generalisation** in human cognition — once we know "dog" and "canine" are equivalent, learning about dogs transfers to canines without explicit teaching.

2. **Combinatory Entailment (Transitivity)**
   - If COORD(A, B) and COORD(B, C), then COORD(A, C) is derived automatically.
   - This mirrors **transitive inference**, a well-documented capability in primates (e.g., if A > B and B > C, then A > C) demonstrated by **McGonigle & Chalmers (1992)** [9].

3. **Transformation of Functions**
   - If concept A has high motivational relevance (high accumulated weight), and A is coordinate with B, B inherits partial motivational relevance.
   - Analogous to **stimulus equivalence** studies in behaviour analysis showing that newly learned relations transfer valence between related stimuli.

#### 5.1.1.3 Implementation Details

**Phase D Integration**: The new inference phase is inserted after Phase C (Direct Concept Match) and before Thompson Sampling. It only activates when no direct experience exists — pure derived inference.

```python
# PHASE D: DERIVED RELATIONAL FRAME LOOKUP (RFT)
# Only fires when no direct rule exists — shadow reasoning fallback
frames = memory.get_frames_for_concept(full_text_id)
for frame in frames:
    if frame['relation_type'] == 'COORD':
        partner_id = frame['concept_b'] if frame['concept_a'] == full_text_id else frame['concept_a']
        derived_action = self._get_action_for_concept(partner_id, rules)
        if derived_action is not None:
            return derived_action  # Inferred, not directly learned
```

**Sleep Cycle Enhancement**: The RFT engine runs after standard consolidation, detecting new coordinations, closing transitivity, deriving mutual entailments, and applying transformations.

#### 5.1.1.5 Preservation Principle

All original GL5 learning pathways maintain **absolute precedence** over derived rules. Direct experiential rules (memory_type 0 or 1) always have higher effective weight than derived rules (memory_type 2). This ensures the agent never "forgets" what it was taught and remains grounded in reality rather than abstract inference.

---

### 5.2 Predictive Coding & Active Inference (Friston, 2010)

The **Free Energy Principle** by **Karl Friston** [8] reframes cognition as continuous *surprise minimization*. Rather than reacting to stimuli, the agent maintains a generative model of the world and acts to minimize the discrepancy between prediction and observation. In GL5 terms, the `agenda` (visuospatial working memory) is a primitive form of top-down predictive state; a full implementation would have the agent continuously generating expected fuzzy vectors before acting and comparing them against observed `fuzzy_processor.get_feature_vector(state)`.

### 5.3 Multi-Agent Social Learning

GL5 currently operates as a solitary agent. A natural extension is a **multi-agent parliament** where several GL5 instances co-inhabit an environment and can observe each other's actions — enabling **vicarious learning** beyond the current human-guided GUIDE MODE. This would allow emergent social norms, cooperative strategies, and inter-agent concept transfer via shared conceptual ID namespaces.

### 5.5 Literature Review Roadmap

For the next phase, a structured review of the following corpora is planned:

- **Reinforcement Learning**: Sutton & Barto (2018), *Reinforcement Learning: An Introduction* — foundational formalism.
- **Behavior Analysis**: Skinner (1938), *The Behavior of Organisms* — operant conditioning substrate.
- **Cognitive Science / RFT**: Hayes, Barnes-Holmes & Roche (2001), *Relational Frame Theory: A Post-Skinnerian Account of Human Language and Cognition*.
- **Predictive Coding**: Friston (2010), *The free-energy principle: a unified brain theory?*
- **Fuzzy Systems**: Zadeh (1965, 1973); Mamdani & Assilian (1975) — fuzzy rule interpolation.
- **Computational Neuroscience**: Dayan & Abbott (2001), *Theoretical Neuroscience* — neural column modeling, spike-timing-dependent plasticity (STDP) as a biological analog to the current weight decay mechanism.

---

## References & Bibliography

[1] **William Grey Walter**, *Machina speculatrix*. Cybernetic theory extending to robotic homeostasis and emergent behavior. [Reference via Wikipedia: William Grey Walter - Robots](https://en.wikipedia.org/wiki/William_Grey_Walter#Robots).

[2] **W. Fritz**, *The General Learner*. Biologically Inspired Cognitive Architectures (BICA), focused on modeling neural columns and stimulus-response arcs.

[3] **J. Andrade**, *Thinking with the Teachable Machine*. Internet Archive eBook tracing the pedagogical loops of early theoretical neural networks and teaching systems. [Archived Entry](https://archive.org/details/thinkingwithteac0000andr).

[5] **Lotfi A. Zadeh**, *Fuzzy Sets* (1965). The introduction of infinite-valued logic to accommodate vagueness and uncertainty in algorithmic processing. [Reference via Wikipedia: Fuzzy Logic](https://en.wikipedia.org/wiki/Fuzzy_logic).

[5] **William R. Thompson**, *On the likelihood that one unknown probability exceeds another in view of the evidence of two samples* (1933). The foundation of Bayesian Bandit sampling protocols. [Reference via Wikipedia: Thompson Sampling](https://en.wikipedia.org/wiki/Thompson_sampling).

[6] **Hermann Ebbinghaus**, *Memory: A Contribution to Experimental Psychology* (1885). Empirical study of memory retention and the asymptotic nature of forgetting. [Reference via Wikipedia: Forgetting Curve](https://en.wikipedia.org/wiki/Forgetting_curve).

[7] **Steven C. Hayes, Dermot Barnes-Holmes & Bryan Roche**, *Relational Frame Theory: A Post-Skinnerian Account of Human Language and Cognition* (2001). Kluwer Academic / Plenum Publishers. The foundational text for RFT, proposing derived relational responding as the core mechanism of human symbolic cognition.

[8] **Karl J. Friston**, *The free-energy principle: a unified brain theory?* (2010). Nature Reviews Neuroscience, 11(2), 127–138. Introduces Active Inference and the Free Energy Principle as a unifying framework for perception, action, and learning in biological organisms.

[9] **Brian M. McGonigle & Michael Chalmers**, *Are monkeys logical?* (1992). Journal of Experimental Psychology: Animal Learning and Cognition, 18(3), 235-250. Demonstrates transitive inference in non-human primates, supporting the cognitive basis for RFT's combinatory entailment mechanism.
