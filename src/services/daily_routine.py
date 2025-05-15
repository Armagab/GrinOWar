import asyncio, logging
from services.scoring import calculate_daily_top_jokes
from services.prompt_manager import select_prompt_for_today
from database.prompt_queries import get_prompt_for_today
from services.results_storage import store_daily_winners
from utils.formatters import format_results, format_new_daily_prompt
from database.user_queries import get_active_user_ids, disable_inactive_users

logger = logging.getLogger(__name__)


async def run_daily_routine(bot):
    await disable_inactive_users(days_threshold=7)

    top5 = await calculate_daily_top_jokes()

    await store_daily_winners(top5)

    old_prompt = await get_prompt_for_today()
    await select_prompt_for_today(bot)
    new_prompt = await get_prompt_for_today()

    user_ids = await get_active_user_ids()

    formatted_top = [
        (j["id"], j["text"], j["author"], round(j["score"], 3))
        for j in top5
    ]
    top_text    = format_results(formatted_top, old_prompt)
    prompt_text = format_new_daily_prompt(new_prompt)

    async def send_to(uid):
        try:
            await bot.send_message(uid, top_text,    parse_mode="Markdown")
            await bot.send_message(uid, prompt_text, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"[Send Error] {uid}: {e}")

    await asyncio.gather(*(send_to(uid) for uid in user_ids))


