
import streamlit as st

from auth import register, login, user_exists
from dongle import check_dongle, get_dongle_path
from face_auth import enroll_face, verify_face
from crypto_text import encrypt_text, decrypt_text
from crypto_file import encrypt_file, decrypt_file
from database import init_db, save_note, get_notes
from steganography import hide_message, reveal_message
from blockchain import Chain


# =====================================================
# KONFIGURASI APLIKASI
# =====================================================

st.set_page_config(
    page_title="SecureVault",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 SecureVault")
st.caption("Multi-Layer Cryptography System — academic demo")

# Inisialisasi database
init_db()

# Inisialisasi session state
if "chain" not in st.session_state:
    st.session_state.chain = Chain()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "pending_login" not in st.session_state:
    st.session_state.pending_login = False


# =====================================================
# FUNGSI LOGOUT
# =====================================================

def logout():
    st.session_state.authenticated = False
    st.session_state.pending_login = False

    st.session_state.pop("vault_password", None)
    st.session_state.pop("login_user", None)


# =====================================================
# PEMERIKSAAN USB DONGLE
# =====================================================

if st.session_state.authenticated and not check_dongle():
    logout()
    st.warning(
        "USB Dongle terlepas. Sesi dikunci. "
        "Pasang kembali flashdisk yang berisi securevault.key."
    )


# =====================================================
# HALAMAN LOGIN DAN REGISTER
# =====================================================

if not st.session_state.authenticated:

    # -------------------------------------------------
    # TAHAP VERIFIKASI SETELAH PASSWORD BENAR
    # -------------------------------------------------

    if st.session_state.pending_login:

        st.subheader("🔐 Verifikasi Akses")

        dongle_path = get_dongle_path()

        st.caption(
            f"Lokasi USB Dongle: {dongle_path}"
        )

        # Pemeriksaan USB
        if not check_dongle():

            st.error(
                "USB Dongle tidak ditemukan. "
                "Pasang flashdisk yang berisi securevault.key."
            )

            st.info(
                "Pastikan flashdisk terpasang dan file "
                "securevault.key berada di dalamnya."
            )

            if st.button("Periksa USB Lagi"):
                st.rerun()

        else:

            st.success("USB Dongle berhasil terdeteksi.")

            # -----------------------------------------
            # VERIFIKASI WAJAH
            # -----------------------------------------

            st.subheader("👤 Face Recognition")

            st.write(
                "Posisikan wajah di depan kamera. "
                "Ambil foto untuk mencocokkan wajah "
                "dengan data yang sudah didaftarkan."
            )

            face_photo = st.camera_input(
                "Ambil foto wajah untuk verifikasi",
                key="login_face_camera"
            )

            if st.button(
                "Verifikasi Wajah",
                disabled=face_photo is None
            ):

                matched, message = verify_face(
                    st.session_state.get("login_user", ""),
                    face_photo.getvalue()
                )

                if matched:

                    st.success(message)

                    st.session_state.authenticated = True
                    st.session_state.pending_login = False

                    st.rerun()

                else:

                    st.error(message)

        # Tombol kembali
        if st.button("Batal / Kembali ke Login"):

            st.session_state.pending_login = False

            st.rerun()

    # -------------------------------------------------
    # HALAMAN LOGIN DAN REGISTER
    # -------------------------------------------------

    else:

        login_tab, register_tab = st.tabs(
            ["Login", "Register (First Use)"]
        )

        # =============================================
        # LOGIN
        # =============================================

        with login_tab:

            st.subheader("Login SecureVault")

            username = st.text_input(
                "Username",
                key="login_user"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_pass"
            )

            if st.button("Login"):

                if login(username, password):

                    st.session_state.pending_login = True

                    st.rerun()

                else:

                    st.error(
                        "Login gagal. Username atau password salah."
                    )

        # =============================================
        # REGISTER
        # =============================================

        with register_tab:

            st.subheader("Buat Akun Baru")

            new_user = st.text_input(
                "Create Username",
                key="reg_user"
            )

            new_password = st.text_input(
                "Create Password",
                type="password",
                key="reg_pass"
            )

            st.write(
                "Pendaftaran wajah: ambil 5 foto wajah "
                "dengan sudut sedikit berbeda dan pencahayaan cukup."
            )

            # Mengambil lima foto wajah
            face_photos = []

            for photo_number in range(1, 6):

                photo = st.camera_input(
                    f"Foto Wajah {photo_number}",
                    key=f"register_face_{photo_number}"
                )

                if photo is not None:

                    face_photos.append(photo.getvalue())

            # -----------------------------------------
            # PROSES PENDAFTARAN AKUN
            # -----------------------------------------

            if st.button("Create Account and Register Face"):

                # Validasi username dan password
                if not new_user.strip() or not new_password:

                    st.error(
                        "Username dan password wajib diisi."
                    )

                # Validasi jumlah foto
                elif len(face_photos) < 5:

                    st.error(
                        "Silakan ambil kelima foto wajah terlebih dahulu."
                    )

                # Periksa username duplikat
                elif user_exists(new_user):

                    st.error(
                        "Username sudah terdaftar. "
                        "Silakan gunakan username lain."
                    )

                else:

                    # Daftarkan model wajah
                    face_ok, face_message = enroll_face(
                        new_user,
                        face_photos
                    )

                    if not face_ok:

                        st.error(face_message)

                    else:

                        # Simpan akun dan password
                        account_created = register(
                            new_user,
                            new_password
                        )

                        if account_created:

                            st.success(
                                "Akun dan data wajah berhasil didaftarkan!"
                            )

                            st.info(
                                "Silakan masuk melalui tab Login."
                            )

                        else:

                            st.error(
                                "Pendaftaran akun gagal. "
                                "Periksa kembali data akun."
                            )

    st.stop()


# =====================================================
# HALAMAN UTAMA SETELAH LOGIN BERHASIL
# =====================================================

st.sidebar.success("Signed in")

st.sidebar.success(
    "USB Dongle dan Face Recognition aktif."
)

if st.sidebar.button("Logout"):

    logout()

    st.rerun()


# =====================================================
# MENU NAVIGASI
# =====================================================

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Text Encryption",
        "File Encryption",
        "Secure Database",
        "Steganography",
        "Blockchain Assets"
    ]
)


