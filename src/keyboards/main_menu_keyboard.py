from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from enum import Enum
from database.user_queries import get_user_subscription_status



class MainMenuButton(str, Enum):
    CONTINUE_JOKE          = "📝 Продолжить шутку"
    VOTE                   = "🎭 Голосовать за шутки"
    SUGGEST                = "💡 Предложить заготовку"
    STATS                  = "📈 Моя статистика"
    SHOW_YESTERDAY_WINNERS = "🏆 Топ 5 прошедшего дня"
    UNSUBSCRIBE            = "🔕 Отказаться от рассылки"
    SUBSCRIBE              = "🔔 Включить рассылку"


async def main_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    subscribed = await get_user_subscription_status(user_id)

    kb = [
        [
            KeyboardButton(MainMenuButton.CONTINUE_JOKE.value),
            KeyboardButton(MainMenuButton.VOTE.value),
        ],
        [
            KeyboardButton(MainMenuButton.SUGGEST.value),
            KeyboardButton(MainMenuButton.STATS.value),
        ],
    ]

    bottom = [KeyboardButton(MainMenuButton.SHOW_YESTERDAY_WINNERS.value)]
    if subscribed:
        bottom.append(KeyboardButton(MainMenuButton.UNSUBSCRIBE.value))
    else:
        bottom.append(KeyboardButton(MainMenuButton.SUBSCRIBE.value))

    kb.append(bottom)
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)