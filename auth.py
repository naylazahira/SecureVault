
import bcrypt
import json
from pathlib import Path

USER_FILE = Path("data/user.bin")


def _load_users():
    """Membaca akun baru dan memigrasikan format akun lama."""
    if not USER_FILE.exists():
        return {}

    raw = USER_FILE.read_bytes()

    # Format baru: JSON
    try:
        data = json.loads(raw.decode("utf-8"))
        return data.get("users", {})
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass

    # Format lama: username + bcrypt hash
    try:
        username, password_hash = raw.split(b"\n", 1)
        username = username.decode("utf-8").strip()

        if username and password_hash:
            return {
                username.lower(): {
                    "username": username,
                    "password_hash": password_hash.decode("ascii")
                }
            }
    except Exception:
        pass

    return {}


def _save_users(users):
    USER_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {"users": users}
    temp_file = USER_FILE.with_suffix(".tmp")

    temp_file.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )
    temp_file.replace(USER_FILE)


def user_exists(username):
    if not username or not username.strip():
        return False

    users = _load_users()
    return username.strip().lower() in users


def register(username, password):
    username = username.strip()

    if not username or not password:
        return False

    users = _load_users()
    key = username.lower()

    if key in users:
        return False

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    users[key] = {
        "username": username,
        "password_hash": password_hash.decode("ascii")
    }

    _save_users(users)
    return True


def login(username, password):
    if not username or not password:
        return False

    users = _load_users()
    account = users.get(username.strip().lower())

    if not account:
        return False

    try:
        password_hash = account["password_hash"].encode("ascii")
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash
        )
    except Exception:
        return False
