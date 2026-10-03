from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_analysis_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура быстрых действий после анализа переписки."""
    buttons = [
        [
            InlineKeyboardButton(text="🔄 Ещё 3 варианта ответа", callback_data="action:more_options"),
            InlineKeyboardButton(text="☕ Как позвать на свидание", callback_data="action:invite_date")
        ],
        [
            InlineKeyboardButton(text="🧠 Психологический профиль (НЛП)", callback_data="action:psychology")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
