import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

KEY_DIR="keys"
PRIV=KEY_DIR+"/private.pem"
PUB=KEY_DIR+"/public.pem"

def ensure_keys():
    os.makedirs(KEY_DIR,exist_ok=True)
    if not os.path.exists(PRIV):
        key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        with open(PRIV,"wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
        with open(PUB,"wb") as f:
            f.write(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
    return open(PUB,"rb").read(),open(PRIV,"rb").read()

def encrypt_file(data):
    pub_pem,_=ensure_keys()
    pub=serialization.load_pem_public_key(pub_pem)
    aeskey=AESGCM.generate_key(256); nonce=AESGCM.generate_nonce(12)
    cipher=AESGCM(aeskey).encrypt(nonce,data,None)
    wrapped=pub.encrypt(aeskey,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    return b"SV1"+len(wrapped).to_bytes(2,"big")+wrapped+nonce+cipher

def decrypt_file(data):
    _,priv_pem=ensure_keys()
    priv=serialization.load_pem_private_key(priv_pem,password=None)
    if data[:3]!=b"SV1": raise ValueError("Format file tidak dikenali.")
    n=int.from_bytes(data[3:5],"big"); wrapped=data[5:5+n]; nonce=data[5+n:17+n]; cipher=data[17+n:]
    aeskey=priv.decrypt(wrapped,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    return AESGCM(aeskey).decrypt(nonce,cipher,None)
