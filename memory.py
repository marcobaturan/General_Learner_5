import sqlite3
import json

class Memory:
    """
    Manages the persistent storage for the General Learner robot.
    Uses SQLite to store chronological experiences (episodic memory) 
    and learned rules (semantic memory).
    """
    def __init__(self, db_path="general_learner.db"):
        self.conn = sqlite3.connect(db_path)
        # Allows accessing columns by name like a dictionary (row['column_name'])
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initializes the database tables if they do not exist."""
        cur = self.conn.cursor()
        
        # 1. Chronological memory (Episodic buffer)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chrono_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                command_text TEXT DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Conceptual ID Mapping (Agnostic Grounding)
        # Maps words or spaces to unique internal IDs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conceptual_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT UNIQUE NOT NULL
            )
        """)
        
        # 3. Rules memory (Semantic/Consolidated knowledge)
        # Using REAL for weights to support asymptotic decay
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception_pattern TEXT NOT NULL,
                target_action INTEGER NOT NULL,
                command_id INTEGER DEFAULT NULL,
                macro_actions TEXT DEFAULT NULL,
                weight REAL DEFAULT 1.0,
                is_composite INTEGER DEFAULT 0,
                next_perception TEXT DEFAULT NULL,
                memory_type INTEGER DEFAULT 0, -- 0: Episodic, 1: Semantic
                FOREIGN KEY (command_id) REFERENCES conceptual_ids(id)
            )
        """)

        # 4. Global Territory Map (Hippocampal Territory)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS territory (
                x INTEGER,
                y INTEGER,
                situation_id TEXT,
                visits INTEGER DEFAULT 1,
                importance REAL DEFAULT 1.0,
                PRIMARY KEY (x, y)
            )
        """)

        # Migration: add missing columns to existing DBs
        migrations = [
            "ALTER TABLE rules ADD COLUMN memory_type INTEGER DEFAULT 0",
            "ALTER TABLE rules ADD COLUMN command_id INTEGER DEFAULT NULL",
            "ALTER TABLE rules ADD COLUMN macro_actions TEXT DEFAULT NULL",
            "ALTER TABLE rules ADD COLUMN is_composite INTEGER DEFAULT 0"
        ]
        for m in migrations:
            try:
                cur.execute(m)
            except sqlite3.OperationalError:
                pass  # Column already exists

        self.conn.commit()

    def get_or_create_concept_id(self, value):
        """
        Maps a string value (word or space) to a unique conceptual ID.
        This ensures the system is agnostic to the specific characters used.
        """
        if not value: return None
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT OR IGNORE INTO conceptual_ids (value) VALUES (?)", (value,))
            cur.execute("SELECT id FROM conceptual_ids WHERE value = ?", (value,))
            row = cur.fetchone()
            return row['id'] if row else None
        except sqlite3.Error:
            return None

    def tokenize(self, text):
        """
        Splits text into unique concept IDs: words and standardized spaces.
        "Avanza  y gira" -> [ID(AVANZA), ID( ), ID(Y), ID( ), ID(GIRA)]
        """
        if not text: return []
        import re
        # Split by spaces but KEEP the spaces as tokens
        raw_tokens = re.split(r'(\s+)', text.strip().upper())
        clean_tokens = []
        for t in raw_tokens:
            if not t: continue
            if t.isspace():
                clean_tokens.append(" ") # Consolidate spaces
            else:
                clean_tokens.append(t)
        
        return [self.get_or_create_concept_id(t) for t in clean_tokens]

    def add_chrono(self, perception, action, reward, command=None):
        """Adds a new event with optional command text to episodic memory."""
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute("""
            INSERT INTO chrono_memory (perception, action, reward, command_text) 
            VALUES (?, ?, ?, ?)
        """, (perc_str, action, reward, command))
        self.conn.commit()

    def add_rule(self, perception_pattern, action, weight=1.0, is_composite=0, 
                 next_perception=None, command_id=None, macro_actions=None, memory_type=0):
        """
        Adds or updates a rule in semantic/episodic memory.
        Uses conceptual IDs for commands.
        """
        cur = self.conn.cursor()
        perc_str = json.dumps(perception_pattern)
        next_perc_str = json.dumps(next_perception) if next_perception else None
        macro_str = json.dumps(macro_actions) if macro_actions else None
        
        # Check if the exact rule exists
        query = """
            SELECT id, weight FROM rules 
            WHERE perception_pattern = ? AND target_action = ? AND is_composite = ? 
            AND memory_type = ?
        """
        params = [perc_str, action, is_composite, memory_type]
        
        if command_id is not None:
            query += " AND command_id = ?"
            params.append(command_id)
        else:
            query += " AND command_id IS NULL"

        cur.execute(query, params)
        row = cur.fetchone()
        
        if row:
            # For existing rules, we strengthen them (additive)
            new_weight = row['weight'] + weight
            cur.execute("UPDATE rules SET weight = ?, next_perception = ?, macro_actions = ? WHERE id = ?", 
                        (new_weight, next_perc_str, macro_str, row['id']))
        else:
            cur.execute("""
                INSERT INTO rules (perception_pattern, target_action, weight, is_composite, next_perception, command_id, macro_actions, memory_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (perc_str, action, weight, is_composite, next_perc_str, command_id, macro_str, memory_type))
        self.conn.commit()

    def update_territory(self, x, y, situation_id, importance=1.0):
        """Updates the global world map with visited locations."""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO territory (x, y, situation_id, visits, importance)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(x, y) DO UPDATE SET 
                visits = visits + 1,
                situation_id = excluded.situation_id,
                importance = MAX(importance, excluded.importance)
        """, (x, y, situation_id, importance))
        self.conn.commit()

    def get_territory(self):
        """Retrieves the full explored territory map."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM territory")
        return [dict(row) for row in cur.fetchall()]

    def get_rules(self, memory_type=None):
        """Retrieves learned rules sorted by weight."""
        cur = self.conn.cursor()
        if memory_type is not None:
            cur.execute("SELECT * FROM rules WHERE memory_type = ? ORDER BY weight DESC", (memory_type,))
        else:
            cur.execute("SELECT * FROM rules ORDER BY weight DESC")
        return [dict(row) for row in cur.fetchall()]

    def clear(self):
        """Clears all stored memories (both episodic and semantic)."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        cur.execute("DELETE FROM rules")
        self.conn.commit()

    def decay_rules(self):
        """
        Applies asymptotic biological forgetting.
        Weights decrease non-linearly toward zero.
        """
        from constants import DECAY_RATE_EPISODIC, DECAY_RATE_SEMANTIC, FORGET_THRESHOLD, MEMORY_EPISODIC, MEMORY_SEMANTIC
        cur = self.conn.cursor()
        
        # Update weights based on memory type
        cur.execute("UPDATE rules SET weight = weight * ? WHERE memory_type = ?", (DECAY_RATE_EPISODIC, MEMORY_EPISODIC))
        cur.execute("UPDATE rules SET weight = weight * ? WHERE memory_type = ?", (DECAY_RATE_SEMANTIC, MEMORY_SEMANTIC))
        
        # Forget rules that drop below the threshold
        cur.execute("DELETE FROM rules WHERE weight < ?", (FORGET_THRESHOLD,))
        self.conn.commit()

    def get_all_chrono(self):
        """Retrieves all events from episodic memory buffer."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM chrono_memory ORDER BY id ASC")
        return [dict(row) for row in cur.fetchall()]

    def clear_chrono(self):
        """Clears episodic memory after consolidation."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        self.conn.commit()
