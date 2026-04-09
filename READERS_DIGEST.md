# Reader's Digest: What's GL5.1?

## 🤖 What is GL5.1?

**General Learner 5.1** is a **dual-bot social interaction research platform** featuring:
- **Two virtual robots** living in the same 2D maze (10x10 grid)
- Each robot has **independent memory** (separate databases)
- They can **see each other**, **collide**, and **learn from interaction**
- Research platform for **emergent social behavior** — like Schelling's segregation or Axelrod's cooperation

---

## 🏠 The 4 Pillars of Intelligence (Architecture)

### 1. **Situational Map** (Spatial "Brain")
The robot doesn't know where the battery is. When it moves, it observes its surroundings (walls, empty space, battery) and creates a **mental map** of "places" (each 3x3 pattern is a "place"). This map is like landmarks in your brain when you go somewhere new.

```
places = ["north-wall", "south-wall", "empty", "battery-near"]
```

### 2. **Visuospatial Agenda** (Imagination)
When the robot sees a battery FAR AWAY, it does a **daydream**: it searches its mental map for a path from where it is to the battery. It stores those "expected places" in a list = **agenda**. It's like when you close your eyes and imagine the route to your home.

### 3. **Bayesian Thompson Sampling** (Smart Decision-Making)
The robot has **4 possible actions**:
- Turn left
- Turn right
- Move forward
- Move backward

When it doesn't know what to do, it uses **loaded dice** (Beta distribution). The dice are "loaded" based on how well each action worked in the past. If an action usually gives a battery, it comes up more often. But sometimes it "rolls the dice" randomly to explore new things.

### 4. **Biological Forgetting** (Brain Cleanup)
Every time the robot sleeps (sleep cycle triggered):
- Rules weaken (lose strength)
- Weak rules get deleted
- Strong rules survive

This prevents the robot from filling up with junk (mental garbage).

---

## 🎮 Guided Mode (Vicarious Learning)

The user clicks on the map to move the robot:
1. The robot moves **immediately**
2. **Learns the relationship**: "If I'm here and human moves me here → do this"
3. Absorbs your "expertise" directly into memory

It's like teaching a child to ride a bike by holding them.

---

## 🚀 Autonomous Mode

The robot **on its own** decides what to do every 0.5 seconds (default):

### Its mental cycle (each step):

```
1. OBSERVE: What do I see? (walls, battery near/far, hungry, tired)
   ↓
2. THINK (4-phase cascade):
   
   Phase A: Do I have a stored command? → execute plan
   Phase B: Did you say "FORWARD AND RIGHT"? → split into steps
   Phase C: Did I already learn something in this situation? → use rule
   Phase D: (GL5 only) Do I know something related? → infer (e.g., "go" = "forward")
   ↓
3. ACT: Do what it decided
   ↓
4. REWARD: +10 if battery, -1 if not
   ↓
5. LEARN: "If I see this and do this → I get this"
   ↓
6. SLEEP if tired → consolidate memory
```

---

## 🧠 Types of Memory (Like Human Brain)

| Type | Speed | Example |
|------|-------|---------|
| **Episodic** | Fast, forgotten quickly | "Today I found battery in the NE corner" |
| **Semantic** | Slow, lasts long | "Batteries are always in the corners" |
| **Derived** (GL5) | Infers without experience | If "forward"→forward and "go"=forward, then "go"→forward |

---

## 🧩 Cognitivism: The Memory Architecture (GL5)

Based on neuroscientific research, GL5 implements a comprehensive multi-store memory system inspired by human cognition:

### The Five Memory Stores

| Store | Duration | Capacity | Biological Analogue |
|-------|----------|----------|---------------------|
| **Sensory Memory (SM)** | ~250ms | 12 items | Thalamus/Neocortex |
| **Working Memory (WM)** | ~18s | 4 chunks | Prefrontal Cortex |
| **Intermediate-Term (ITM)** | ~20-30 min | 50 items | Hippocampus (bridge) |
| **Long-Term (LTM)** | Indefinite | Unlimited | Neocortex |

### Memory Flow

```
SENSORS → SM (250ms decay) → WM (4 chunks max)
    ↓
ITM (20-30 min buffer) → SLEEP → LTM (semantic rules)
```

### Key Research Sources

1. **Atkinson-Shiffrin Model (1968)**: Three-stage memory model
2. **Baddeley (1974)**: Working memory with central executive
3. **Cowan (2001)**: Magical number 4 in short-term memory
4. **Squire (1986)**: Hippocampal vs neocortical memory distinction
5. **Ebbinghaus (1885)**: Forgetting curve and decay
6. **Hayes et al. (2001)**: Relational Frame Theory

