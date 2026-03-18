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
    await database.create_pool(db)
    bot.bot.db = db

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    bot.bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

asyncio.run(run())