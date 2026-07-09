import discord
from discord.ext import commands, tasks
from datetime import datetime, date
import pytz
import os

ET = pytz.timezone("America/New_York")

# First Monday the update should go out; it then repeats every 2nd Monday.
ANCHOR_MONDAY = date(2026, 7, 13)


class SubteamUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subteam_channel_id = int(os.getenv("SUBTEAM_CHANNEL_ID"))

        # Remember the last day we sent, so a restart can't double-post.
        self.state_path = os.path.join(os.path.dirname(__file__), "last_sent.txt")
        self.last_sent = self.load_last_sent()

        self.send_update_reminder.start()

    def load_last_sent(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r") as f:
                return f.read().strip()
        return ""

    def save_last_sent(self, value):
        with open(self.state_path, "w") as f:
            f.write(value)

    def is_send_day(self, day):
        # Every other Monday, anchored on ANCHOR_MONDAY.
        return day.weekday() == 0 and (day - ANCHOR_MONDAY).days % 14 == 0

    @tasks.loop(minutes=1)
    async def send_update_reminder(self):
        now = datetime.now(ET)
        today = now.date()
        today_str = today.isoformat()
        # Fire once, any time from 18:00 onward on an "on" Monday. The window
        # (instead of an exact minute) means a restart near 18:00 won't lose it,
        # and last_sent makes sure it only goes out once that day.
        if self.is_send_day(today) and now.hour >= 18 and self.last_sent != today_str:
            self.last_sent = today_str
            self.save_last_sent(today_str)
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
