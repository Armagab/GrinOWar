from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_replacement_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Да", callback_data="replace_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="replace_no")
    )
    return keyboard