"""Input checks (SRS: upload validation). Every function returns (ok, message)."""
from __future__ import annotations
from PIL import Image, UnidentifiedImageError

ALLOWED_EXT = {"jpg", "jpeg", "png"}
MAX_MB = 10
MIN_SIDE = 64          # pixels; smaller than this is useless for the model
WEIGHT_MIN, WEIGHT_MAX = 0.1, 500.0   # kg


def validate_image(file) -> tuple[bool, str]:
    """`file` is a Streamlit UploadedFile (has .name, .size, file-like)."""
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if ext not in ALLOWED_EXT:
        return False, "Sirf JPG ya PNG image chalegi."
    if file.size > MAX_MB * 1024 * 1024:
        return False, f"Image {MAX_MB} MB se chhoti honi chahiye."
    try:
        file.seek(0)
        img = Image.open(file)
        img.verify()                      # catches corrupted / fake files
        file.seek(0)
        img = Image.open(file)
    except (UnidentifiedImageError, OSError):
        return False, "Ye valid image nahi hai ya file kharab hai."
    if min(img.size) < MIN_SIDE:
        return False, f"Image bahut chhoti hai (kam se kam {MIN_SIDE}px chahiye)."
    file.seek(0)
    return True, "ok"


def validate_weight(value) -> tuple[bool, str]:
    try:
        w = float(value)
    except (TypeError, ValueError):
        return False, "Weight number hona chahiye."
    if not (WEIGHT_MIN <= w <= WEIGHT_MAX):
        return False, f"Weight {WEIGHT_MIN} se {WEIGHT_MAX} kg ke beech hona chahiye."
    return True, "ok"
