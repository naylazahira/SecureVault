import streamlit as st
from pathlib import Path
from auth import register, login
from dongle import check_dongle, DONGLE_PATH
from crypto_text import encrypt_text,decrypt_text
from crypto_file import encrypt_file,decrypt_file
from database import init_db,save_note,get_notes
from steganography import hide_message,reveal_message
from blockchain import Chain

st.set_page_config(page_title="SecureVault",page_icon="🔐",layout="wide")
st.title("🔐 SecureVault")
st.caption("Multi-Layer Cryptography System — academic demo")
init_db()

# Persistent blockchain demo chain for this running session
if "chain" not in st.session_state: st.session_state.chain=Chain()

def gate():
    st.subheader("Access verification")
    st.info("Demo mode: biometric verification is simulated by a button. USB check can be disabled for first-time setup.")
    st.caption(f"Required dongle file: securevault.key — configured path: {DONGLE_PATH}")
    if not check_dongle():
        st.error("Dongle file not detected. Connect the USB and place securevault.key at the configured path.")
        return False
    st.success("Dongle detected.")
    if not st.session_state.get("bio",False):
        if st.button("👆 Simulate fingerprint verification"):
            st.session_state.bio=True; st.rerun()
        return False
    st.success("Fingerprint demo verified.")
    st.session_state.bio=False
    return True

if "authenticated" not in st.session_state: st.session_state.authenticated=False
if not st.session_state.authenticated:
    tab1,tab2=st.tabs(["Login","Register (first use)"])
    with tab1:
        u=st.text_input("Username",key="login_user"); p=st.text_input("Password",type="password",key="login_pass")
        if st.button("Login"):
            verified = gate()
            if verified and login(u,p):
                st.session_state.authenticated=True; st.session_state.vault_password=p; st.rerun()
            elif verified: st.error("Username/password invalid.")
    with tab2:
        ru=st.text_input("Create username",key="reg_user"); rp=st.text_input("Create password",type="password",key="reg_pass")
        if st.button("Create account"):
            if ru and rp and register(ru,rp): st.success("Account created. Login tab to sign in.")
            else: st.error("Account already exists or fields empty.")
    st.stop()

st.sidebar.success("Signed in")
if st.sidebar.button("Logout"):
    st.session_state.authenticated=False; st.session_state.bio=False; st.rerun()
menu=st.sidebar.radio("Menu",["Dashboard","Text Encryption","File Encryption","Secure Database","Steganography","Blockchain Assets"])

if menu=="Dashboard":
    st.header("Dashboard")
    st.write("SecureVault demo: protect text, files, image messages, database notes, and asset records.")
    cols=st.columns(5)
    for c,label in zip(cols,["Text + AES","Hybrid File","Encrypted DB","Steganography","Blockchain"]): c.metric("Module",label)
    st.warning("Educational demo only; not designed for production security.")
elif menu=="Text Encryption":
    st.header("📝 Super Encryption: Caesar + AES-GCM")
    text=st.text_area("Message")
    pw=st.text_input("Encryption password",type="password")
    if st.button("Encrypt text"):
        if text and pw:
            st.session_state.text_cipher=encrypt_text(text,pw); st.success("Encrypted!")
    if st.session_state.get("text_cipher"):
        st.text_area("Ciphertext (Base64)",st.session_state.text_cipher)
        st.download_button("Download ciphertext",st.session_state.text_cipher,file_name="message.enc.txt")
    cipher=st.text_area("Paste ciphertext for decryption",key="text_decrypt_input")
    dpw=st.text_input("Decryption password",type="password",key="text_decrypt_pw")
    if st.button("Decrypt text"):
        try: st.success(decrypt_text(cipher,dpw))
        except Exception: st.error("Decrypt failed. Check ciphertext/password.")
elif menu=="File Encryption":
    st.header("📁 File Encryption: RSA-OAEP + AES-GCM")
    up=st.file_uploader("Upload file to encrypt")
    if up and st.button("Encrypt file"):
        enc=encrypt_file(up.getvalue()); st.download_button("Download encrypted file",enc,file_name=up.name+".svenc")
    encup=st.file_uploader("Upload .svenc to decrypt",key="filedec")
    if encup and st.button("Decrypt file"):
        try: st.download_button("Download decrypted file",decrypt_file(encup.getvalue()),file_name="decrypted_file")
        except Exception as e: st.error(f"Decryption failed: {e}")
elif menu=="Secure Database":
    st.header("🗄️ Encrypted notes (SQLite + AES-GCM)")
    title=st.text_input("Note title"); body=st.text_area("Important message")
    pw=st.text_input("Database encryption password",type="password")
    if st.button("Save encrypted note"):
        if title and body and pw: save_note(title,body,pw); st.success("Encrypted note saved.")
        else: st.warning("Fill all fields.")
    readpw=st.text_input("Password to decrypt stored notes",type="password",key="readpw")
    if st.button("Read notes"):
        for i,t,c in get_notes(readpw): st.write(f"#{i} — {t}"); st.write(c)
elif menu=="Steganography":
    st.header("🖼️ Image Steganography (LSB)")
    img=st.file_uploader("Upload PNG image",type=["png","jpg","jpeg"])
    msg=st.text_area("Message to hide")
    if img and msg and st.button("Hide message"):
        try: st.download_button("Download image with hidden message",hide_message(img.getvalue(),msg),file_name="hidden_message.png")
        except Exception as e: st.error(f"Failed: {e}")
    reveal=st.file_uploader("Upload image to reveal message",type=["png"],key="revealimg")
    if reveal and st.button("Reveal"):
        try: st.code(reveal_message(reveal.getvalue()))
        except Exception as e: st.error(f"Could not reveal: {e}")
elif menu=="Blockchain Assets":
    st.header("⛓️ Blockchain Asset Ledger (demo)")
    asset=st.text_input("Asset / document name"); owner=st.text_input("Owner")
    if st.button("Register asset"):
        if asset and owner: st.session_state.chain.add(asset,owner); st.success("Asset recorded in chain.")
    st.write("Chain integrity:", "VALID ✅" if st.session_state.chain.valid() else "INVALID ❌")
    st.json(st.session_state.chain.blocks)
