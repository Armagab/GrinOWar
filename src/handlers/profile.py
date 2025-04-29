from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards.main_menu_keyboard import MainMenuButton
from utils.formatters import format_single_joke
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from database.user_queries import (
    get_user_subscription_status,
    set_user_active
)
from keyboards.main_menu_keyboard import main_menu_keyboard



async def my_stats(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Без имени"

    stats = await get_user_stats(user_id)

    if not stats["joke_text"] or not stats["prompt"]:
        await message.answer("😕 У вас пока нет отправленной шутки.")
        return

    stats_line = f"👍 Лайков: {stats['likes']}\n👁️‍🗨️ Просмотров: {stats['views']}"
    formatted = format_single_joke(stats["prompt"], stats["joke_text"], first_name, stats_line)

    await message.answer(formatted, parse_mode="Markdown")


async def toggle_notifications(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id

    subscribed = await get_user_subscription_status(user_id)
    if subscribed:
        await set_user_active(user_id, False)
        text = "🔕 Вы отписались от рассылки."
    else:
        await set_user_active(user_id, True)
        text = "🔔 Вы подписались на рассылку."

    kb = await main_menu_keyboard(user_id)
    await message.answer(text, reply_markup=kb)


async def show_rules_from_menu(message: types.Message, state: FSMContext):
    await state.finish()
    rules_text = (
        "📜 *Правила игры:*\n\n"
        "• Каждый день выбирается новый промпт — начало шутки.\n"
        "• Вы можете дописать свою шутку на его основе.\n"
        "• Затем начинается голосование за лучшие шутки.\n"
        "• В конце дня определяется ТОП 5!\n\n"
        "❗ Нельзя лайкать свои шутки.\n"
        "❗ Нельзя отправлять оскорбления или нецензурные тексты."
    )
    await message.answer(rules_text, parse_mode="Markdown")

from database.joke_queries import get_user_stats



def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(my_stats, text=MainMenuButton.STATS.value, state="*")
    dp.register_message_handler(show_rules_from_menu, text=MainMenuButton.RULES.value, state="*")
    dp.register_message_handler(toggle_notifications, text=MainMenuButton.UNSUBSCRIBE.value, state="*")
    dp.register_message_handler(toggle_notifications, text=MainMenuButton.SUBSCRIBE.value, state="*")