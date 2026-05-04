import re


def normalize_text(value: str) -> str:
    return re.sub(r'\s+', ' ', (value or '').strip()).casefold()


def normalize_engine(value: str) -> str:
    raw = str(value or '').strip()
    digits = re.sub(r'\D', '', raw)
    if digits:
        return digits
    return normalize_text(raw)
