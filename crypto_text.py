import base64, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def caesar(text, shift=3):
    out=[]
    for ch in text:
        if 'a'<=ch<='z': out.append(chr((ord(ch)-97+shift)%26+97))
        elif 'A'<=ch<='Z': out.append(chr((ord(ch)-65+shift)%26+65))
        else: out.append(ch)
    return ''.join(out)

def caesar_decrypt(text, shift=3): return caesar(text,-shift)

def key_from_password(password): return hashlib.sha256(password.encode()).digest()

def encrypt_text(text, password):
    stage1=caesar(text)
    key=key_from_password(password)
    nonce=AESGCM.generate_nonce(12)
    cipher=AESGCM(key).encrypt(nonce,stage1.encode(),None)
    return base64.b64encode(nonce+cipher).decode()

def decrypt_text(ciphertext, password):
    raw=base64.b64decode(ciphertext)
    stage1=AESGCM(key_from_password(password)).decrypt(raw[:12],raw[12:],None).decode()
    return caesar_decrypt(stage1)
