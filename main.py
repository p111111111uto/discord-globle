import bot
import logging
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

bot.bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)