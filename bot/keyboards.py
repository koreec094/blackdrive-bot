from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def options_keyboard(options: list[str], row_width: int = 2) -> ReplyKeyboardMarkup:
    rows = []
    for i in range(0, len(options), row_width):
        rows.append([KeyboardButton(text=o) for o in options[i:i+row_width]])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
