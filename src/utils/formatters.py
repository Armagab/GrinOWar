def format_single_joke(prompt: str, joke_text: str, first_name: str, status_text: str = None) -> str:
    name_display = first_name if first_name else "Без имени"
    result = (
        f"{prompt} `{joke_text}`\n"
        f"👤 Автор: {name_display}"
    )
    if status_text:
        result += f"\n\n{status_text}"
    return result


def format_jokes_page(jokes_slice, prompt: str, current_page: int, total_pages: int):
    text = "Проголосуйте за шутки других игроков: \n\n"
    for idx, (joke_id, username, first_name, joke_text) in enumerate(jokes_slice, start=1):
        name_display = first_name if first_name else "Без имени"
        text += (
            f"{idx}. {prompt} `{joke_text}`\n"
            f"👤 {name_display}\n\n"
        )
    return text


def format_results(top_jokes: list, prompt: str) -> str:
    if not top_jokes:
        return "😕 Пока нет шуток с голосами (нечего отображать)."

    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 *Топ шуток прошедшего дня:*\n\n"

    for idx, (joke_id, joke_text, first_name, votes_count) in enumerate(top_jokes):
        if idx < len(medals):
            prefix = medals[idx]
        else:
            prefix = f"{idx+1}."

        name_display = first_name or "Без имени"
        text += (
            f"{prefix} {prompt} `{joke_text}`\n"
            f"👤 Автор: {name_display}\n"
            f"👍 Рейтинг: {votes_count}\n\n"
        )

    return text


def format_new_daily_prompt(prompt: str) -> str:
    return (
        f"🌟 *Новая заготовка дня:*\n\n"
        f"`{prompt.strip()}`\n\n"
        f"✏️ Придумайте своё продолжение!"
    )


def format_requested_daily_prompt(prompt: str) -> str:
    return (
        f"🌟 *Заготовка дня:*\n\n"
        f"`{prompt.strip()}`\n\n"
        f"✏️ Придумайте своё продолжение!"
    )


def format_first_prompt_message(prompt: str) -> str:
    return (
        "🚀 *Добро пожаловать в игру!*\n\n"
        "Каждый день мы выбираем начало шутки — *Заготовку*.\n"
        "Ваша задача — придумать смешное продолжение!\n\n"
        "Вот заготовка на сегодня:\n\n"
        f"`{prompt.strip()}`\n\n"
        "✏️ Придумайте и отправьте своё продолжение шутки прямо сейчас!"
    )


def format_admin_prompt_chosen(prompt: str) -> str:
    return (
        f"✅ Заготовка на сегодня была выбрана:\n\n`{prompt.strip()}`"
    )


def format_user_stats_line(likes, views):
    return (
        f"👍 Лайков: {likes}\n👁️‍🗨️ Просмотров: {views}"
    )
