import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Creates a connection pool for efficient async database access
async def create_pool():
    return await asyncpg.create_pool(os.getenv('DATABASE_URL'))

# Creates the players table if it doesn't already exist
# Called once at startup — safe to run every time due to IF NOT EXISTS
async def create_tables(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id BIGINT PRIMARY KEY,  -- Discord user ID
            username TEXT,               -- Display name, updated on each interaction
            wins INT DEFAULT 0,          -- Total number of correct guesses
            total_guesses INT DEFAULT 0, -- Total guesses across all games
            games_played INT DEFAULT 0,  -- Total games (wins + giveups)
            last_played DATE             -- Prevents playing more than once per day
        );
    """)