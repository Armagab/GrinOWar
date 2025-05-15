from math import log10
from database.joke_queries import get_jokes_for_scoring
from database.prompt_queries import get_prompt_for_today

async def calculate_daily_top_jokes():
    prompt = await get_prompt_for_today()
    jokes = await get_jokes_for_scoring(prompt)

    for joke in jokes:
        joke["score"] = log10(1 + joke["likes"]) * (joke["likes"] / joke["views"])

    return sorted(jokes, key=lambda x: x["score"], reverse=True)[:5]