from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from states.bot_states import PromptStates

from keyboards.start_buttons import start_menu_keyboard, rules_keyboard
from keyboards.main_menu_keyboard import main_menu_keyboard
from services.prompt_manager import get_current_prompt
from utils.formatters import format_first_prompt_message
from database.user_queries import register_user_if_needed



async def start_command(message: types.Message):
    await register_user_if_needed(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    await message.answer(
        "👋 Привет!\n\n"
        "Я бот для тренировки юмора!\n\n"
        "Рекомендуем ознакомиться с правилами игры:",
        reply_markup=start_menu_keyboard()
    )


async def show_rules_callback(call: types.CallbackQuery):
    await call.answer()

    rules_text = (
        "📜 *Правила игры:*\n\n"
        "• Каждый день выбирается новый промпт — начало шутки.\n"
        "• Вы можете дописать свою шутку на его основе.\n"
        "• Затем начинается голосование за лучшие шутки.\n"
        "• В конце дня определяется ТОП 5!\n\n"
        "❗ Нельзя лайкать свои шутки.\n"
        "❗ Нельзя отправлять оскорбления или нецензурные тексты."
    )

    await call.message.edit_text(rules_text, reply_markup=rules_keyboard(), parse_mode="Markdown")


async def ready_to_start_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=None)

    prompt_text = get_current_prompt()
    formatted_message = format_first_prompt_message(prompt_text)

    kb = await main_menu_keyboard(call.from_user.id)
    await call.message.bot.send_message(
        call.message.chat.id,
        formatted_message,
        parse_mode="Markdown",
        reply_markup=kb
    )
    await state.set_state(PromptStates.waiting_for_joke)



def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=["start"], state="*")
    dp.register_callback_query_handler(show_rules_callback, lambda c: c.data == "show_rules", state="*")
    dp.register_callback_query_handler(ready_to_start_callback, lambda c: c.data == "ready_to_start", state="*")