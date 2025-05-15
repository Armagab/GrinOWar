CENSORSHIP_PROMPT = (
    "Ты модератор шуток. "
    "Твоя задача — отклонять текст только если он содержит: "
    "маты и оскорбления (грубые, враждебные), темы реального насилия, смерти, убийств, самоубийства, "
    "грязные темы типа экскрементов, крови, расчленения, "
    "явные сексуальные извращения, особенно с участием животных или детей, "
    "расизм, политическую агрессию, пропаганду вражды, "
    "чёрный юмор на темы смерти, крови, пыток. "
    "Мягкие или ласковые обращения, фразы про дружбу, любовь, милые шутки — разрешены. "
    "Сарказм и ирония — разрешены. "
    "Если текст полностью безопасен, ответь только 'safe'. "
    "Если текст нарушает правила, ответь только 'unsafe'. "
    "Отвечай только 'safe' или 'unsafe', без объяснений."
)
MEANINGFULNESS_PROMPT = (
    "Ты помощник-модератор. "
    "Твоя задача — проверять, является ли фраза осмысленным началом шутки.\n\n"
    "Если пользователь предложил связное, логичное и понятное начало — ответь 'valid'.\n"
    "Если фраза абсурдная, бессмысленная, набор букв или не имеет структуры — ответь 'invalid'.\n\n"
    "Примеры valid:\n"
    "• Когда ежик пошёл в магазин,\n"
    "• Вчера на работе случилось\n"
    "Примеры invalid:\n"
    "• йцукен\n"
    "• 1234\n"
    "• кот\n"
    "• ха ха ха ха\n\n"
    "Отвечай ТОЛЬКО 'valid' или 'invalid'. Без пояснений."
)


import asyncio
import os
import openai

from dotenv import load_dotenv
load_dotenv()


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def is_safe_text(text: str) -> bool:
    try:
        response = client.moderations.create(input=text)
        results = response.results[0]

        return not results.flagged

    except openai.APIError as e:
        print(f"[OpenAI API Error] {e}")
        return False
    except Exception as e:
        print(f"[Unexpected Error] {e}")
        return False


async def is_safe_combined_text(prompt: str, joke_text: str) -> bool:
    try:
        combined_text = f"{prompt} {joke_text}"

        response = client.moderations.create(input=combined_text)
        results = response.results[0]

        return not results.flagged

    except openai.APIError as e:
        print(f"[OpenAI API Error] {e}")
        return False
    except Exception as e:
        print(f"[Unexpected Error] {e}")
        return False


async def is_safe_with_gpt(prompt: str, joke_text: str, timeout_sec: int = 8) -> bool:
    combined_text = f"{prompt} {joke_text}"

    try:
        def sync_call():
            return client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": CENSORSHIP_PROMPT},
                    {"role": "user", "content": f"Текст для проверки: {combined_text}"}
                ],
                temperature=0,
                max_tokens=1,
            )

        response = await asyncio.wait_for(
            asyncio.to_thread(sync_call),
            timeout=timeout_sec
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer == "safe"

    except asyncio.TimeoutError:
        print("[Moderation Timeout] GPT ответ не получен вовремя.")
        return False

    except openai.APIError as e:
        print(f"[OpenAI API Error] {e}")
        return False

    except Exception as e:
        print(f"[Moderation Unexpected Error] {e}")
        return False


async def is_meaningful_prompt_with_gpt(prompt_text: str, timeout_sec: int = 6) -> bool:

    try:
        def sync_call():
            return client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": MEANINGFULNESS_PROMPT},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=0,
                max_tokens=1,
            )

        response = await asyncio.wait_for(
            asyncio.to_thread(sync_call),
            timeout=timeout_sec
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer == "valid"

    except Exception as e:
        print(f"[Meaningful Check Error] {e}")
        return False