
import os
import base64
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def caesar(text, shift=3):
    result = []

    for ch in text:
        if 'a' <= ch <= 'z':
            result.append(
                chr((ord(ch) - 97 + shift) % 26 + 97)
            )

        elif 'A' <= ch <= 'Z':
            result.append(
                chr((ord(ch) - 65 + shift) % 26 + 65)
            )

        else:
            result.append(ch)

    return ''.join(result)


def caesar_decrypt(text, shift=3):
    return caesar(text, -shift)


def key_from_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).digest()


def encrypt_text(text, password):
    if not text or not password:
        raise ValueError("Pesan dan password wajib diisi.")

    # Layer 1: Caesar Cipher
    stage1 = caesar(text)

    # Generate AES key
    key = key_from_password(password)

    # Generate nonce 12 byte
    nonce = os.urandom(12)

    # Layer 2: AES-GCM
    cipher = AESGCM(key).encrypt(
        nonce,
        stage1.encode("utf-8"),
        None
    )

    # Gabungkan nonce dan ciphertext
    result = nonce + cipher

    return base64.b64encode(result).decode("utf-8")


def decrypt_text(ciphertext, password):
    if not ciphertext or not password:
        raise ValueError("Ciphertext dan password wajib diisi.")

    try:
        raw = base64.b64decode(
            ciphertext,
            validate=True
        )

        if len(raw) < 28:
            raise ValueError("Ciphertext tidak valid.")

        nonce = raw[:12]
        cipher = raw[12:]

        key = key_from_password(password)

        # Layer 1: Dekripsi AES-GCM
        stage1 = AESGCM(key).decrypt(
            nonce,
            cipher,
            None
        ).decode("utf-8")

        # Layer 2: Dekripsi Caesar Cipher
        original = caesar_decrypt(stage1)

        return original

    except Exception as e:
        raise ValueError(
            "Dekripsi gagal. Periksa password atau ciphertext."
        ) from e
