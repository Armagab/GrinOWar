import asyncio
import os

from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from aiogram import Bot

from database import prompt_queries, joke_queries
from database.prompt_queries import get_random_prompt


DEFAULT_PROMPT = "Когда кот впервые пошел работать в офис,"  # дефолтный промпт fallback

_current_prompt = DEFAULT_PROMPT


async def generate_prompt_with_gpt() -> str:
    system_prompt = (
        "Ты креативный сценарист шуток. "
        "Каждый раз придумывай новое, оригинальное, забавное начало шутки одним коротким предложением. "
        "Это нужно для того, чтобы я и мои друзья сами придумали разные смешные продолжения шутки. "
        "Не придумывай окончание. Только начало. "
    )

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = await asyncio.to_thread(lambda: client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                ChatCompletionUserMessageParam(role="user", content="Придумай начало шутки.")
            ],
            temperature=1.1,
            max_tokens=50,
        ))

        prompt_text = response.choices[0].message.content.strip()
        return prompt_text

    except Exception as e:
        print(f"[GPT Error] {e}")
        return DEFAULT_PROMPT


async def try_select_prompt_from_db() -> str | None:
    prompt_row = await get_random_prompt()
    if prompt_row:
        _, prompt_text = prompt_row
        await prompt_queries.clear_prompts()
        return prompt_text
    return None


async def clear_old_jokes():
    await joke_queries.clear_jokes()
    await joke_queries.clear_votes_and_views()


async def update_current_prompt(new_prompt: str):
    global _current_prompt
    _current_prompt = new_prompt


async def select_prompt_for_today(bot: Bot):
    prompt_text = await try_select_prompt_from_db()

    if prompt_text is None:
        prompt_text = await generate_prompt_with_gpt()

    await update_current_prompt(prompt_text)

    await clear_old_jokes()


def get_current_prompt() -> str:
    return _current_prompt