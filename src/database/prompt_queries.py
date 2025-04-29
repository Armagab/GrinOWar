import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

async def insert_prompt(user_id: int, username: str, first_name: str, prompt_text: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            INSERT INTO prompts (user_id, username, first_name, prompt_text)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, prompt_text))
        await conn.commit()

async def get_random_prompt():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT id, prompt_text FROM prompts
            ORDER BY RANDOM()
            LIMIT 1
        ''')
        result = await cursor.fetchone()
        await cursor.close()
    return result

async def clear_prompts():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('DELETE FROM prompts')
        await conn.commit()

async def get_user_prompt(user_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT id, prompt_text
            FROM prompts
            WHERE user_id = ?
            LIMIT 1
        ''', (user_id,))
        result = await cursor.fetchone()
        await cursor.close()
    return result  # None или (id, prompt_text)

async def update_prompt(prompt_id: int, prompt_text: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            UPDATE prompts
            SET prompt_text = ?
            WHERE id = ?
        ''', (prompt_text, prompt_id))
        await conn.commit()