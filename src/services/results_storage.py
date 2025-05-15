import os
import aiosqlite
from datetime import date
from database.prompt_queries import get_prompt_for_today
from database.joke_queries import DB_PATH



async def store_daily_winners(top5: list[dict]):
    prompt = await get_prompt_for_today()
    today = date.today().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute('''
            CREATE TABLE IF NOT EXISTS todays_winners (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT    NOT NULL,
                joke_id     INTEGER NOT NULL,
                prompt      TEXT,
                joke_text   TEXT,
                first_name  TEXT,
                likes       INTEGER,
                views       INTEGER,
                score       REAL
            )
        ''')

        await db.execute('DELETE FROM todays_winners')

        for w in top5:
            await db.execute('''
                INSERT INTO todays_winners
                  (date, joke_id, prompt, joke_text, first_name, likes, views, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                w['id'],
                prompt,
                w['text'],
                w['author'],
                w['likes'],
                w['views'],
                w['score'],
            ))
        await db.commit()