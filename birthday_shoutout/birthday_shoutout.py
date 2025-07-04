import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import random
import os
import csv
import json

class BirthdayShoutout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_channel_id = int(os.getenv("TEST_CHANNEL_ID"))
        self.birthdays = self.load_birthdays_from_env()
        self.gifs = self.load_gifs("birthday_gifs.txt")
        self.shoutout_loop.start()


    def load_birthdays_from_env(self):
        data = os.getenv("BIRTHDAYS_JSON")
        if not data:
            return {}
        
        loaded = json.loads(data)
        birthdays = {}
        for entry in loaded:
            date = entry["date"]
            mention = f"<@{entry['id']}>"
            birthdays[date] = birthdays.get(date, []) + [mention]
        return birthdays


    def load_gifs(self, file_name):
        path = os.path.join(os.path.dirname(__file__), file_name)
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    @tasks.loop(minutes=1)
    async def shoutout_loop(self):
        now = datetime.now(pytz.timezone("America/New_York"))
        if now.strftime("%H:%M") == "08:00":
            today = now.strftime("%m-%d")
            if today in self.birthdays:
                await self.send_birthday_shoutout(today)

    async def send_birthday_shoutout(self, today):
        channel = self.bot.get_channel(self.birthday_channel_id)
        if channel:
            mentions = ", ".join(self.birthdays[today])
            gif_url = random.choice(self.gifs)

            embed = discord.Embed(
                title="🎉 Happy Birthday! 🎉",
                description=f"Happy birthday to {mentions} ! 🎂",
                color=discord.Color.gold()
            )
            embed.set_image(url=gif_url)

            await channel.send(embed=embed)

    @shoutout_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BirthdayShoutout(bot))