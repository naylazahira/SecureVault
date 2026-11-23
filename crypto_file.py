
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


KEY_DIR = Path("keys")
PRIV = KEY_DIR / "private.pem"
PUB = KEY_DIR / "public.pem"


def ensure_keys():
    KEY_DIR.mkdir(parents=True, exist_ok=True)

    # Buat pasangan RSA jika salah satu file belum tersedia
    if not PRIV.exists() or not PUB.exists():
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        private_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_bytes = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        PRIV.write_bytes(private_bytes)
        PUB.write_bytes(public_bytes)

    return PUB.read_bytes(), PRIV.read_bytes()


def encrypt_file(data):
    if not data:
        raise ValueError("File kosong tidak dapat dienkripsi.")

    pub_pem, _ = ensure_keys()

    pub = serialization.load_pem_public_key(pub_pem)

    # Generate AES-256 key
    aeskey = AESGCM.generate_key(bit_length=256)

    # Generate nonce 12 byte
    nonce = os.urandom(12)

    # Enkripsi data menggunakan AES-GCM
    cipher = AESGCM(aeskey).encrypt(
        nonce,
        data,
        None
    )

    # Enkripsi AES key menggunakan RSA-OAEP
    wrapped = pub.encrypt(
        aeskey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Format: SV1 + panjang RSA key + RSA key + nonce + ciphertext
    return (
        b"SV1"
        + len(wrapped).to_bytes(2, "big")
        + wrapped
        + nonce
        + cipher
    )


def decrypt_file(data):
    if not data or len(data) < 5:
        raise ValueError("File terenkripsi tidak valid.")

    if data[:3] != b"SV1":
        raise ValueError("Format file tidak dikenali.")

    _, priv_pem = ensure_keys()

    priv = serialization.load_pem_private_key(
        priv_pem,
        password=None
    )

    n = int.from_bytes(data[3:5], "big")

    if n == 0 or len(data) < 5 + n + 12 + 16:
        raise ValueError("Data terenkripsi tidak lengkap.")

    wrapped = data[5:5+n]
    nonce = data[5+n:17+n]
    cipher = data[17+n:]

    # Dekripsi AES key menggunakan RSA
    aeskey = priv.decrypt(
        wrapped,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Dekripsi file menggunakan AES-GCM
    return AESGCM(aeskey).decrypt(
        nonce,
        cipher,
        None
    )
