from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards.main_menu_keyboard import MainMenuButton
from utils.formatters import format_single_joke, format_user_stats_line, format_results
from utils.reply_lines import reply_game_rules, reply_no_joke_for_stats, reply_notifications_unsub, reply_notifications_sub, reply_no_winners_info
from database.user_queries import (
    get_user_subscription_status,
    set_user_active
)
from keyboards.main_menu_keyboard import main_menu_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.joke_queries import get_user_stats, get_winners



def stats_inline_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📜 Правила игры", callback_data="show_rules_inline"))
    return kb

async def my_stats(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Без имени"

    stats = await get_user_stats(user_id)

    if not stats["joke_text"] or not stats["prompt"]:
        await message.answer(reply_no_joke_for_stats, reply_markup=stats_inline_keyboard())
        return

    stats_line = format_user_stats_line(stats["likes"], stats["views"])
    formatted = format_single_joke(stats["prompt"], stats["joke_text"], first_name, stats_line)

    await message.answer(formatted, parse_mode="Markdown", reply_markup=stats_inline_keyboard())


async def toggle_notifications(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id

    subscribed = await get_user_subscription_status(user_id)
    if subscribed:
        await set_user_active(user_id, False)
        text = reply_notifications_unsub
    else:
        await set_user_active(user_id, True)
        text = reply_notifications_sub

    kb = await main_menu_keyboard(user_id)
    await message.answer(text, reply_markup=kb)

async def show_rules_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(reply_game_rules, parse_mode="Markdown")


async def show_top(message: types.Message, state: FSMContext):
    await state.finish()
    winners = await get_winners()

    if not winners:
        await message.answer(reply_no_winners_info)
        return

    prompt = winners[0]["prompt"]
    data = [
        (w["id"], w["text"], w["author"], round(w["score"], 3))
        for w in winners
    ]
    text = format_results(data, prompt)
    await message.answer(text, parse_mode="Markdown")



def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(my_stats, text=MainMenuButton.STATS.value, state="*")
    dp.register_message_handler(toggle_notifications, text=MainMenuButton.UNSUBSCRIBE.value, state="*")
    dp.register_message_handler(toggle_notifications, text=MainMenuButton.SUBSCRIBE.value, state="*")
    dp.register_callback_query_handler(show_rules_callback, lambda c: c.data == "show_rules_inline", state="*")
    dp.register_message_handler(show_top, text=MainMenuButton.SHOW_YESTERDAY_WINNERS.value, state="*")

