import asyncio
import asyncpg
import bot
import os
import database
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

async def run():
    # Set up the database connection pool and ensure tables exist before starting the bot
    db = await database.create_pool()
    await database.create_tables(db)

    # Attach the db pool to the bot so commands can access it via bot.db
    bot.bot.db = db

    await bot.bot.start(DISCORD_TOKEN)

asyncio.run(run())