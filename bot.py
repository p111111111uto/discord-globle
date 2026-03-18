import discord
from discord.ext import commands
import os
import datetime
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = os.getenv('GUILD_ID')
import game
countries_list = game.load_countries()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.db = None

@bot.event
async def on_ready():
    await bot.tree.sync()
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f'Bot is ready.')

# Guess command handler
@bot.tree.command(name='guess', description='Guess today\'s country', guild=discord.Object(id=int(GUILD_ID)))
async def guess(interaction: discord.Interaction, usr_country: str):
    user_id = interaction.user.id

    # If user has won, they can't play again
    row = await bot.db.fetchrow('SELECT last_played FROM players WHERE user_id = $1', user_id)
    if row and row['last_played'] == datetime.date.today():
        await interaction.response.send_message('You\'ve already guessed today!', ephemeral=True)
        return
    
    await bot.db.execute("""
        INSERT INTO players (user_id, total_guesses)
        VALUES ($1, 1)
        ON CONFLICT DO (user_id) DO UPDATE SET total_guesses = players.total_guesses + 1
    """, user_id)

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
        await interaction.followup.send(f'{interaction.user.name} has won!') # Let everyone know user won
        await bot.db.execute("""
                INSERT INTO players (user_id, last_played)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET last_played = $2
                """, user_id, datetime.date.today())
        return
    
    # Response message with relevent info for user's next guess
    await interaction.response.send_message(f'{usr_country} is {distance} miles away {direction}. Proximity: {proximity}%', ephemeral=True)


# Giveup command handler
@bot.tree.command(name='giveup', description='Give up guessing today\'s country', guild=discord.Object(id=int(GUILD_ID)))
async def giveup(interaction: discord.Interaction):
    user_id = interaction.user.id
    row = await bot.db.fetchrow('SELECT last_played FROM players WHERE user_id = $1', user_id)
    if row and row['last_played'] == datetime.date.today():
        await interaction.response.send_message('You\'ve already guessed today!', ephemeral=True)
        return
    todays_country = game.daily_country(countries_list)
    await interaction.response.send_message(f"Country is {todays_country['COUNTRY']}", ephemeral=True)
    await bot.db.execute("""
            INSERT INTO players (user_id, last_played)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET last_played = $2
            """, user_id, datetime.date.today()) # prevent user from guessing again
    return