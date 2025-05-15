import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from services.daily_routine import run_daily_routine



def init_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
    trigger = CronTrigger(hour=12, minute=0)

    scheduler.add_job(
        lambda: asyncio.create_task(run_daily_routine(bot)),
        trigger,
        id="daily_routine",
        replace_existing=True
    )

    scheduler.start()



