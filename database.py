import sqlite3, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

DB="data/vault.db"
def key(password): return hashlib.sha256(password.encode()).digest()
def init_db():
    os.makedirs("data",exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title BLOB, content BLOB)")
def save_note(title,content,password):
    nonce=AESGCM.generate_nonce(12); k=key(password)
    title_enc=nonce+AESGCM(k).encrypt(nonce,title.encode(),None)
    nonce2=AESGCM.generate_nonce(12); content_enc=nonce2+AESGCM(k).encrypt(nonce2,content.encode(),None)
    with sqlite3.connect(DB) as c: c.execute("INSERT INTO notes(title,content) VALUES(?,?)",(title_enc,content_enc))
def get_notes(password):
    with sqlite3.connect(DB) as c: rows=c.execute("SELECT id,title,content FROM notes").fetchall()
    k=key(password); result=[]
    for i,t,cipher in rows:
        try:
            title=AESGCM(k).decrypt(t[:12],t[12:],None).decode()
            content=AESGCM(k).decrypt(cipher[:12],cipher[12:],None).decode()
            result.append((i,title,content))
        except Exception: result.append((i,"[Gagal decrypt]","Password salah atau data rusak"))
    return result
