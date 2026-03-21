import discord
from discord.ext import commands
import os
import datetime
from dotenv import load_dotenv

import logging

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('discord.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import game

# Load all countries from CSV once at startup so every command can use it
countries_list = game.load_countries()

# Enable required gateway intents for reading messages and member info
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.db = None  # asyncpg connection pool, assigned in main.py before bot.run()

@bot.event
async def on_ready():
    # Sync globally first to clear any stale global commands, then sync to guild for instant availability
    await bot.tree.sync()
    print(f'Bot is ready.')

# Guess command handler
@bot.tree.command(name='guess', description='Guess today\'s country')
async def guess(interaction: discord.Interaction, usr_country: str):
  try:
    user_id = interaction.user.id

    # If user has won, they can't play again
    won = await bot.db.fetchrow('SELECT last_played FROM players WHERE user_id = $1', user_id)
    if won and won['last_played'] == datetime.date.today():
        await interaction.response.send_message('You\'ve already guessed today!', ephemeral=True)
        return
    
    # Track every guess attempt, even incorrect ones, for average guess calculation
    await bot.db.execute("""
        INSERT INTO players (user_id, total_guesses, username)
        VALUES ($1, 1, $2)
        ON CONFLICT (user_id) DO UPDATE SET total_guesses = players.total_guesses + 1, username = $2
    """, user_id, interaction.user.name)

    # User's guess
    guessed = game.find_country(usr_country, countries_list)

    # If country cannot be found
    if guessed is None:
        await interaction.response.send_message('Country not found', ephemeral=True)
        return
    
    # Today's answer
    target = game.daily_country(countries_list)

    # Calculate distance from user's guess and target country
    distance = game.haversine(float(guessed['latitude']), float(guessed['longitude']), float(target['latitude']), float(target['longitude']))

    # Directional arrow to guide user
    direction = game.directional_arrows(float(guessed['latitude']), float(guessed['longitude']), float(target['latitude']), float(target['longitude']))

    # Proximity based on distance between countries
    proximity = game.proximity_percent(distance)

    # Win condition
    if distance < 1:
        await interaction.response.send_message(f'Correct! Country was {usr_country}', ephemeral=True)
        await interaction.followup.send(f'{interaction.user.mention} has won!') # Let everyone know user won
        await bot.db.execute("""
                INSERT INTO players (user_id, last_played, username)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET last_played = $2, wins = players.wins +1, username = $3
                """, user_id, datetime.date.today(), interaction.user.name)
        return
    
    # Response message with relevent info for user's next guess
    await interaction.response.send_message(f'{usr_country} is {distance} miles away {direction}. Proximity: {proximity}%', ephemeral=True)

  except Exception as e:
    logger.error(f'Error in /guess command: {e}', exc_info=True)
    await interaction.response.send_message('Something went wrong, please try again.', ephemeral=True)


# Giveup command handler
@bot.tree.command(name='giveup', description='Give up guessing today\'s country')
async def giveup(interaction: discord.Interaction):
    try: 
        user_id = interaction.user.id
        row = await bot.db.fetchrow('SELECT last_played FROM players WHERE user_id = $1', user_id)
        if row and row['last_played'] == datetime.date.today():
            await interaction.response.send_message('You\'ve already guessed today!', ephemeral=True)
            return
        todays_country = game.daily_country(countries_list)
        await interaction.response.send_message(f"Country is {todays_country['COUNTRY']}", ephemeral=True)
        await bot.db.execute("""
                INSERT INTO players (user_id, last_played, username)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET last_played = $2
                """, user_id, datetime.date.today(), interaction.user.name) # prevent user from guessing again
        return
    except Exception as e:
        logger.error(f'Error in /giveup command: {e}', exc_info=True)
        await interaction.response.send_message('Something went wrong, please try again.', ephemeral=True)

@bot.tree.command(name='leaderboard', description='Display leaderboard')
async def leaderboard(interaction: discord.Interaction):
    try:
        rows = await bot.db.fetch("""SELECT user_id, wins, total_guesses, games_played FROM players
        ORDER BY wins DESC LIMIT 10
        """)

        if not rows:
            await interaction.response.send_message('No winners yet!')
            return
        
        leaderboard_text = '🏆 **Leaderboard** 🏆\n\n'
        for i, r in enumerate(rows, start=1):
            # Avoid division by zero for players who have guesses but no wins yet
            avg_guesses = round(r['total_guesses'] /  r['games_played'], 1) if r['games_played'] > 0 else 0
            leaderboard_text += f"{i}. <@{r['user_id']}> - {r['wins']} wins | {avg_guesses} average guesses\n"

        await interaction.response.send_message(leaderboard_text)
    except Exception as e:
        logger.error(f'Error in /leaderboard command: {e}', exc_info=True)
        await interaction.response.send_message('Something went wrong, please try again.', ephemeral=True)

@bot.tree.command(name='hint', description='Want a hint?')
async def hint(interaction: discord.Interaction):
    try:
        user_id = interaction.user.id
        hint = await bot.db.fetchrow("""SELECT user_id, hints_reset_date, last_played FROM players WHERE user_id = $1""", user_id)
        if hint and hint['hints_reset_date'] != datetime.date.today():
            await bot.db.execute("""
                INSERT INTO players (user_id, hints_reset_date)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET hints_used = 0, hints_reset_date = $2
            """, user_id, datetime.date.today())

        guess = await bot.db.fetchrow('SELECT hints_used FROM players WHERE user_id = $1', user_id)
        if guess and guess['hints_used'] >= 4:
            await interaction.response.send_message("You're out of hints today.", ephemeral=True)
            return
        else:
            hints_used = guess['hints_used'] if guess else 0
            target = game.daily_country(countries_list)
            await interaction.response.send_message(game.hint_options(target['COUNTRY'], hints_used), ephemeral=True)
            await bot.db.execute("""
                INSERT INTO players (user_id, hints_used)
                VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET hints_used = players.hints_used + 1
            """, user_id)
    except Exception as e:
        logger.error(f'Error in /hint command: {e}', exc_info=True)
        await interaction.response.send_message('Something went wrong, please try again.', ephemeral=True)