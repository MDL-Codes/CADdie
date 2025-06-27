import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import os

class QOTW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.qotw_channel_id = int(os.getenv("QOTW_CHANNEL_ID"))

        # Load questions and gifs
        self.questions = self.load_lines("questions.txt")
        self.gifs = self.load_lines("qotw_gifs.txt")
        self.index = 0

        self.send_question.start()

    def load_lines(self, file_name):
        path = os.path.join(os.path.dirname(__file__), file_name)
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    @tasks.loop(minutes=1)
    async def send_question(self):
        now = datetime.now(pytz.timezone("America/New_York"))
        if now.strftime("%A %H:%M") == "Thursday 20:15":
            if self.index < len(self.questions):
                await self.send_qotw()
            else:
                print("✅ All QOTW questions have been sent.")

    async def send_qotw(self):
        channel = self.bot.get_channel(self.qotw_channel_id)
        if channel:
            embed = discord.Embed(
                title="🧠 Question of the Week!",
                description=self.questions[self.index],
                color=discord.Color.purple()
            )
            embed.set_image(url=self.gifs[self.index])
            await channel.send(embed=embed)
            self.index += 1
        else:
            print("⚠️ Could not find the QOTW channel.")

    @commands.command(name="testq")
    async def test_qotw(self, ctx):
        await self.send_qotw()

    @send_question.before_loop
    async def before_qotw(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(QOTW(bot))