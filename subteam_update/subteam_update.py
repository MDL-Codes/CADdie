import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import os

class SubteamUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subteam_channel_id = int(os.getenv("SUBTEAM_CHANNEL_ID"))
        self.send_update_reminder.start()

    @tasks.loop(minutes=1)
    async def send_update_reminder(self):
        now = datetime.now(pytz.timezone("America/New_York"))
        if now.strftime("%A %H:%M") == "Monday 18:00":
            await self.send_reminder()

    async def send_reminder(self):
        channel = self.bot.get_channel(self.subteam_channel_id)
        if channel:
            embed = discord.Embed(
                title="📣 Weekly Subteam Update",
                description=(
                    "Hey team leads! 👋\n\n"
                    "It's time for your **weekly update**. Please share a quick "
                    "recap of what your team accomplished this past week, what's "
                    "coming up next, and any blockers you'd like help with.\n\n"
                    "Thanks for keeping everyone in the loop! 💜"
                ),
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)
        else:
            print("⚠️ Could not find the subteam channel.")

    @commands.command(name="testupdate")
    async def test_update(self, ctx):
        await self.send_reminder()

    @send_update_reminder.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(SubteamUpdate(bot))
