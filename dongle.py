from pathlib import Path
import os

# Demo dongle: place this file on a USB drive and set DONGLE_PATH accordingly.
DONGLE_FILENAME = "securevault.key"
DONGLE_PATH = os.environ.get("SECUREVAULT_DONGLE_PATH", "D:/securevault.key")

def check_dongle():
    return Path(DONGLE_PATH).is_file() and Path(DONGLE_PATH).name == DONGLE_FILENAME
