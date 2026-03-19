import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

async def create_pool():
    return await asyncpg.create_pool(os.getenv('DATABASE_URL'))

async def create_tables(db):

    await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            wins INT DEFAULT 0,
            total_guesses INT DEFAULT 0,
            games_played INT DEFAULT 0,
            last_played DATE
        );
    """)