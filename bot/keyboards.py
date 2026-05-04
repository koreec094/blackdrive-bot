from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def options_keyboard(options: list[str], prefix: str, row_width: int = 2) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(options), row_width):
        rows.append([InlineKeyboardButton(text=o, callback_data=f'{prefix}|{o}') for o in options[i:i+row_width]])
    return InlineKeyboardMarkup(inline_keyboard=rows)
