from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from services.prompt_manager import select_prompt_for_today
from database.prompt_queries import get_prompt_for_today
from services.daily_routine import run_daily_routine
from utils.formatters import format_admin_prompt_chosen
from utils.reply_lines import reply_admin_routine_start, reply_admin_routine_end, reply_admin_no_rights

ADMIN_ID = 811546015

async def force_prompt_command(message: types.Message, state: FSMContext):
    await state.finish()

    if message.from_user.id != ADMIN_ID:
        await message.answer(reply_admin_no_rights)
        return

    await select_prompt_for_today(message.bot)
    selected = await get_prompt_for_today()

    await message.answer(
        format_admin_prompt_chosen(selected),
        parse_mode="Markdown"
    )


async def force_routine_command(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id != ADMIN_ID:
        await message.answer(reply_admin_no_rights)
        return

    await message.answer(reply_admin_routine_start, parse_mode=None)
    await run_daily_routine(message.bot)
    await message.answer(reply_admin_routine_end, parse_mode=None)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(force_prompt_command, commands=["forceprompt"], state="*")
    dp.register_message_handler(force_routine_command, commands=["forceroutine"], state="*")