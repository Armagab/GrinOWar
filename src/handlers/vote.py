from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from services.prompt_manager import get_current_prompt
from database.joke_queries import get_jokes_for_voting, add_vote, get_user_votes, remove_vote, register_views
from states.bot_states import VoteStates

from keyboards.voting_buttons import generate_voting_keyboard
from utils.formatters import format_jokes_page

from config import JOKES_PER_PAGE



async def vote_command(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    prompt_text = get_current_prompt()

    jokes = await get_jokes_for_voting(user_id, prompt_text, limit=50)
    voted_jokes = await get_user_votes(user_id)

    await state.update_data(jokes=jokes, page=0, voted_jokes=voted_jokes)
    await state.set_state(VoteStates.showing_page)

    await send_jokes_page(message.chat.id, message.bot, state)


async def send_jokes_page(chat_id, bot, state: FSMContext, message_id=None, do_register_views=True):
    data = await state.get_data()
    jokes = data.get('jokes', [])
    page = data.get('page', 0)
    voted_jokes = data.get('voted_jokes', set())
    prompt_text = get_current_prompt()

    start = page * JOKES_PER_PAGE
    end = start + JOKES_PER_PAGE
    jokes_slice = jokes[start:end]

    if not jokes or not jokes_slice:
        await bot.send_message(
            chat_id,
            "😕 Пока нет доступных шуток для голосования.\n(Или вы уже посмотрели все доступные шутки)"
        )
        await state.finish()
        return

    if do_register_views:
        joke_ids = [row[0] for row in jokes_slice]
        await register_views(chat_id, joke_ids)

    total_pages = (len(jokes) + JOKES_PER_PAGE - 1) // JOKES_PER_PAGE

    text = format_jokes_page(
        jokes_slice,
        prompt_text,
        current_page=page + 1,
        total_pages=total_pages
    )

    keyboard = generate_voting_keyboard(
        jokes_slice,
        voted_jokes,
        prompt_text,
        page,
        total_jokes=len(jokes),
        jokes_per_page=JOKES_PER_PAGE
    )

    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await bot.send_message(
            chat_id,
            text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )


async def pagination_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get('page', 0)
    jokes = data.get('jokes', [])

    if call.data == "page_next":
        if (page + 1) * JOKES_PER_PAGE < len(jokes):
            page += 1
            await state.update_data(page=page)
            await send_jokes_page(call.message.chat.id, call.bot, state, call.message.message_id)
        else:
            await call.answer("✅ Вы просмотрели все шутки!", show_alert=True)

    elif call.data == "finish_voting":
        await call.message.edit_reply_markup()
        await call.message.answer("✅ Спасибо за участие в голосовании!")
        await state.finish()


async def vote_callback(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = call.data

    if not data.startswith("vote_"):
        return

    joke_id = int(data.split("_")[1])
    state_data = await state.get_data()
    voted_jokes = state_data.get('voted_jokes', set())

    if joke_id in voted_jokes:
        await remove_vote(user_id, joke_id)
        voted_jokes.discard(joke_id)
        await state.update_data(voted_jokes=voted_jokes)

        await send_jokes_page(call.message.chat.id, call.bot, state, call.message.message_id, do_register_views=False)
        await call.answer("🔙 Голос отменён", show_alert=False)

    else:
        await add_vote(user_id, joke_id)
        voted_jokes.add(joke_id)
        await state.update_data(voted_jokes=voted_jokes)

        await send_jokes_page(call.message.chat.id, call.bot, state, call.message.message_id, do_register_views=False)
        await call.answer("✅ Голос учтён!", show_alert=False)



def register_vote_handlers(dp: Dispatcher):
    dp.register_message_handler(vote_command, text="🎭 Голосовать за шутки", state="*")
    dp.register_callback_query_handler(pagination_callback, lambda c: c.data in ["page_next", "finish_voting"], state=VoteStates.showing_page)
    dp.register_callback_query_handler(vote_callback, lambda c: c.data and c.data.startswith("vote_"), state=VoteStates.showing_page)