### Transfer Mechanisms

- **SM → WM**: Attention selection (relevance filtering)
- **WM → ITM**: Encoding every action cycle
- **ITM → LTM**: Sleep consolidation (synaptic strengthening)
- **Rehearsal**: Protected decay for repeated items

### Decay Rates

| Store | Decay Rate | Threshold |
|-------|------------|-----------|
| SM | 0.1 (90% loss) | N/A |
| WM | 0.7 (30% loss) | N/A |
| ITM | 0.85 (15% loss) | 0.3 |
| LTM | 0.95 (5% loss) | 0.5 |

---

## 📊 Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│                    2D WORLD (PyGame)                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Robot   │───▶│ Sensors │───▶│ Fuzzy   │            │
│  │ (x,y)   │    │ (dist)  │    │ Logic   │            │
│  └─────────┘    └─────────┘    └────┬────┘            │
│                                       │                 │
│                    ┌─────────────────┘                 │
│                    ▼                                   │
│              ┌───────────────────┐                    │
│              │ LEARNER (Brain)   │                    │
│              │ ┌───────────────┐  │                    │
│              │ │ 1. Mental Map │  │  ← Situational    │
│              │ │ 2. Agenda     │  │  ← Planning        │
│              │ │ 3. Thompson   │  │  ← Decision        │
│              │ │ 4. Forgetting │  │  ← Sleep cycle    │
│              │ └───────────────┘  │                    │
│              └────────┬───────────┘                    │
│                       ▼                                 │
│              ┌───────────────────┐                      │
│              │ MEMORY (File)     │  ← SQLite            │
│              │ - chrono_memory   │  ← Episodic         │
│              │ - rules           │  ← Semantic         │
│              │ - relational_frame│  ← RFT (GL5)        │
│              └───────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Does It Fulfill the Workflow?

| Requirement | Status | Notes |
|-------------|--------|-------|
| Observation | ✅ | Fuzzy logic captures state |
| Representation | ✅ | Situational map + territory |
| Decision | ✅ | Cascade A-D + Thompson |
| Action | ✅ | 4 primitive actions |
| Learning | ✅ | Reinforces rules, macro induction |
| Forgetting | ✅ | Differentiated decay by type |
| Guided mode | ✅ | Guide mode + vicarious learning |
| Autonomous mode | ✅ | Auto mode with planning |

**CONCLUSION**: The system **DOES fulfill** the Universal Learner architecture proposed by Fritz (1989) and works as documented.

---

## 📈 Key Performance Indicators (KPIs)

Based on sample runs, the system demonstrates:

- **Learning Efficiency**: Rules grow from ~3 to ~54 in ~440 steps
- **Goal Achievement**: Score increases when batteries are found
- **Memory Consolidation**: Rules oscillate (created/during sleep, pruned via decay)
- **Autonomous Behavior**: Successfully navigates and finds goals after learning

---

## 🪞 Self-Recognition & Autobiographical Memory (GL5)

### The Mirror Test in Robotics

The **mirror test** (Gallup, 1970) is a classic cognitive benchmark used to assess self-awareness in animals and robots. It tests whether an entity can recognise its own reflection as itself, not as another individual.

### Key Research Projects

| Project | Institution | Year | Key Achievement |
|---------|-------------|------|-----------------|
| **QBO** | TheCorpora (Spain) | 2011 | First robot to pass mirror test; uses stereo vision to identify its reflection |
| **NICO** | Yale University | 2012 | Learned self-recognition through visual experience; "What is this?" → "Myself" |
| **iCub** | IIT (Italy) | Various | Open-source humanoid with self-model capabilities |

### How QBO Works (TheCorpora)

1. **Stereoscopic Vision**: Two cameras perceive depth
2. **Object Detection**: Identifies "red object" in view
3. **Spatial Reasoning**: Asks "What is this?" through internal knowledge base
4. **Learning**: When told "This is you", stores association "Myself = red object at centre"
5. **Recognition**: Next time seeing red object at centre → "This is me!"

> *"Qbo interprets the object 'Myself' as an ordinary object, for which it has special answers such as 'Wow. I'm learning myself' or 'Oh. This is me. Nice.'"* — TheCorpora Blog

### GL5 Implementation

Our system implements a simplified version:

