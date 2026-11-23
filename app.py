import streamlit as st
from auth import register, login, init_auth_db
from dongle import check_dongle, DONGLE_PATH
from crypto_text import encrypt_text, decrypt_text
from crypto_file import encrypt_file, decrypt_file
from database import init_db, save_note, get_notes
from steganography import hide_message, reveal_message
from blockchain import Chain

# ================= KONFIGURASI =================
st.set_page_config(page_title="SecureVault", layout="wide")

# ================= TEMA DAN CSS =================
# Palet: #231F2E (ink), #66ACDB (blue), #71F05F (green), #FFFFFF (white)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    color-scheme: light;
    --ink:#231F2E;
    --blue:#66ACDB;
    --green:#71F05F;
    --white:#FFFFFF;
    --bg:#F6F9FC;
    --line:#E1E8F0;
    --line-strong:#C9D5E2;
    --text:#3B3750;
    --muted:#6A6780;
    --blue-soft:#EAF3FA;
    --green-soft:#EAFBE7;
    --grad:linear-gradient(100deg,#71F05F 0%,#66ACDB 100%);
    --display:'Inter',sans-serif;
}

html,body,[class*="css"] {
    font-family:'Inter',sans-serif;
}

.stApp {
    background:var(--bg);
    color:var(--ink);
}

/* HEADER DAN JARAK ATAS */
header[data-testid="stHeader"] {
    background:transparent!important;
}
[data-testid="stToolbar"] {
    visibility:hidden;
}
[data-testid="stDecoration"] {
    display:none;
}
.block-container {
    max-width:1280px;
    padding-top:2.8rem!important;
    padding-bottom:3rem!important;
}

/* TIPOGRAFI */
h1,h2,h3,h4,h5,p,label,li {
    color:var(--ink);
}
h1,h2 {
    font-family:var(--display)!important;
    font-weight:700!important;
    letter-spacing:-0.02em;
}
h3 {
    font-weight:700!important;
    letter-spacing:-0.01em;
}
[data-testid="stCaptionContainer"] p {
    color:var(--muted)!important;
}
hr {
    border-color:var(--line)!important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background:var(--white);
    border-right:1px solid var(--line);
}
[data-testid="stSidebar"] .block-container {
    padding-top:2rem!important;
}
[data-testid="stSidebar"] hr {
    border-color:var(--line)!important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color:var(--text)!important;
}
.sv-side-brand {
    display:flex;
    align-items:center;
    gap:10px;
    margin-bottom:4px;
}
.sv-side-logo {
    width:32px;
    height:32px;
    border-radius:9px;
    background:var(--grad);
    color:var(--ink);
    font-family:var(--display);
    font-weight:800;
    font-size:17px;
    display:flex;
    align-items:center;
    justify-content:center;
}
.sv-side-name {
    font-size:18px;
    font-weight:700;
    color:var(--ink);
}
.sv-status {
    display:flex;
    align-items:center;
    gap:8px;
    background:var(--green-soft);
    border:1px solid #A9EDA0;
    border-radius:10px;
    padding:9px 12px;
    color:#1E5A17;
    font-size:13px;
    font-weight:600;
    margin:14px 0;
}
.sv-status::before {
    content:"";
    width:8px;
    height:8px;
    border-radius:50%;
    background:#3FC72E;
}

/* RADIO MENU */
[data-testid="stRadio"] [role="radiogroup"] {
    gap:4px;
}
[data-testid="stRadio"] label {
    border-radius:10px;
    padding:8px 12px;
    border-left:3px solid transparent;
    transition:background .15s;
}
[data-testid="stRadio"] label:hover {
    background:var(--bg);
}
[data-testid="stRadio"] label:has(input:checked) {
    background:var(--blue-soft);
    border-left:3px solid var(--blue);
}
[data-testid="stRadio"] label:has(input:checked) p {
    font-weight:600;
}

/* INPUT */
.stTextInput label,.stTextArea label,.stSelectbox label,
.stNumberInput label,.stFileUploader label {
    color:var(--ink)!important;
    font-weight:600;
}
.stTextInput input,.stTextArea textarea,
.stNumberInput input,.stSelectbox div[data-baseweb="select"] {
    background:var(--white)!important;
    color:var(--ink)!important;
    border:1px solid var(--line-strong)!important;
    border-radius:10px!important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color:#8E8CA3!important;
    opacity:1!important;
}
.stTextInput input:focus,.stTextArea textarea:focus {
    border-color:var(--blue)!important;
    box-shadow:0 0 0 3px #66ACDB33!important;
}
[data-testid="stTextInput"] button {
    background:transparent!important;
    color:var(--muted)!important;
}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"] {
    background:var(--white)!important;
    border-radius:10px!important;
}

