import os

DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
UPLOAD_DIR = os.path.join(DB_DIR, 'storage')
ACTIVE_FILE = os.path.join(DB_DIR, 'active_db.txt')
DEFAULT_DB = os.path.join(DB_DIR, 'playground.db')

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_active_db() -> str:
    """Return the path of the currently active database."""
    if os.path.exists(ACTIVE_FILE):
        try:
            with open(ACTIVE_FILE) as f:
                path = f.read().strip()
                if path and os.path.exists(path):
                    return path
        except Exception:
            pass
    return DEFAULT_DB


def set_active_db(path: str) -> None:
    """Set the active database path."""
    with open(ACTIVE_FILE, 'w') as f:
        f.write(path)


def list_databases():
    """List available uploaded databases."""
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.db')]
    # include default if not present
    if os.path.basename(DEFAULT_DB) not in files:
        files.insert(0, os.path.basename(DEFAULT_DB))
    return files
