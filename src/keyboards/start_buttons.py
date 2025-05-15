from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



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


def retry_joke_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔁 Попробовать ещё раз", callback_data="retry_joke")
    )