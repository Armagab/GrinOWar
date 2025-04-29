from aiogram import types

def generate_voting_keyboard(jokes_slice, voted_jokes, prompt_of_the_day, page: int, total_jokes: int, jokes_per_page: int):
    keyboard = types.InlineKeyboardMarkup(row_width=4)

    buttons = []
    for idx, (joke_id, username, first_name, joke_text) in enumerate(jokes_slice, start=1):
        emoji = "✅" if joke_id in voted_jokes else "👍"
        buttons.append(types.InlineKeyboardButton(f"{emoji}{idx}", callback_data=f"vote_{joke_id}"))
    keyboard.row(*buttons)

    nav = []
    nav.append(types.InlineKeyboardButton("🏁 Закончить голосование", callback_data="finish_voting"))
    if (page + 1) * jokes_per_page < total_jokes:
        nav.append(types.InlineKeyboardButton("➡️ Показать ещё", callback_data="page_next"))
    keyboard.row(*nav)

    return keyboard