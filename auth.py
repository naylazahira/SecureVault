import bcrypt
from pathlib import Path

USER_FILE = Path("data/user.bin")

def register(username, password):
    USER_FILE.parent.mkdir(exist_ok=True)
    if USER_FILE.exists():
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    USER_FILE.write_bytes(username.encode()+b"\n"+hashed)
    return True

def login(username, password):
    if not USER_FILE.exists():
        return False
    try:
        saved_user, saved_hash = USER_FILE.read_bytes().split(b"\n",1)
        return saved_user.decode()==username and bcrypt.checkpw(password.encode(),saved_hash)
    except Exception:
        return False
