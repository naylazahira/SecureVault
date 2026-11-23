
from pathlib import Path
import os
import ctypes
import string

# Nama file kunci USB
DONGLE_FILENAME = "securevault.key"
# Konfigurasi opsional melalui environment variable
CUSTOM_DONGLE_PATH = os.environ.get("SECUREVAULT_DONGLE_PATH")
# Kompatibilitas dengan app.py versi sebelumnya
DONGLE_PATH = CUSTOM_DONGLE_PATH or "Deteksi otomatis pada drive USB"

def get_removable_drives():
    """
    Mendeteksi seluruh drive USB/removable
    yang terhubung pada Windows.
    """
    drives = []

    if os.name != "nt":
        return drives

    bitmask = ctypes.windll.kernel32.GetLogicalDrives()

    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"

            # DRIVE_REMOVABLE = 2
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(
                ctypes.c_wchar_p(drive)
            )

            if drive_type == 2:
                drives.append(Path(drive))

        bitmask >>= 1

    return drives


def check_dongle():
    """
    Memeriksa keberadaan securevault.key.

    Prioritas:
    1. Lokasi custom dari environment variable.
    2. Semua drive USB yang terdeteksi otomatis.
    """

    # 1. Periksa lokasi custom jika dikonfigurasi
    if CUSTOM_DONGLE_PATH:
        custom_file = Path(CUSTOM_DONGLE_PATH)

        if (
            custom_file.exists()
            and custom_file.is_file()
            and custom_file.name.lower() == DONGLE_FILENAME
        ):
            return True

    # 2. Cari otomatis di semua USB
    for drive in get_removable_drives():
        dongle_file = drive / DONGLE_FILENAME

        if dongle_file.exists() and dongle_file.is_file():
            return True

    return False


def get_dongle_location():
    """
    Mengembalikan lokasi USB Dongle
    jika ditemukan.
    """

    if CUSTOM_DONGLE_PATH:
        custom_file = Path(CUSTOM_DONGLE_PATH)

        if custom_file.is_file():
            return str(custom_file)

    for drive in get_removable_drives():
        dongle_file = drive / DONGLE_FILENAME

        if dongle_file.is_file():
            return str(dongle_file)

    return "USB Dongle tidak ditemukan"
