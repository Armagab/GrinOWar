from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from database.user_queries import update_last_active

class LastActiveMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: Message, data: dict):
        user_id = message.from_user.id
        await update_last_active(user_id)