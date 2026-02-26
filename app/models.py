import sqlite3
from pathlib import Path
DB_PATH = Path('catalyst.sqlite3')
SCHEMA = '''
CREATE TABLE IF NOT EXISTS personas (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT,
 role TEXT,
 segment TEXT,
 goals TEXT,
 pains TEXT,
 notes TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS empathy_maps (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 persona_id INTEGER,
 says TEXT,
 thinks TEXT,
 does TEXT,
 feels TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(persona_id) REFERENCES personas(id) ON DELETE CASCADE
);
-- Define/HMW
CREATE TABLE IF NOT EXISTS problem_defs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 persona_id INTEGER,
 pov TEXT,
 hmw TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(persona_id) REFERENCES personas(id) ON DELETE CASCADE
);
-- Ideation ideas
CREATE TABLE IF NOT EXISTS ideas (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 persona_id INTEGER,
 stage TEXT,
 framework TEXT,
 text TEXT,
 votes INTEGER DEFAULT 0,
 cluster INTEGER,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(persona_id) REFERENCES personas(id) ON DELETE CASCADE
);
-- Prototypes
CREATE TABLE IF NOT EXISTS prototypes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 persona_id INTEGER,
 title TEXT,
 description TEXT,
 type TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(persona_id) REFERENCES personas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS story_panels (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 prototype_id INTEGER,
 idx INTEGER,
 title TEXT,
 body TEXT,
 FOREIGN KEY(prototype_id) REFERENCES prototypes(id) ON DELETE CASCADE
);
-- Test feedback
CREATE TABLE IF NOT EXISTS feedback (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 prototype_id INTEGER,
 worked TEXT,
 didnt TEXT,
 questions TEXT,
 ideas TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(prototype_id) REFERENCES prototypes(id) ON DELETE CASCADE
);
-- Iteration status
CREATE TABLE IF NOT EXISTS iterations (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 prototype_id INTEGER,
 status TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(prototype_id) REFERENCES prototypes(id) ON DELETE CASCADE
);
'''
def get_conn:
 conn = sqlite3.connect(DB_PATH)
 conn.row_factory = sqlite3.Row
 return conn
def init_db:
 with get_conn as c:
 c.executescript(SCHEMA)
def ensure_migrations:
 with get_conn as c:
 # Add matrix_quadrant to ideas if not exists
 try:
 c.execute("ALTER TABLE ideas ADD COLUMN matrix_quadrant TEXT")
 except Exception:
 pass