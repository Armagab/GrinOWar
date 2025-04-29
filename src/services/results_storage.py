import os
import aiosqlite
from datetime import date
from services.prompt_manager import get_current_prompt
from database.joke_queries import DB_PATH



async def store_daily_winners(top5: list[dict]):
    prompt = get_current_prompt()
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