import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

async def run():
    db = await asyncpg.create_pool(os.getenv('DATABASE_URL'))

    await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id BIGINT PRIMARY KEY,
            wins INT DEFAULT 0,
            total_guesses INT DEFAULT 0,
            games_played INT DEFAULT 0,
            last_played DATE
        );
    """)