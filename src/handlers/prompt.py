from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from keyboards.confirm_replace import confirm_replacement_keyboard
from services.prompt_manager import get_current_prompt
from utils.formatters import format_requested_daily_prompt
from states.bot_states import PromptStates
from database.joke_queries import get_user_joke, insert_joke, update_joke
from utils.validators import is_valid_text_length
from utils.formatters import format_single_joke
from utils.moderation import is_safe_with_gpt
from utils.reply_lines import (
    reply_checking,
    reply_censorship_failed,
    reply_joke_too_long,
    reply_moderation_error, reply_confirm_replacement
)
from keyboards.main_menu_keyboard import MainMenuButton
from .suggest import suggest_prompt_start



async def prompt_show(message: types.Message, state: FSMContext):
    await state.finish()
    prompt_text = get_current_prompt()
    await message.answer(format_requested_daily_prompt(prompt_text), parse_mode="Markdown")
    await state.set_state(PromptStates.waiting_for_joke)


async def joke_receive(message: types.Message, state: FSMContext):

    if message.text == MainMenuButton.SUGGEST.value:
        await state.finish()
        await suggest_prompt_start(message, state)  # вызов обработчика вручную
        return
    elif message.text == MainMenuButton.CONTINUE_JOKE.value:
        prompt_text = get_current_prompt()
        await message.answer(format_requested_daily_prompt(prompt_text), parse_mode="Markdown")
        return

    user_id = message.from_user.id
    username = message.from_user.username or None
    first_name = message.from_user.first_name or "Без имени"
    joke_text = message.text.strip()
    prompt_text = get_current_prompt()

    if not is_valid_text_length(joke_text):
        await message.answer(reply_joke_too_long)
        return

    checking_message = await message.answer(reply_checking)

    try:
        is_safe = await is_safe_with_gpt(prompt_text, joke_text)
    except Exception as e:
        print(f"[Moderation Check Error] {e}")
        await checking_message.edit_text(reply_moderation_error)
        await state.finish()
        return

    if not is_safe:
        await checking_message.edit_text(reply_censorship_failed)
        await state.finish()
        return

    existing_joke = await get_user_joke(user_id, prompt_text)

    if existing_joke:
        await state.update_data(
            new_joke_text=joke_text,
            old_joke_id=existing_joke[0],
            checking_message_id=checking_message.message_id
        )
        await checking_message.edit_text(
            reply_confirm_replacement,
            reply_markup=confirm_replacement_keyboard()
        )
        await state.set_state(PromptStates.confirm_replacement)
        return

    await insert_joke(user_id, username, first_name, prompt_text, joke_text)
    status_text = "✅ Спасибо! Шутка добавлена."
    formatted = format_single_joke(prompt_text, joke_text, first_name, status_text)
    await checking_message.edit_text(formatted, parse_mode="Markdown")
    await state.finish()


async def handle_replace_confirmation(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    joke_id = data.get("old_joke_id")
    new_text = data.get("new_joke_text")
    message_id = data.get("checking_message_id")
    prompt_text = get_current_prompt()
    first_name = call.from_user.first_name or "Без имени"

    if call.data == "replace_no":
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=message_id,
            text="❌ Отмена. Твоя шутка осталась прежней."
        )
        await state.finish()
        return

    if call.data == "replace_yes":
        await update_joke(joke_id, new_text, reset_stats=True)

        first_name = call.from_user.first_name or "Без имени"
        formatted = format_single_joke(
            prompt_text,
            new_text,
            first_name,
            "✅ Шутка обновлена! Лайки и просмотры сброшены."
        )

        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=message_id,
            text=formatted,
            parse_mode="Markdown"
        )
        await state.finish()



def register_prompt_handlers(dp: Dispatcher):
    dp.register_message_handler(joke_receive, state=PromptStates.waiting_for_joke)
    dp.register_message_handler(prompt_show, text=MainMenuButton.CONTINUE_JOKE.value, state="*")
    dp.register_callback_query_handler(handle_replace_confirmation, lambda c: c.data in ["replace_yes", "replace_no"],
                                       state=PromptStates.confirm_replacement)
