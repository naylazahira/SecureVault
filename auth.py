import sqlite3
import bcrypt
from pathlib import Path

DB_PATH = Path("data/users.db")


def init_auth_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)


def user_exists(username):
    init_auth_db()
    username = username.strip()
    if not username:
        return False
    with sqlite3.connect(DB_PATH) as conn:
        user = conn.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    return user is not None


def register(username, password):
    init_auth_db()
    username = username.strip()
    if not username or not password:
        return False
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def login(username, password):
    init_auth_db()
    username = username.strip()
    if not username or not password:
        return False
    with sqlite3.connect(DB_PATH) as conn:
        user = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    if user is None:
        return False
    return bcrypt.checkpw(
        password.encode("utf-8"),
        user[0]
    )
