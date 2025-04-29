import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')


async def register_user_if_needed(user_id: int, username: str | None, first_name: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        exists = await cursor.fetchone()
        await cursor.close()

        if not exists:
            await db.execute('''
                INSERT INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            await db.commit()

from datetime import datetime


async def update_last_active(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users
            SET last_active = ?
            WHERE user_id = ?
        ''', (datetime.utcnow(), user_id))
        await db.commit()


async def disable_inactive_users(days_threshold: int = 7):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'''
            UPDATE users
            SET paused_due_to_inactivity = 1
            WHERE last_active IS NOT NULL
              AND julianday('now') - julianday(last_active) > ?
        ''', (days_threshold,))
        await db.commit()


async def get_active_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT user_id FROM users
            WHERE is_active = 1 AND paused_due_to_inactivity = 0
        ''')
        users = await cursor.fetchall()
        await cursor.close()
    return [row[0] for row in users]


async def get_user_subscription_status(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT is_active FROM users WHERE user_id = ?',
            (user_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
    return bool(row and row[0])


async def set_user_active(user_id: int, active: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users
            SET is_active = ?, paused_due_to_inactivity = 0
            WHERE user_id = ?
        ''', (1 if active else 0, user_id))
        await db.commit()