/* BUTTON */
.stButton>button {
    background:var(--grad)!important;
    color:var(--ink)!important;
    border:0!important;
    border-radius:10px!important;
    font-weight:700!important;
    min-height:44px;
    transition:filter .2s, box-shadow .2s;
}
.stButton>button p {
    color:var(--ink)!important;
}
.stButton>button:hover {
    filter:brightness(1.05);
    box-shadow:0 6px 18px #66ACDB55;
}
.stDownloadButton>button {
    background:var(--white)!important;
    color:var(--ink)!important;
    border:1.5px solid var(--blue)!important;
    border-radius:10px!important;
    font-weight:600!important;
    min-height:44px;
}
.stDownloadButton>button p {
    color:var(--ink)!important;
}
.stDownloadButton>button:hover {
    background:var(--blue-soft)!important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background:transparent!important;
    border-bottom:1px solid var(--line);
    gap:28px;
}
.stTabs [data-baseweb="tab"] {
    background:transparent!important;
    color:var(--muted)!important;
    border:0!important;
    padding:12px 4px;
    font-weight:600;
}
.stTabs [data-baseweb="tab"]:hover {
    color:var(--ink)!important;
}
.stTabs [aria-selected="true"] {
    color:var(--ink)!important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background:var(--grad)!important;
    height:3px!important;
}
.stTabs [data-baseweb="tab-border"] {
    background:transparent!important;
}

