import asyncio
import asyncpg
import bot
import logging
import os
import database
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

async def run():
    db = await database.create_pool()
    await database.create_tables(db)
    bot.bot.db = db

    await bot.bot.start(DISCORD_TOKEN)

asyncio.run(run())