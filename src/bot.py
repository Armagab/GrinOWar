from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import register_all_handlers
from middlewares.last_active import LastActiveMiddleware

from services.scheduler import init_scheduler


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LastActiveMiddleware())
register_all_handlers(dp)


async def on_startup(dispatcher):
    init_scheduler(bot)


if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )


