
import os
import sqlite3
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


DB = "data/vault.db"


def key(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).digest()


def init_db():
    os.makedirs("data", exist_ok=True)

    with sqlite3.connect(DB) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title BLOB,
                content BLOB
            )
        """)


def save_note(title, content, password):

    if not title or not content or not password:
        raise ValueError(
            "Judul, isi catatan, dan password wajib diisi."
        )

    init_db()

    aes_key = key(password)
    aes = AESGCM(aes_key)

    # Enkripsi judul
    nonce1 = os.urandom(12)

    title_enc = nonce1 + aes.encrypt(
        nonce1,
        title.encode("utf-8"),
        None
    )

    # Enkripsi isi catatan
    nonce2 = os.urandom(12)

    content_enc = nonce2 + aes.encrypt(
        nonce2,
        content.encode("utf-8"),
        None
    )

    with sqlite3.connect(DB) as conn:

        conn.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            (title_enc, content_enc)
        )


def get_notes(password):

    if not password:
        raise ValueError("Password wajib diisi.")

    init_db()

    with sqlite3.connect(DB) as conn:

        rows = conn.execute(
            "SELECT id, title, content FROM notes ORDER BY id DESC"
        ).fetchall()

    aes = AESGCM(key(password))

    result = []

    for note_id, title_data, content_data in rows:

        try:
            if len(title_data) < 28 or len(content_data) < 28:
                raise ValueError("Data tidak lengkap.")

            # Dekripsi judul
            title = aes.decrypt(
                title_data[:12],
                title_data[12:],
                None
            ).decode("utf-8")

            # Dekripsi isi
            content = aes.decrypt(
                content_data[:12],
                content_data[12:],
                None
            ).decode("utf-8")

            result.append(
                (note_id, title, content)
            )

        except Exception:
            result.append(
                (
                    note_id,
                    "[Gagal decrypt]",
                    "Password salah atau data rusak."
                )
            )

    return result
