import aiosqlite
from datetime import datetime, timedelta

DB_PATH = "db.sqlite3"

async def setup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS spins (user_id INTEGER, timestamp TEXT)")
        await db.commit()

async def user_already_played(user_id: int):
    now = datetime.now()
    eight_hours_ago = now - timedelta(hours=8)
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT timestamp FROM spins WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                last_time = datetime.fromisoformat(row[0])
                return last_time > eight_hours_ago
            return False

async def save_user_spin(user_id: int):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO spins (user_id, timestamp) VALUES (?, ?)", (user_id, now))
        await db.commit()

async def clean_old_spins():
    eight_hours_ago = (datetime.now() - timedelta(hours=8)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM spins WHERE timestamp < ?", (eight_hours_ago,))
        await db.commit()
