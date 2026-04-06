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
        
        # Chronological memory: Stores perceptions, actions, rewards, AND text stimulus.
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
        
        # Rules memory: Stores associations between situations, actions, and text stimuli.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception_pattern TEXT NOT NULL,
                target_action INTEGER NOT NULL,
                command_text TEXT DEFAULT NULL,
                macro_actions TEXT DEFAULT NULL,
                weight INTEGER DEFAULT 1,
                is_composite INTEGER DEFAULT 0,
                next_perception TEXT DEFAULT NULL
            )
        """)

        # Migration: Ensure new columns exist for older databases.
        cols = {
            'chrono_memory': ['command_text TEXT DEFAULT NULL'],
            'rules': [
                'is_composite INTEGER DEFAULT 0',
                'next_perception TEXT DEFAULT NULL',
                'command_text TEXT DEFAULT NULL',
                'macro_actions TEXT DEFAULT NULL'
            ]
        }
        for table, new_cols in cols.items():
            for col_def in new_cols:
                col_name = col_def.split()[0]
                try:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
                except sqlite3.OperationalError:
                    pass 
        
        self.conn.commit()

    def add_chrono(self, perception, action, reward, command=None):
        """Adds a new event with optional command text to episodic memory."""
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute("""
            INSERT INTO chrono_memory (perception, action, reward, command_text) 
            VALUES (?, ?, ?, ?)
        """, (perc_str, action, reward, command))
        self.conn.commit()

    def add_rule(self, perception_pattern, action, weight=1, is_composite=0, next_perception=None, command=None, macro_actions=None):
        """
        Adds or updates a rule in semantic memory.
        If the (perception, action, command) triad exists, increments weight.
        """
        cur = self.conn.cursor()
        perc_str = json.dumps(perception_pattern)
        next_perc_str = json.dumps(next_perception) if next_perception else None
        macro_str = json.dumps(macro_actions) if macro_actions else None
        
        # Check if the exact rule (same stimulus + command + action/macro) exists
        query = "SELECT id, weight FROM rules WHERE perception_pattern = ? AND target_action = ?"
        params = [perc_str, action]
        if command:
            query += " AND command_text = ?"
            params.append(command)
        else:
            query += " AND command_text IS NULL"

        cur.execute(query, params)
        row = cur.fetchone()
        
        if row:
            cur.execute("UPDATE rules SET weight = weight + ?, is_composite = ?, next_perception = ?, macro_actions = ? WHERE id = ?", 
                        (weight, is_composite, next_perc_str, macro_str, row['id']))
        else:
            cur.execute("""
                INSERT INTO rules (perception_pattern, target_action, weight, is_composite, next_perception, command_text, macro_actions) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (perc_str, action, weight, is_composite, next_perc_str, command, macro_str))
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

    def decay_rules(self, amount=1, spatial_perceptions=None):
        """
        Applies biological forgetting. 
        Spatial rules (landmarks) decay at 1/5th the rate of episodic behavioral rules.
        """
        cursor = self.conn.cursor()
        if spatial_perceptions:
            # Slower decay for spatial landmarks
            placeholders = ','.join(['?'] * len(spatial_perceptions))
            cursor.execute(f"UPDATE rules SET weight = weight - (? * 0.2) WHERE perception_pattern IN ({placeholders})", 
                         [amount] + list(spatial_perceptions))
            # Standard decay for others
            cursor.execute(f"UPDATE rules SET weight = weight - ? WHERE perception_pattern NOT IN ({placeholders})", 
                         [amount] + list(spatial_perceptions))
        else:
            cursor.execute("UPDATE rules SET weight = weight - ?", (amount,))
            
        cursor.execute("DELETE FROM rules WHERE weight <= 0")
        self.conn.commit()

    def clear_chrono(self):
        """Clears episodic memory after consolidation."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        self.conn.commit()
