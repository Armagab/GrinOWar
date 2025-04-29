import aiosqlite
import os
from config import VOTE_RANDOMNESS

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')



async def get_user_joke(user_id: int, prompt: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT id FROM jokes
            WHERE user_id = ? AND prompt = ? AND is_active = 1
        ''', (user_id, prompt))
        result = await cursor.fetchone()
        await cursor.close()
    return result


async def insert_joke(user_id: int, username: str, first_name: str, prompt: str, joke_text: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            INSERT INTO jokes (user_id, username, first_name, prompt, joke_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, prompt, joke_text))
        await conn.commit()


async def update_joke(joke_id: int, joke_text: str, reset_stats: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if reset_stats:
            await db.execute('''
                UPDATE jokes
                SET joke_text = ?, likes = 0, views = 0
                WHERE id = ?
            ''', (joke_text, joke_id))
        else:
            await db.execute('''
                UPDATE jokes
                SET joke_text = ?
                WHERE id = ?
            ''', (joke_text, joke_id))
        await db.commit()


async def get_jokes_for_voting(user_id: int, prompt: str, limit: int = 5):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(f'''
            SELECT id, username, first_name, joke_text
            FROM jokes
            WHERE user_id != ?
              AND prompt = ?
              AND id NOT IN (
                  SELECT joke_id FROM views WHERE viewer_user_id = ?
              )
              AND is_active = 1
            ORDER BY (views + RANDOM() * ?) ASC
            LIMIT ?
        ''', (user_id, prompt, user_id, VOTE_RANDOMNESS, limit))
        jokes = await cursor.fetchall()
        await cursor.close()
    return jokes


async def add_vote(user_id: int, joke_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            INSERT INTO votes (voter_user_id, joke_id)
            VALUES (?, ?)
        ''', (user_id, joke_id))
        await conn.execute('''
            UPDATE jokes
            SET likes = likes + 1
            WHERE id = ?
        ''', (joke_id,))
        await conn.commit()


async def remove_vote(user_id: int, joke_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            DELETE FROM votes
            WHERE voter_user_id = ? AND joke_id = ?
        ''', (user_id, joke_id))
        await conn.execute('''
            UPDATE jokes
            SET likes = CASE WHEN likes > 0 THEN likes - 1 ELSE 0 END
            WHERE id = ?
        ''', (joke_id,))
        await conn.commit()


async def register_views(user_id: int, joke_ids: list[int]):
    if not joke_ids:
        return
    async with aiosqlite.connect(DB_PATH) as conn:
        for joke_id in joke_ids:
            await conn.execute('''
                INSERT OR IGNORE INTO views (viewer_user_id, joke_id)
                VALUES (?, ?)
            ''', (user_id, joke_id))
            await conn.execute('''
                UPDATE jokes
                SET views = views + 1
                WHERE id = ?
            ''', (joke_id,))
        await conn.commit()


async def has_user_voted(user_id: int, joke_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT id FROM votes
            WHERE voter_user_id = ? AND joke_id = ?
        ''', (user_id, joke_id))
        result = await cursor.fetchone()
        await cursor.close()
    return bool(result)


async def get_user_votes(user_id: int) -> set:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT joke_id FROM votes
            WHERE voter_user_id = ?
        ''', (user_id,))
        rows = await cursor.fetchall()
        await cursor.close()
    return {row[0] for row in rows}


async def get_top_jokes(prompt: str, limit: int = 3):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT jokes.id, jokes.joke_text, jokes.first_name, COUNT(votes.id) as votes_count
            FROM jokes
            LEFT JOIN votes ON jokes.id = votes.joke_id
            WHERE jokes.prompt = ? AND jokes.is_active = 1
            GROUP BY jokes.id
            ORDER BY votes_count DESC
            LIMIT ?
        ''', (prompt, limit))
        rows = await cursor.fetchall()
        await cursor.close()
    return rows


async def clear_jokes():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('DELETE FROM jokes')
        await conn.commit()


async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT COUNT(*), SUM(likes), SUM(views)
            FROM jokes
            WHERE user_id = ?
        ''', (user_id,))
        count, total_likes, total_views = await cursor.fetchone()
        await cursor.close()


        cursor = await db.execute('''
            SELECT prompt, joke_text
            FROM jokes
            WHERE user_id = ?
            LIMIT 1
        ''', (user_id,))
        result = await cursor.fetchone()
        await cursor.close()

    return {
        "jokes": count or 0,
        "likes": total_likes or 0,
        "views": total_views or 0,
        "prompt": result[0] if result else None,
        "joke_text": result[1] if result else None
    }


async def get_jokes_for_scoring(prompt: str, limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('''
            SELECT id, joke_text, first_name, likes, views
            FROM jokes
            WHERE prompt = ?
              AND is_active = 1
              AND likes > 0
            ORDER BY likes DESC
            LIMIT ?
        ''', (prompt, limit))
        rows = await cursor.fetchall()
        await cursor.close()

    return [
        {
            "id":     r[0],
            "text":   r[1],
            "author": r[2],
            "likes":  r[3],
            "views":  r[4],
        }
        for r in rows
    ]


async def clear_votes_and_views():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('DELETE FROM votes')
        await conn.execute('DELETE FROM views')
        await conn.commit()