/* BRAND */
.sv-brand {
    display:flex;
    align-items:center;
    gap:14px;
    margin-bottom:28px;
}
.sv-logo {
    width:50px;
    height:50px;
    border-radius:14px;
    background:var(--grad);
    color:var(--ink);
    font-family:var(--display);
    font-weight:800;
    font-size:26px;
    display:flex;
    align-items:center;
    justify-content:center;
}
.sv-brand-name {
    font-size:26px;
    font-weight:700;
    letter-spacing:-0.02em;
    line-height:1.2;
    background:linear-gradient(90deg,#71F05F 0%,#66ACDB 45%,#231F2E 100%);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
    display:inline-block;
}
.sv-brand-sub {
    color:var(--muted);
    font-size:12px;
    margin-top:2px;
}

/* HERO */
.sv-hero {
    background:
        radial-gradient(circle at 100% 0%,#FFFFFFD9 0%,#FFFFFF00 28%),
        linear-gradient(250deg,#71F05F 0%,#66ACDB 24%,#3E5A86 50%,#231F2E 78%);
    border-radius:20px;
    padding:48px 44px;
    margin-bottom:32px;
}
.sv-hero-title {
    color:var(--white);
    font-family:var(--display);
    font-size:36px;
    font-weight:700;
    line-height:1.25;
    letter-spacing:-0.025em;
    margin-bottom:14px;
    max-width:620px;
}
.sv-hero-desc {
    color:#FFFFFFD9;
    font-size:15px;
    line-height:1.75;
    max-width:520px;
}

/* FEATURE CARD */
.sv-card {
    position:relative;
    background:var(--white);
    border:1px solid var(--line);
    border-radius:14px;
    padding:22px 22px 20px;
    margin-bottom:14px;
    overflow:hidden;
}
.sv-card::before {
    content:"";
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:4px;
    background:linear-gradient(180deg,#71F05F,#66ACDB);
}
.sv-card-title {
    color:var(--ink);
    font-size:16px;
    font-weight:700;
    margin-bottom:6px;
}
.sv-card-desc {
    color:var(--text);
    font-size:13.5px;
    line-height:1.7;
}
.sv-login-title {
    color:var(--ink);
    font-family:var(--display);
    font-size:28px;
    font-weight:700;
    letter-spacing:-0.02em;
    margin:8px 0 6px;
}
.sv-login-desc {
    color:var(--muted);
    font-size:14px;
    margin-bottom:22px;
    line-height:1.7;
}
.sv-footer {
    text-align:center;
    color:var(--muted);
    font-size:12px;
    line-height:1.9;
    padding:24px 0;
}

/* ALERT - SUCCESS, INFO, WARNING, ERROR */
[data-testid="stAlert"],
[data-testid="stAlertContainer"] {
    background:var(--blue-soft)!important;
    border:1px solid #BBD9EE!important;
    border-radius:12px!important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span,
[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] div,
[data-testid="stAlertContainer"] span {
    color:var(--ink)!important;
}
[data-testid="stAlert"][kind="success"],
[data-testid="stAlertContainer"][kind="success"] {
    background:var(--green-soft)!important;
    border-color:#A9EDA0!important;
}
[data-testid="stAlert"][kind="info"],
[data-testid="stAlertContainer"][kind="info"] {
    background:var(--blue-soft)!important;
    border-color:#BBD9EE!important;
}
[data-testid="stAlert"][kind="warning"],
[data-testid="stAlertContainer"][kind="warning"] {
    background:#FFF7E1!important;
    border-color:#F0D58A!important;
}
[data-testid="stAlert"][kind="error"],
[data-testid="stAlertContainer"][kind="error"] {
    background:#FDECEF!important;
    border-color:#F0B3BE!important;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background:#F3F9FD!important;
    border:1.5px dashed var(--blue)!important;
    border-radius:14px!important;
    padding:12px!important;
}
[data-testid="stFileUploader"] section {
    background:var(--white)!important;
    border:1px solid var(--line)!important;
    border-radius:10px!important;
}
[data-testid="stFileUploader"] section * {
    color:var(--ink)!important;
}
[data-testid="stFileUploader"] button {
    background:var(--white)!important;
    color:var(--ink)!important;
    border:1.5px solid var(--blue)!important;
    border-radius:9px!important;
}
[data-testid="stFileUploader"] small {
    color:var(--muted)!important;
}

/* METRIC */
[data-testid="stMetric"] {
    background:var(--white);
    border:1px solid var(--line);
    border-top:3px solid var(--blue);
    border-radius:12px;
    padding:16px 18px;
}
[data-testid="stMetricLabel"] {
    color:var(--muted)!important;
}
[data-testid="stMetricValue"] {
    color:var(--ink)!important;
    font-size:1.25rem!important;
    font-weight:700!important;
}

/* EXPANDER DAN TABLE */
[data-testid="stExpander"] {
    background:var(--white)!important;
    border:1px solid var(--line)!important;
    border-radius:12px!important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color:var(--ink)!important;
    font-weight:600;
}
[data-testid="stTable"],[data-testid="stDataFrame"] {
    color:var(--ink);
}

/* CODE DAN JSON */
.stCode,pre {
    background:#F1F5F9!important;
    color:var(--ink)!important;
    border:1px solid var(--line)!important;
    border-radius:10px!important;
}
.stCode code,pre code {
    color:var(--ink)!important;
}
[data-testid="stJson"] {
    background:var(--white);
    border:1px solid var(--line);
    border-radius:10px;
    padding:12px;
}

/* FOOTER STREAMLIT */
footer {
    visibility:hidden;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNGSI TAMPILAN =================
def app_brand():
    st.markdown("""
    <div class="sv-brand">
        <div class="sv-logo">S</div>
        <div>
            <div class="sv-brand-name">SecureVault</div>
            <div class="sv-brand-sub">Secure your digital assets</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def feature_card(title, description):
    st.markdown(f"""
    <div class="sv-card">
        <div class="sv-card-title">{title}</div>
        <div class="sv-card-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def show_hero():
    st.markdown("""
    <div class="sv-hero">
        <div class="sv-hero-title">Keamanan digital dalam satu tempat.</div>
        <div class="sv-hero-desc">
            Selamat datang di SecureVault. Lindungi pesan, file, dan informasi
            penting melalui sistem keamanan berlapis yang terintegrasi.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= INISIALISASI =================
init_auth_db()
init_db()

if "chain" not in st.session_state:
    st.session_state.chain = Chain()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_pending" not in st.session_state:
    st.session_state.login_pending = False
if "bio_verified" not in st.session_state:
    st.session_state.bio_verified = False

# ================= LOGIN DAN REGISTER =================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"
if "flash" not in st.session_state:
    st.session_state.flash = None

def do_register():
    ru = st.session_state.get("reg_user", "")
    rp = st.session_state.get("reg_pass", "")
    if ru and rp and register(ru, rp):
        st.session_state.flash = ("success", "Akun berhasil dibuat. Silakan Login.")
        st.session_state.auth_mode = "Login"
    else:
        st.session_state.flash = ("error", "Akun sudah terdaftar atau data belum lengkap.")

def back_to_login():
    st.session_state.login_pending = False
    st.session_state.bio_verified = False
    st.session_state.pop("pending_password", None)

if not st.session_state.authenticated:

    # ---------- HALAMAN VERIFIKASI KEAMANAN ----------
    if st.session_state.login_pending:
        app_brand()
        st.markdown("## Verifikasi Keamanan")
        st.caption("Selesaikan tahapan verifikasi untuk mengakses SecureVault.")

        usb_col, bio_col = st.columns(2, gap="large")

        with usb_col:
            feature_card("USB Dongle", "Hubungkan perangkat USB yang berisi securevault.key.")
            st.caption(f"Lokasi USB Dongle: {DONGLE_PATH}")
            if check_dongle():
                st.success("USB Dongle berhasil terdeteksi.")
            else:
                st.error("USB Dongle tidak ditemukan. Pasang flashdisk yang berisi securevault.key.")

        with bio_col:
            feature_card("Fingerprint Verification", "Lakukan verifikasi sidik jari untuk melanjutkan.")
            if not st.session_state.bio_verified:
                st.info("Verifikasi fingerprint saat ini masih berupa simulasi.")
                if st.button("Simulasikan Verifikasi Fingerprint", use_container_width=True):
                    st.session_state.bio_verified = True
                    st.rerun()
            else:
                st.success("Verifikasi fingerprint berhasil.")

        if check_dongle() and st.session_state.bio_verified:
            st.success("Seluruh tahapan verifikasi berhasil.")
            st.session_state.authenticated = True
            st.session_state.vault_password = st.session_state.pending_password
            st.session_state.login_pending = False
            st.session_state.bio_verified = False
            del st.session_state.pending_password
            st.rerun()

        st.divider()
        st.button("Kembali ke Login", on_click=back_to_login)
        st.stop()

    # ---------- HALAMAN LOGIN / REGISTER ----------
    app_brand()
    show_hero()

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("### Perlindungan Berlapis")
        st.caption("Berbagai mekanisme keamanan dalam satu aplikasi.")
        feature_card("Advanced Encryption", "Lindungi pesan dan file menggunakan algoritma kriptografi.")
        feature_card("USB Dongle Verification", "Verifikasi akses tambahan menggunakan file kunci USB.")
        feature_card("Biometric Verification", "Simulasi verifikasi sidik jari sebagai bagian dari proses autentikasi.")
        st.markdown("""
        <div class="sv-footer">
            SecureVault, sistem kriptografi berlapis<br>
            Proyek demonstrasi akademik
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sv-login-title">Akses SecureVault</div>', unsafe_allow_html=True)
        st.markdown('<div class="sv-login-desc">Masuk ke akun atau buat akun baru untuk melanjutkan.</div>', unsafe_allow_html=True)

        st.radio("Mode", ["Login", "Register"], key="auth_mode",
                 horizontal=True, label_visibility="collapsed")

        if st.session_state.flash:
            kind, msg_text = st.session_state.flash
            st.session_state.flash = None
            (st.success if kind == "success" else st.error)(msg_text)

        if st.session_state.auth_mode == "Login":
            st.markdown("### Selamat Datang Kembali")
            st.caption("Masukkan username dan password akunmu.")
            u = st.text_input("Username", key="login_user", placeholder="Masukkan username")
            p = st.text_input("Password", type="password", key="login_pass", placeholder="Masukkan password")

            if st.button("Login", use_container_width=True):
                if not u or not p:
                    st.error("Username dan password wajib diisi.")
                elif login(u, p):
                    st.session_state.login_pending = True
                    st.session_state.pending_password = p
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        else:
            st.markdown("### Buat Akun Baru")
            st.caption("Daftarkan akun untuk menggunakan SecureVault.")
            st.text_input("Username Baru", key="reg_user", placeholder="Buat username")
            st.text_input("Password Baru", type="password", key="reg_pass", placeholder="Buat password")
            st.button("Buat Akun", use_container_width=True, on_click=do_register)

    st.stop()

# ================= PEMERIKSAAN USB DONGLE =================
if st.session_state.authenticated and not check_dongle():
    st.session_state.authenticated = False
    st.session_state.bio_verified = False
    st.session_state.login_pending = False
    st.session_state.pop("vault_password", None)
    st.error("USB Dongle dilepas atau tidak ditemukan!")
    st.warning("Sesi SecureVault dikunci. Pasang kembali USB Dongle dan Login ulang.")
    st.stop()

# ================= SIDEBAR =================
st.sidebar.markdown("""
<div class="sv-side-brand">
    <div class="sv-side-logo">S</div>
    <div class="sv-side-name">SecureVault</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sv-status">Signed in</div>', unsafe_allow_html=True)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.bio_verified = False
    st.session_state.login_pending = False
    st.session_state.pop("vault_password", None)
    st.rerun()

st.sidebar.divider()
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Text Encryption",
    "File Encryption",
    "Secure Database",
    "Steganography",
    "Blockchain Assets"
])
st.sidebar.divider()
st.sidebar.caption("Sistem Kriptografi Berlapis")
st.sidebar.caption("Proyek Demonstrasi Akademik")

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.markdown("## Dashboard")
    st.caption("Pusat pengelolaan keamanan digital SecureVault.")

    st.markdown("""
    <div class="sv-hero">
        <div class="sv-hero-title">Selamat datang di SecureVault</div>
        <div class="sv-hero-desc">
            Kelola dan lindungi informasi digital melalui berbagai fitur
            keamanan dalam satu aplikasi.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    for col, label in zip(cols, ["Text + AES", "Hybrid File", "Encrypted DB", "Steganography", "Blockchain"]):
        col.metric("Modul", label)

    st.markdown("### Fitur Keamanan")
    c1, c2 = st.columns(2)
    with c1:
        feature_card("Text Encryption", "Enkripsi dan dekripsi pesan menggunakan Caesar dan AES-GCM.")
        feature_card("File Encryption", "Lindungi file menggunakan kombinasi RSA-OAEP dan AES-GCM.")
        feature_card("Secure Database", "Simpan catatan penting dalam database terenkripsi.")
    with c2:
        feature_card("Steganography", "Sembunyikan dan tampilkan pesan di dalam gambar.")
        feature_card("Blockchain Assets", "Catat aset dan periksa integritas data blockchain.")
    st.warning("SecureVault merupakan aplikasi demonstrasi akademik, bukan sistem keamanan untuk produksi.")

# ================= TEXT ENCRYPTION =================
elif menu == "Text Encryption":
    st.markdown("## Text Encryption")
    st.caption("Enkripsi dan dekripsi pesan menggunakan Caesar dan AES-GCM.")

    text = st.text_area("Pesan yang akan dienkripsi", placeholder="Masukkan pesan di sini...")
    pw = st.text_input("Password Enkripsi", type="password", key="text_enc_pw")

    if st.button("Encrypt Text", use_container_width=True):
        if text and pw:
            try:
                st.session_state.text_cipher = encrypt_text(text, pw)
                st.success("Pesan berhasil dienkripsi.")
            except Exception as e:
                st.error(f"Enkripsi gagal: {e}")
        else:
            st.warning("Masukkan pesan dan password terlebih dahulu.")

    if st.session_state.get("text_cipher"):
        st.markdown("### Hasil Enkripsi")
        st.text_area("Ciphertext (Base64)", st.session_state.text_cipher)
        st.download_button("Download Ciphertext", st.session_state.text_cipher, file_name="message.enc.txt")

    st.divider()
    st.markdown("### Dekripsi Pesan")
    cipher = st.text_area("Masukkan Ciphertext", key="text_decrypt_input")
    dpw = st.text_input("Password Dekripsi", type="password", key="text_decrypt_pw")

    if st.button("Decrypt Text", use_container_width=True):
        if not cipher or not dpw:
            st.warning("Masukkan ciphertext dan password.")
        else:
            try:
                st.success(decrypt_text(cipher, dpw))
            except Exception:
                st.error("Dekripsi gagal. Periksa ciphertext dan password.")

# ================= FILE ENCRYPTION =================
elif menu == "File Encryption":
    st.markdown("## File Encryption")
    st.caption("Enkripsi file menggunakan RSA-OAEP dan AES-GCM.")

    st.markdown("### Enkripsi File")
    up = st.file_uploader("Pilih file yang akan dienkripsi", key="file_enc")

    if up and st.button("Encrypt File", use_container_width=True):
        try:
            enc = encrypt_file(up.getvalue())
            st.success("File berhasil dienkripsi.")
            st.download_button("Download Encrypted File", enc, file_name=up.name + ".svenc")
        except Exception as e:
            st.error(f"Enkripsi gagal: {e}")

    st.divider()
    st.markdown("### Dekripsi File")
    encup = st.file_uploader("Pilih file .svenc untuk didekripsi", key="filedec")

    if encup and st.button("Decrypt File", use_container_width=True):
        try:
            decrypted = decrypt_file(encup.getvalue())
            original_name = encup.name.removesuffix(".svenc")
            st.success("File berhasil didekripsi.")
            st.download_button("Download Decrypted File", decrypted, file_name=original_name)
        except Exception as e:
            st.error(f"Dekripsi gagal: {e}")

# ================= SECURE DATABASE =================
elif menu == "Secure Database":
    st.markdown("## Secure Database")
    st.caption("Simpan dan baca catatan penting menggunakan enkripsi AES-GCM.")

    st.markdown("### Simpan Catatan")
    title = st.text_input("Judul Catatan", placeholder="Masukkan judul catatan")
    body = st.text_area("Isi Catatan", placeholder="Tuliskan informasi penting...")
    pw = st.text_input("Password Enkripsi Database", type="password", key="db_save_pw")

    if st.button("Save Encrypted Note", use_container_width=True):
        if title and body and pw:
            try:
                save_note(title, body, pw)
                st.success("Catatan berhasil disimpan dalam bentuk terenkripsi.")
            except Exception as e:
                st.error(f"Gagal menyimpan catatan: {e}")
        else:
            st.warning("Lengkapi semua kolom terlebih dahulu.")

    st.divider()
    st.markdown("### Baca Catatan")
    readpw = st.text_input("Password untuk Membuka Catatan", type="password", key="readpw")

    if st.button("Read Notes", use_container_width=True):
        if not readpw:
            st.warning("Masukkan password terlebih dahulu.")
        else:
            try:
                notes = get_notes(readpw)
                if notes:
                    for i, title, content in notes:
                        with st.expander(f"Catatan #{i} — {title}"):
                            st.write(content)
                else:
                    st.info("Belum ada catatan yang dapat ditampilkan.")
            except Exception as e:
                st.error(f"Gagal membaca catatan: {e}")

# ================= STEGANOGRAPHY =================
elif menu == "Steganography":
    st.markdown("## Steganography")
    st.caption("Sembunyikan pesan di dalam gambar dan tampilkan kembali pesan tersebut.")

    st.markdown("### Sembunyikan Pesan")
    img = st.file_uploader("Pilih gambar", type=["png", "jpg", "jpeg"], key="hide_img")
    msg = st.text_area("Pesan yang akan disembunyikan")

    if img and msg and st.button("Hide Message", use_container_width=True):
        try:
            result = hide_message(img.getvalue(), msg)
            st.success("Pesan berhasil disembunyikan dalam gambar.")
            st.download_button("Download Gambar", result, file_name="hidden_message.png")
        except Exception as e:
            st.error(f"Gagal menyembunyikan pesan: {e}")

    st.divider()
    st.markdown("### Tampilkan Pesan")
    reveal = st.file_uploader("Pilih gambar PNG", type=["png"], key="revealimg")

    if reveal and st.button("Reveal Message", use_container_width=True):
        try:
            st.code(reveal_message(reveal.getvalue()))
        except Exception as e:
            st.error(f"Tidak dapat membaca pesan: {e}")

# ================= BLOCKCHAIN ASSETS =================
elif menu == "Blockchain Assets":
    st.markdown("## Blockchain Assets")
    st.caption("Catat aset digital dan periksa integritas data menggunakan blockchain demo.")

    st.markdown("### Registrasi Aset")
    asset = st.text_input("Nama Aset / Dokumen", placeholder="Masukkan nama aset")
    owner = st.text_input("Nama Pemilik", placeholder="Masukkan nama pemilik")

    if st.button("Register Asset", use_container_width=True):
        if asset and owner:
            try:
                st.session_state.chain.add(asset, owner)
                st.success("Aset berhasil dicatat dalam blockchain.")
            except Exception as e:
                st.error(f"Gagal mencatat aset: {e}")
        else:
            st.warning("Nama aset dan pemilik wajib diisi.")

    st.divider()
    st.markdown("### Status Integritas Blockchain")
    if st.session_state.chain.valid():
        st.success("VALID — Integritas blockchain terjaga.")
    else:
        st.error("INVALID — Terdapat perubahan pada data blockchain.")

    with st.expander("Lihat Data Blockchain"):
        st.json(st.session_state.chain.blocks)