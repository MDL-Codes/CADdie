import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")

async def main():
    async with bot:
        await bot.load_extension("praise")
        await bot.load_extension("qotw")
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
