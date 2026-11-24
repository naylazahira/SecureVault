
from pathlib import Path
import string

DONGLE_FILENAME = "securevault.key"


def get_dongle_path():
    """Mencari securevault.key pada drive komputer."""
    for letter in string.ascii_uppercase:
        path = Path(f"{letter}:/") / DONGLE_FILENAME
        if path.is_file():
            return str(path)

    # Lokasi default jika flashdisk belum ditemukan
    return "E:/securevault.key"


def check_dongle():
    """Memeriksa apakah file dongle tersedia."""
    return Path(get_dongle_path()).is_file()


DONGLE_PATH = get_dongle_path()
