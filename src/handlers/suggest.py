from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from states.bot_states import SuggestPromptStates
from database.prompt_queries import insert_prompt, get_user_prompt, update_prompt
from utils.validators import is_valid_text_length
from utils.reply_lines import (reply_prompt_saved, reply_prompt_too_long, reply_checking,
                               reply_moderation_error, reply_censorship_failed, reply_prompt_updated, reply_meaningfulness_failed)
from utils.reply_lines import reply_suggest_prompt
from utils.moderation import is_safe_with_gpt
from keyboards.main_menu_keyboard import MainMenuButton
from keyboards.start_buttons import retry_joke_keyboard
from utils.moderation import is_meaningful_prompt_with_gpt



async def suggest_prompt_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(reply_suggest_prompt)
    await state.set_state(SuggestPromptStates.waiting_for_prompt)


async def prompt_received(message: types.Message, state: FSMContext):

    if message.text == MainMenuButton.SUGGEST.value:
        await message.answer(reply_suggest_prompt)
        return

    prompt_text = message.text.strip()

    if not is_valid_text_length(prompt_text):
        await message.answer(reply_prompt_too_long)
        return

    checking_message = await message.answer(reply_checking)

    try:
        is_safe = await is_safe_with_gpt("", prompt_text)
    except Exception as e:
        print(f"[Moderation Check Error] {e}")
        await checking_message.edit_text(reply_moderation_error)
        await state.finish()
        return

    if not is_safe:
        await checking_message.edit_text(
            reply_censorship_failed,
            reply_markup=retry_joke_keyboard()
        )
        await state.set_state(SuggestPromptStates.waiting_for_prompt)
        return
    try:
        is_meaningful = await is_meaningful_prompt_with_gpt(prompt_text)
    except Exception as e:
        print(f"[Meaningful Prompt Check Error] {e}")
        await checking_message.edit_text(reply_moderation_error)
        await state.finish()
        return

    if not is_meaningful:
        await checking_message.edit_text(
            reply_meaningfulness_failed,
            reply_markup=retry_joke_keyboard()
        )
        await state.set_state(SuggestPromptStates.waiting_for_prompt)
        return

    user_id = message.from_user.id
    username = message.from_user.username or None
    first_name = message.from_user.first_name or "Без имени"

    existing_prompt = await get_user_prompt(user_id)

    if existing_prompt:
        prompt_id = existing_prompt[0]
        await update_prompt(prompt_id, prompt_text)
        await checking_message.edit_text(reply_prompt_updated)
    else:
        await insert_prompt(user_id, username, first_name, prompt_text)
        await checking_message.edit_text(reply_prompt_saved)
    await state.finish()


async def retry_prompt_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    await call.message.edit_text(reply_suggest_prompt)
    await state.set_state(SuggestPromptStates.waiting_for_prompt)


def register_suggest_handlers(dp: Dispatcher):
    dp.register_message_handler(prompt_received, state=SuggestPromptStates.waiting_for_prompt)
    dp.register_message_handler(suggest_prompt_start, text=MainMenuButton.SUGGEST.value, state="*")
    dp.register_callback_query_handler(retry_prompt_callback, lambda c: c.data == "retry_joke", state=SuggestPromptStates.waiting_for_prompt)