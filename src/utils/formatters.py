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
    text = "Шутки для голосования: "
    for idx, (joke_id, username, first_name, joke_text) in enumerate(jokes_slice, start=1):
        name_display = first_name if first_name else "Без имени"
        text += (
            f"{idx}. {prompt} `{joke_text}`\n"
            f"👤 {name_display}\n\n"
        )
    return text


def format_results(top_jokes: list, prompt: str) -> str:
    if not top_jokes:
        return "😕 Пока нет шуток с голосами."

    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 *Топ шуток дня:*\n\n"

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
        f"🌟 *Новый промпт дня:*\n\n"
        f"`{prompt.strip()}`\n\n"
        f"✏️ Напиши свою шутку!"
    )


def format_requested_daily_prompt(prompt: str) -> str:
    return (
        f"🌟 *Промпт дня:*\n\n"
        f"`{prompt.strip()}`\n\n"
        f"✏️ Напиши своё продолжение!"
    )


def format_first_prompt_message(prompt: str) -> str:
    return (
        "🚀 *Добро пожаловать в игру!*\n\n"
        "Каждый день мы выбираем начало шутки — *Промпт дня*.\n"
        "Ваша задача — придумать забавное продолжение!\n\n"
        "Вот сегодняшний промпт:\n\n"
        f"`{prompt.strip()}`\n\n"
        "✏️ Отправьте своё продолжение шутки прямо сейчас!"
    )


def format_requested_suggest_prompt() -> str:
    return "✏️ Введите заготовку (начало шутки), которую хотите предложить:"


def format_game_rules() -> str:
    return (
        "📜 *Правила игры:*\n\n"
        "• Каждый день выбирается новый промпт — начало шутки.\n"
        "• Вы можете дописать свою шутку на его основе.\n"
        "• Затем начинается голосование за лучшие шутки.\n"
        "• В конце дня определяется ТОП 5!\n\n"
        "❗ Нельзя лайкать свои шутки.\n"
        "❗ Нельзя отправлять оскорбления или нецензурные тексты."
    )


def format_user_stats() -> str:
    return "📈 Здесь будет ваша статистика (в разработке)."