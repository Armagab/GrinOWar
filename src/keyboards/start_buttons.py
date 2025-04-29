from aiogram import types



def start_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("📜 Правила игры", callback_data="show_rules")
    )
    return keyboard


def rules_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Я готов начать", callback_data="ready_to_start")
    )
    return keyboard