# =====================================================
# DASHBOARD
# =====================================================

if menu == "Dashboard":

    st.header("Dashboard")

    st.write(
        "SecureVault demo: protect text, files, "
        "image messages, database notes, and asset records."
    )

    cols = st.columns(5)

    labels = [
        "Text + AES",
        "Hybrid File",
        "Encrypted DB",
        "Steganography",
        "Blockchain"
    ]

    for col, label in zip(cols, labels):

        col.metric("Module", label)

    st.warning(
        "Educational demo only; "
        "not designed for production security."
    )


# =====================================================
# TEXT ENCRYPTION
# =====================================================

elif menu == "Text Encryption":

    st.header("📝 Super Encryption: Caesar + AES-GCM")

    message = st.text_area("Message")

    password = st.text_input(
        "Encryption Password",
        type="password"
    )

    if st.button("Encrypt Text"):

        if message and password:

            try:

                st.session_state.text_cipher = encrypt_text(
                    message,
                    password
                )

                st.success("Text berhasil dienkripsi!")

            except Exception as error:

                st.error(f"Encryption failed: {error}")

        else:

            st.warning(
                "Masukkan pesan dan password terlebih dahulu."
            )

    if st.session_state.get("text_cipher"):

        st.text_area(
            "Ciphertext (Base64)",
            st.session_state.text_cipher
        )

        st.download_button(
            "Download Ciphertext",
            st.session_state.text_cipher,
            file_name="message.enc.txt"
        )

    cipher = st.text_area(
        "Paste Ciphertext for Decryption",
        key="text_decrypt_input"
    )

    decrypt_password = st.text_input(
        "Decryption Password",
        type="password",
        key="text_decrypt_pw"
    )

    if st.button("Decrypt Text"):

        try:

            if not cipher or not decrypt_password:
                st.warning("Masukkan ciphertext dan password.")
            else:
                decrypted = decrypt_text(
                    cipher,
                    decrypt_password
                )

                st.success("Decryption berhasil!")
                st.text_area(
                    "Decrypted Message",
                    decrypted
                )

        except Exception as error:

            st.error(f"Decrypt failed: {error}")


