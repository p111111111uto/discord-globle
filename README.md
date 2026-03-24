# 🌍 Globle

A daily geography guessing game for Discord, inspired by [Globle](https://globle-game.com/). Every day a new country is chosen, guess it using distance and direction clues to narrow it down.

## How It Works

Each day a random country is selected as the answer. Players use the `/guess` command to submit a country and receive feedback on how close they are. The closer the guess, the higher the proximity score. An arrow shows which direction the target country is from your guess.

The daily country resets at midnight UTC and is the same for everyone in the server.

## Commands

| Command | Description |
|---|---|
| `/guess [country]` | Guess today's country |
| `/giveup` | Reveal today's country and end your game |
| `/leaderboard` | Show the top 10 players by wins |
| `/hint` | Get a hint about today's country (max 4 per day) |

## Features

- 🌐 **250+ countries and territories** — including overseas territories, islands, and disputed regions
- 📍 **Distance feedback** — see exactly how many miles away your guess is
- 🧭 **Directional arrows** — know which direction to look next
- 📊 **Proximity score** — 0–100% rating based on how close you are
- 🏆 **Persistent leaderboard** — tracks wins and average guesses across all players
- 💡 **Daily hints** — up to 4 hints per day revealing capital, region, neighbors, and languages
- 🔒 **One game per day** — resets automatically at midnight UTC, no cheating

## Tech Stack

- **[discord.py](https://discordpy.readthedocs.io/)** — Discord bot framework
- **[asyncpg](https://magicstack.github.io/asyncpg/)** — async PostgreSQL driver
- **[countryinfo](https://pypi.org/project/countryinfo/)** — country data for hints (capital, region, neighbors, languages)
- **[PostgreSQL](https://www.postgresql.org/)** — persistent player stats and leaderboard
- **[Railway](https://railway.app/)** — hosting and managed Postgres database

## Self Hosting

1. Clone the repo
2. Create a Discord bot at the [Discord Developer Portal](https://discord.com/developers/applications)
3. Set up a PostgreSQL database
4. Create a `.env` file with the following:
```env
DISCORD_TOKEN=your_token
DATABASE_URL=your_postgres_url
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Run the bot:
```bash
python main.py
```
