from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from services.prompt_manager import select_prompt_for_today, get_current_prompt
from services.daily_routine import run_daily_routine
from config import ADMIN_ID

async def force_prompt_command(message: types.Message, state: FSMContext):
    await state.finish()

    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет прав на эту команду.")
        return

    await select_prompt_for_today(message.bot)
    selected = get_current_prompt()

    await message.answer(
        f"✅ Заготовка на сегодня была выбрана:\n\n`{selected}`",
        parse_mode="Markdown"
    )


async def force_routine_command(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет прав на эту команду.")
        return

    await message.answer("🕐 Запускаю ежедневную рутину...", parse_mode=None)
    await run_daily_routine(message.bot)
    await message.answer("✅ Ежедневная рутина успешно выполнена.", parse_mode=None)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(force_prompt_command, commands=["forceprompt"], state="*")
    dp.register_message_handler(force_routine_command, commands=["forceroutine"], state="*")