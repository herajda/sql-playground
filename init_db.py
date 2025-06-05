# --------- init_db.py ---------
# Creates and populates a rich SQLite database with many tables and records

import sqlite3
import os
import random
import string
from datetime import datetime, timedelta

from app.db_manager import DEFAULT_DB

DB_PATH = DEFAULT_DB

# How much fake data?
N_USERS = 50
N_POSTS = 120
N_COMMENTS = 250
N_TAGS = 10
N_ROLES = 4

def random_str(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_email(name):
    domains = ['example.com', 'mail.com', 'test.org', 'playground.net']
    return f"{name}@{random.choice(domains)}"

def random_date():
    start = datetime(2023, 1, 1)
    end = datetime(2025, 6, 1)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime('%Y-%m-%d %H:%M:%S')

schema = """
-- USERS, ROLES, and USER_ROLES
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    joined_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER,
    role_id INTEGER,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- POSTS and TAGS (Many-to-many via post_tags)
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- COMMENTS (threaded)
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    parent_comment_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
);

-- Simple index
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)
        cur = conn.cursor()

        # Roles
        roles = ['admin', 'moderator', 'author', 'guest']
        cur.executemany('INSERT OR IGNORE INTO roles (name) VALUES (?)', [(role,) for role in roles])

        # Users
        users = []
        for i in range(N_USERS):
            uname = f"user_{random_str(5)}"
            email = random_email(uname)
            joined_at = random_date()
            users.append((uname, email, joined_at))
        cur.executemany('INSERT INTO users (username, email, joined_at) VALUES (?, ?, ?)', users)
        
        # User roles: random assignment, at least one per user
        cur.execute('SELECT id FROM users')
        user_ids = [row[0] for row in cur.fetchall()]
        cur.execute('SELECT id FROM roles')
        role_ids = [row[0] for row in cur.fetchall()]
        user_roles = []
        for uid in user_ids:
            user_roles.append((uid, random.choice(role_ids)))
            # Some users get a second role
            if random.random() < 0.2:
                user_roles.append((uid, random.choice(role_ids)))
        cur.executemany('INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)', user_roles)

        # Tags
        tags = [f"tag_{random_str(4)}" for _ in range(N_TAGS)]
        cur.executemany('INSERT OR IGNORE INTO tags (name) VALUES (?)', [(tag,) for tag in tags])

        # Posts
        posts = []
        for _ in range(N_POSTS):
            uid = random.choice(user_ids)
            title = f"Post about {random_str(7)}"
            content = f"This is some random content: {random_str(40)}"
            created_at = random_date()
            posts.append((uid, title, content, created_at))
        cur.executemany('INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)', posts)
        cur.execute('SELECT id FROM posts')
        post_ids = [row[0] for row in cur.fetchall()]

        # Post tags
        post_tags = []
        for pid in post_ids:
            tag_count = random.randint(1, 3)
            tag_sample = random.sample(range(1, N_TAGS + 1), tag_count)
            for tid in tag_sample:
                post_tags.append((pid, tid))
        cur.executemany('INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)', post_tags)

        # Comments (some are replies to others)
        comments = []
        for _ in range(N_COMMENTS):
            post_id = random.choice(post_ids)
            user_id = random.choice(user_ids)
            content = f"Comment: {random_str(25)}"
            created_at = random_date()
            # 10% chance of reply to another comment
            parent_id = None
            if comments and random.random() < 0.1:
                parent_id = random.choice([c[0] for c in comments])
            comments.append((post_id, user_id, content, created_at, parent_id))
        # Insert comments one by one to get IDs for parent references
        for c in comments:
            cur.execute('INSERT INTO comments (post_id, user_id, content, created_at, parent_comment_id) VALUES (?, ?, ?, ?, ?)', c)
        
        conn.commit()
        print("Database initialized at", DB_PATH)

if __name__ == '__main__':
    init_db()

