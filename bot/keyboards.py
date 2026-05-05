from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def options_keyboard(options: list[str], prefix: str, row_width: int = 2, with_back: bool = False, back_callback: str = 'nav|back') -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(options), row_width):
        rows.append([InlineKeyboardButton(text=o, callback_data=f'{prefix}|{o}') for o in options[i:i + row_width]])
    if with_back:
        rows.append([InlineKeyboardButton(text='⬅️ Назад', callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def start_menu_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🚗 Рассчитать авто до Алматы', callback_data='menu|calculate')],
            [InlineKeyboardButton(text='👨‍💼 Связаться с менеджером', callback_data='menu|manager')],
            [InlineKeyboardButton(text='📢 Наш канал', url=channel_url)],
        ]
    )


def subscribe_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📢 Подписаться на канал', url=channel_url)],
            [InlineKeyboardButton(text='✅ Проверить подписку', callback_data='menu|check_subscription')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='menu|back_to_start')],
        ]
    )


def final_result_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👨‍💼 Связаться с менеджером', callback_data='final|manager')],
            [InlineKeyboardButton(text='🔄 Рассчитать еще один автомобиль', callback_data='final|recalculate')],
        ]
    )
