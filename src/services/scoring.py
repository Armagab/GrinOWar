from math import log10
from database.joke_queries import get_jokes_for_scoring
from services.prompt_manager import get_current_prompt

async def calculate_daily_top_jokes():
    prompt = get_current_prompt()
    jokes = await get_jokes_for_scoring(prompt)

    for joke in jokes:
        joke["score"] = log10(1 + joke["likes"]) * (joke["likes"] / joke["views"])

    return sorted(jokes, key=lambda x: x["score"], reverse=True)[:5]