```
┌─────────────────────────────────────────────────────────────┐
│                    GL5 SELF-RECOGNITION                     │
├─────────────────────────────────────────────────────────────┤
│  1. UNIQUE SELF-ID: Random 2-digit number (10-99)         │
│     → Represents the "I" concept                            │
│                                                              │
│  2. MIRROR OBJECT: Placed on random wall in maze           │
│     → Blue reflection when viewed through raycasting        │
│                                                              │
│  3. SELF-RECOGNITION EVENT:                                 │
│     - Robot perceives MIRROR_ID in 3x3 grid                 │
│     - Triggers: "SELF-RECOGNITION" in inferences            │
│     - Adds reward: MIRROR_RECOGNITION_REWARD = 5            │
│     - Learning: "seeing self" → positive value              │
│                                                              │
│  4. ID DISPLAY (Red nose light in POV):                     │
│     - When mirror visible: red dot appears                  │
│     - Shows "ID:XX" beside (braille-like display)           │
│     - Reinforces self-identity concept                      │
└─────────────────────────────────────────────────────────────┘
```

### Future: Subject Concept & Multi-Agent

When multiple robots exist:

1. **Subject Recognition**: Robot A sees Robot B → similar to self
2. **Abstract "Other" Concept**: Learns "another autonomous agent"
3. **Social Learning**: Can help, compete, or group with others
4. **Theory of Mind**: "That robot is like me - it acts on its own"

### References

1. Gallup, G.G. (1970). Chimpanzees: Self-recognition. Science, 167(3914), 86-87.
2. IEEE Spectrum (2011). Qbo Robot Passes Mirror Test. https://spectrum.ieee.org/qbo-passes-mirror-test
3. BBC News (2012). Robot learns to recognise itself in mirror. https://www.bbc.com/news/technology-19354994
4. Hart, J. & Scassellati, B. (2012). Robot NICO learning self-awareness using mirrors. Yale University.
5. TheCorpora (2011). QBO Development Blog. https://thecorpora.com

---

## 🤝 GL5.1: Dual-Bot Social Interaction (NEW!)

### What is this?

Two robots sharing one maze — each with their own brain (database). They can see each other, collide, and learn from interaction. This lets us study **emergent social behavior** using rules inspired by:

| Researcher | Concept | What it means |
|------------|---------|---------------|
| **Thomas Schelling** | Segregation | Simple preferences → complex patterns |
| **Robert Axelrod** | Cooperation | Tit-for-Tat strategy emerges |
| **Craig Reynolds** | Boids | Flocking from 3 simple rules |
| **Rodney Brooks** | Subsumption | Intelligence from reflexes |

### The Three Physical Laws

```
┌─────────────────────────────────────────────────────────────┐
│              GL5.1 PHYSICAL INTERACTION                      │
├─────────────────────────────────────────────────────────────┤
│  1. PAULI EXCLUSION                                          │
│     → Two bots cannot occupy the same tile                  │
│     → Movement blocked if other bot is there                 │
│                                                              │
│  2. PAIN ON IMPACT                                           │
│     → Collision = -5 energy to BOTH bots                   │
│     → Creates "ouch!" signal that bots learn to avoid       │
│                                                              │
│  3. MUTUAL RECOGNITION                                       │
│     → Each bot has unique ID (Bot 1 or Bot 2)               │
│     → Sees "OTHER" in perception → knows "not me"           │
│     → Mirror = self, other bot = not-self                   │
└─────────────────────────────────────────────────────────────┘
```

### The Psychosis Cure (Reset Button)

When a robot finds ALL batteries, the maze becomes empty — no goals left! This causes **TOC** (Touch-of-Contract): random movement, no learning.

**Solution**: A green **RESET_BUTTON** appears when batteries = 0. Step on it → batteries respawn → endless search continues.

### The Research Hypotheses

| Hypothesis | What we expect to see |
|------------|----------------------|
| **H1** | Bots learn to avoid each other (competition) |
| **H2** | Bots spread to opposite corners (territory) |
| **H3** | No learning — random behavior persists |
| **H4** | Implicit cooperation (one explores, one rests) |

### Visual Features

- **Maze**: Blue robot (Bot 1) + Orange robot (Bot 2)
- **POV**: Each bot sees itself in its own color, other bot in opposite color
- **Mirror**: Same color as self (self-recognition)

---

6. Schelling, T. (1971). The Strategy of Conflict. — Segregation models
7. Axelrod, R. (1984). The Evolution of Cooperation. — Tit for Tat
8. Reynolds, C. (1987). Flocks, Herds, and Schools. — Boids algorithm
9. Brooks, R. (1991). Intelligence without representation. — Subsumption