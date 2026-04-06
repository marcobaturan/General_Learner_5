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
        
        # Chronological memory: Stores the exact sequence of perceptions, actions, and rewards.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chrono_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Rules memory: Stores associations between situations (perceptions) and actions.
        # now extended with 'next_perception' to represent state transitions (S1, A) -> S2.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception_pattern TEXT NOT NULL,
                target_action INTEGER NOT NULL,
                weight INTEGER DEFAULT 1,
                is_composite INTEGER DEFAULT 0,
                next_perception TEXT DEFAULT NULL
            )
        """)

        # Migration: Ensure the is_composite and next_perception columns exist for older databases.
        try:
            cur.execute("ALTER TABLE rules ADD COLUMN is_composite INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Column already exists
        
        try:
            cur.execute("ALTER TABLE rules ADD COLUMN next_perception TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass # Column already exists
        
        self.conn.commit()

    def add_chrono(self, perception, action, reward):
        """Adds a new event to the chronological (episodic) memory."""
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute("""
            INSERT INTO chrono_memory (perception, action, reward) 
            VALUES (?, ?, ?)
        """, (perc_str, action, reward))
        self.conn.commit()

    def add_rule(self, perception_pattern, action, weight=1, is_composite=0, next_perception=None):
        """
        Adds or updates a rule in semantic memory.
        If the (perception, action) pair exists, increments the weight.
        """
        cur = self.conn.cursor()
        perc_str = json.dumps(perception_pattern)
        next_perc_str = json.dumps(next_perception) if next_perception else None
        
        # Check if the rule already exists
        cur.execute("SELECT id, weight FROM rules WHERE perception_pattern = ? AND target_action = ?", (perc_str, action))
        row = cur.fetchone()
        
        if row:
            # Update existing rule
            cur.execute("UPDATE rules SET weight = weight + ?, is_composite = ?, next_perception = ? WHERE id = ?", 
                        (weight, is_composite, next_perc_str, row['id']))
        else:
            # Insert new rule
            cur.execute("INSERT INTO rules (perception_pattern, target_action, weight, is_composite, next_perception) VALUES (?, ?, ?, ?, ?)", 
                        (perc_str, action, weight, is_composite, next_perc_str))
        self.conn.commit()

    def get_all_chrono(self):
        """Retrieves the entire chronological history ordered by time."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM chrono_memory ORDER BY id ASC")
        return [dict(row) for row in cur.fetchall()]

    def get_rules(self):
        """Retrieves learned rules sorted by their reliability (weight)."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM rules ORDER BY weight DESC")
        return [dict(row) for row in cur.fetchall()]

    def clear(self):
        """Clears all stored memories (both episodic and semantic)."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        cur.execute("DELETE FROM rules")
        self.conn.commit()

    def clear_chrono(self):
        """Clears episodic memory after consolidation."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        self.conn.commit()

    def decay_rules(self, decay_amount=1):
        """
        Simulates the 'Forgetting Curve'.
        Positive weights decrease, negative weights increase (entropy).
        Rules that reach a weight of 0 are deleted (forgotten).
        """
        cur = self.conn.cursor()
        # Decaying positive weights
        cur.execute("UPDATE rules SET weight = weight - ? WHERE weight > 0", (decay_amount,))
        # Decaying negative weights (moving them toward 0)
        cur.execute("UPDATE rules SET weight = weight + ? WHERE weight < 0", (decay_amount,))
        # Clean up forgotten rules
        cur.execute("DELETE FROM rules WHERE weight = 0")
        self.conn.commit()
        return cur.rowcount # Number of rules forgotten
