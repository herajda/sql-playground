# --------- init_db.py ---------
# Creates and populates the SQLite database

import sqlite3
import os

DB_PATH = os.path.join('app', 'db', 'playground.db')

schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL
);

INSERT INTO users (username, email) VALUES
('alice', 'alice@example.com'),
('bob', 'bob@example.com');
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        print("Database initialized at", DB_PATH)

if __name__ == '__main__':
    init_db()

