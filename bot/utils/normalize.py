import re


def normalize_text(value: str) -> str:
    return re.sub(r'\s+', ' ', (value or '').strip()).casefold()


def normalize_engine(value: str) -> str:
    return re.sub(r'\D', '', str(value or ''))
