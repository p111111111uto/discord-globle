import discord
from discord.ext import commands
import game
countries_list = game.load_countries()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

user_state = {}
@bot.command()
async def guess(ctx, *, usr_country):
    user_id = ctx.author.id
    if user_state.get(user_id, {}).get('won'):
        await ctx.send('You\'ve already won today!')
        return

    guessed = game.find_country(usr_country, countries_list)

    if guessed is None:
        await ctx.send('Country not found')
        return
    target = game.daily_country(countries_list)

    distance = game.haversine(float(guessed['latitude']), float(guessed['longitude']), float(target['latitude']), float(target['longitude']))

    if distance < 1:
        await ctx.send(f'Correct! Country was {usr_country}')
        user_state[user_id] = {'won': True}
        return
    
    proximity = game.proximity_percent(distance)

    await ctx.send(f'{usr_country} is {distance} miles away. Proximity: {proximity}%')