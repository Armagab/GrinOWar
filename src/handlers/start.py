from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from states.bot_states import PromptStates

from keyboards.start_buttons import start_menu_keyboard, rules_keyboard
from keyboards.main_menu_keyboard import main_menu_keyboard
from database.prompt_queries import get_prompt_for_today
from utils.formatters import format_first_prompt_message
from utils.reply_lines import reply_start, reply_game_rules
from database.user_queries import register_user_if_needed



async def start_command(message: types.Message):
    await register_user_if_needed(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    await message.answer(
        reply_start,
        reply_markup=start_menu_keyboard()
    )


async def show_rules_callback(call: types.CallbackQuery):
    await call.answer()

    await call.message.edit_text(reply_game_rules, reply_markup=rules_keyboard(), parse_mode="Markdown")


async def ready_to_start_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=None)

    prompt_text = await get_prompt_for_today()
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