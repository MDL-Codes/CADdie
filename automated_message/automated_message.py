import os
import datetime

import discord
import pandas as pd
from discord.ext import commands, tasks
from discord import AllowedMentions


class ScheduleReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        script_dir = os.path.dirname(__file__)
        self.schedule_file = os.path.join(script_dir, "schedule.xlsx")
        channel_id_str = os.getenv("ANNOUCEMENT_CHANNEL_ID")
        if not channel_id_str:
            raise RuntimeError("ANNOUCEMENT_CHANNEL_ID environment variable is not set.")
        self.announcement_channel_id = int(channel_id_str)
        self.schedule = self.load_schedule()
        self.check_events.start()

    def parse_time_cell(self, value) -> tuple[int, int]:
        if isinstance(value, datetime.time):
            return value.hour, value.minute
        if isinstance(value, datetime.datetime):
            return value.hour, value.minute
        time_str = str(value).strip()
        parts = time_str.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        return hour, minute

    def parse_date_cell(self, value) -> datetime.date:
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        date_str = str(value).strip()
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def load_schedule(self):
        if not os.path.exists(self.schedule_file):
            return []
        df = pd.read_excel(self.schedule_file)
        required_cols = {"name", "date", "time", "offset_minutes", "location"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"schedule.xlsx must contain columns: {', '.join(required_cols)}")
        events = []
        now = datetime.datetime.now()
        for _, row in df.iterrows():
            event_date = self.parse_date_cell(row["date"])
            hour, minute = self.parse_time_cell(row["time"])
            offset = int(row["offset_minutes"])
            loc_val = row["location"]
            if pd.isna(loc_val):
                raise ValueError(f"Missing location for event row with name={row.get('name', '<unknown>')}")
            location = str(loc_val).strip()
            event_dt = datetime.datetime(event_date.year, event_date.month, event_date.day, hour, minute)
            reminder_dt = event_dt - datetime.timedelta(minutes=offset)
            if event_dt < now:
                continue
            events.append(
                {
                    "name": str(row["name"]).strip(),
                    "event_dt": event_dt,
                    "reminder_dt": reminder_dt,
                    "location": location,
                    "fired": False,
                }
            )
        return events

    def format_time_12h(self, dt: datetime.datetime) -> str:
        hour = dt.hour
        minute = dt.minute
        suffix = "am"
        h = hour
        if h == 0:
            h = 12
            suffix = "am"
        elif 1 <= h < 12:
            suffix = "am"
        elif h == 12:
            suffix = "pm"
        else:
            h -= 12
            suffix = "pm"
        if minute == 0:
            return f"{h}{suffix}"
        else:
            return f"{h}:{minute:02d}{suffix}"

    @tasks.loop(seconds=30)
    async def check_events(self):
        if not self.schedule:
            return
        now = datetime.datetime.now()
        today = now.date()
        channel = self.bot.get_channel(self.announcement_channel_id)
        if channel is None:
            return
        for event in self.schedule:
            if event["fired"]:
                continue
            event_dt = event["event_dt"]
            reminder_dt = event["reminder_dt"]
            if event_dt.date() != today:
                continue
            if reminder_dt <= now < event_dt:
                name = event["name"]
                location = event["location"]
                name_display = name.capitalize()
                offset_minutes = int((event_dt - reminder_dt).total_seconds() // 60)
                nice_time = self.format_time_12h(event_dt)
                message = (
                    f"Hey @everyone, as a reminder, {name_display} will be taking place "
                    f"in {offset_minutes} minutes at {nice_time} (Location: {location})"
                )
                try:
                    await channel.send(message, allowed_mentions=AllowedMentions(everyone=True))
                    event["fired"] = True
                except Exception:
                    pass

    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()

    @commands.command(name="reload_schedule")
    @commands.has_permissions(manage_guild=True)
    async def reload_schedule(self, ctx: commands.Context):
        self.schedule = self.load_schedule()
        await ctx.send(
            f"Schedule reloaded from schedule.xlsx. {len(self.schedule)} upcoming events loaded."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ScheduleReminder(bot))