# =====================================================
# FILE ENCRYPTION
# =====================================================

elif menu == "File Encryption":

    st.header("📁 File Encryption: RSA-OAEP + AES-GCM")

    upload = st.file_uploader(
        "Upload File to Encrypt"
    )

    if upload and st.button("Encrypt File"):

        try:

            encrypted = encrypt_file(
                upload.getvalue()
            )

            st.download_button(
                "Download Encrypted File",
                encrypted,
                file_name=upload.name + ".svenc"
            )

            st.success("File berhasil dienkripsi!")

        except Exception as error:

            st.error(f"Encryption failed: {error}")

    encrypted_upload = st.file_uploader(
        "Upload .svenc to Decrypt",
        key="filedec"
    )

    if encrypted_upload and st.button("Decrypt File"):

        try:

            decrypted_file = decrypt_file(
                encrypted_upload.getvalue()
            )

            st.download_button(
                "Download Decrypted File",
                decrypted_file,
                file_name="decrypted_file"
            )

            st.success("File berhasil didekripsi!")

        except Exception as error:

            st.error(f"Decryption failed: {error}")


# =====================================================
# SECURE DATABASE
# =====================================================

elif menu == "Secure Database":

    st.header("🗄️ Encrypted Notes (SQLite + AES-GCM)")

    title = st.text_input("Note Title")

    body = st.text_area("Important Message")

    password = st.text_input(
        "Database Encryption Password",
        type="password"
    )

    if st.button("Save Encrypted Note"):

        if title and body and password:

            try:

                save_note(
                    title,
                    body,
                    password
                )

                st.success(
                    "Encrypted note berhasil disimpan."
                )

            except Exception as error:

                st.error(f"Save failed: {error}")

        else:

            st.warning("Isi semua kolom terlebih dahulu.")

    read_password = st.text_input(
        "Password to Decrypt Stored Notes",
        type="password",
        key="readpw"
    )

    if st.button("Read Notes"):

        try:

            notes = get_notes(read_password)

            if not notes:

                st.info("Belum ada catatan tersimpan.")

            for note_id, note_title, content in notes:

                st.write(f"#{note_id} — {note_title}")

                st.write(content)

                st.divider()

        except Exception as error:

            st.error(f"Read notes failed: {error}")


# =====================================================
# STEGANOGRAPHY
# =====================================================

elif menu == "Steganography":

    st.header("🖼️ Image Steganography (LSB)")

    image_upload = st.file_uploader(
        "Upload PNG Image",
        type=["png", "jpg", "jpeg"]
    )

    message = st.text_area(
        "Message to Hide"
    )

    if image_upload and message and st.button("Hide Message"):

        try:

            hidden_image = hide_message(
                image_upload.getvalue(),
                message
            )

            st.download_button(
                "Download Image with Hidden Message",
                hidden_image,
                file_name="hidden_message.png"
            )

            st.success("Pesan berhasil disembunyikan!")

        except Exception as error:

            st.error(f"Failed: {error}")

    reveal_upload = st.file_uploader(
        "Upload Image to Reveal",
        type=["png"],
        key="revealimg"
    )

    if reveal_upload and st.button("Reveal"):

        try:

            revealed_message = reveal_message(
                reveal_upload.getvalue()
            )

            st.success("Pesan berhasil ditemukan!")

            st.code(revealed_message)

        except Exception as error:

            st.error(f"Could not reveal: {error}")


# =====================================================
# BLOCKCHAIN ASSETS
# =====================================================

elif menu == "Blockchain Assets":

    st.header("⛓️ Blockchain Asset Ledger (Demo)")

    asset = st.text_input(
        "Asset / Document Name"
    )

    owner = st.text_input(
        "Owner"
    )

    if st.button("Register Asset"):

        if asset and owner:

            st.session_state.chain.add(
                asset,
                owner
            )

            st.success(
                "Asset successfully recorded in chain."
            )

        else:

            st.warning(
                "Isi nama aset dan pemilik terlebih dahulu."
            )

    st.write(
        "Chain Integrity:",
        "VALID ✅"
        if st.session_state.chain.valid()
        else "INVALID ❌"
    )

    st.json(
        st.session_state.chain.blocks
    )
