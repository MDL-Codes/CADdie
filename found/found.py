import discord
import json
import os
from discord.ext import commands
from datetime import datetime, timezone

DATA_FILE = os.path.join(os.path.dirname(__file__), "found_data.json")
FOUND_COLOR = discord.Color.blue()
MEDALS = {0: "🥇", 1: "🥈", 2: "🥉"}
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"finds": [], "bounties": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_bounty(data, user_id):
    return data["bounties"].get(str(user_id), 1)


def get_finder_points(data, user_id):
    return sum(f["points_awarded"] for f in data["finds"] if f["finder_id"] == str(user_id))


def get_times_found(data, user_id):
    return sum(1 for f in data["finds"] if f["found_id"] == str(user_id))


def get_finders_leaderboard(data):
    totals = {}
    for f in data["finds"]:
        uid = f["finder_id"]
        totals[uid] = totals.get(uid, 0) + f["points_awarded"]
    return sorted(totals.items(), key=lambda x: x[1], reverse=True)


def get_found_leaderboard(data):
    totals = {}
    for f in data["finds"]:
        uid = f["found_id"]
        totals[uid] = totals.get(uid, 0) + 1
    return sorted(totals.items(), key=lambda x: x[1], reverse=True)


def build_leaderboard_embed(title, board, guild, label_singular, label_plural):
    embed = discord.Embed(title=title, color=FOUND_COLOR)

    if not board:
        embed.description = "No data yet!"
        return embed

    lines = []
    for i, (user_id, score) in enumerate(board[:10]):
        member = guild.get_member(int(user_id))
        name = member.display_name if member else f"Unknown ({user_id})"
        prefix = MEDALS.get(i, f"{i + 1}.")
        label = label_singular if score == 1 else label_plural
        lines.append(f"{prefix} **{name}** — {score} {label}")

    embed.description = "\n".join(lines)
    return embed


class Found(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.found_channel_id = int(os.getenv("FOUND_CHANNEL_ID"))

    def is_admin_or_mod(self, member):
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild

    @commands.command(name="found")
    async def found_cmd(self, ctx):
        try:
            attachment = ctx.message.attachments[0] if ctx.message.attachments else None
            if not attachment or not any(attachment.filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                await ctx.send("You need to include an image when using `!found`! 📸")
                return

            if not ctx.message.mentions:
                await ctx.send("You need to mention someone! Usage: `!found @person`")
                return

            found_member = ctx.message.mentions[0]

            # if found_member.id == ctx.author.id:
            #     await ctx.send("You can't find yourself! Nice try though. 😄")
            #     return

            data = load_data()
            now = datetime.now(timezone.utc)

            points = get_bounty(data, found_member.id)

            data["finds"].append({
                "finder_id": str(ctx.author.id),
                "found_id": str(found_member.id),
                "timestamp": now.isoformat(),
                "points_awarded": points
            })
            save_data(data)

            finder_total = get_finder_points(data, ctx.author.id)
            times_found = get_times_found(data, found_member.id)

            embed = discord.Embed(
                title="📸 FOUND!",
                description=f"{ctx.author.mention} found **{found_member.display_name}**!",
                color=FOUND_COLOR
            )
            embed.add_field(name="Points Awarded", value=f"+{points} pt{'s' if points != 1 else ''}", inline=True)
            embed.add_field(name=f"{ctx.author.display_name}'s Total", value=f"{finder_total} pt{'s' if finder_total != 1 else ''}", inline=True)
            embed.add_field(name="Times Spotted", value=f"{found_member.display_name} has been found {times_found} time{'s' if times_found != 1 else ''}", inline=False)
            image_file = await attachment.to_file()
            embed.set_image(url=f"attachment://{attachment.filename}")
            embed.set_footer(
                text=f"Found by {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )

            found_channel = self.bot.get_channel(self.found_channel_id)
            if found_channel:
                await ctx.message.delete()
                await found_channel.send(embed=embed, file=image_file)
            else:
                await ctx.send("Couldn't find the found channel.")

        except Exception as e:
            print(f"Error in found command: {e}")
            await ctx.send("Something went wrong with that find. Please try again!")

    @commands.command(name="setbounty")
    async def setbounty(self, ctx, *, message: str = None):
        try:
            if not self.is_admin_or_mod(ctx.author):
                await ctx.send("You need to be an admin or mod to set bounties.")
                return

            if not ctx.message.mentions or not message:
                await ctx.send("Usage: `!setbounty @person <points>`")
                return

            target = ctx.message.mentions[0]

            points_str = next(
                (w for w in message.split() if not (w.startswith("<@") and w.endswith(">"))),
                None
            )

            if points_str is None:
                await ctx.send("Usage: `!setbounty @person <points>`")
                return

            try:
                points = int(points_str)
            except ValueError:
                await ctx.send("Points must be a whole number. Usage: `!setbounty @person <points>`")
                return

            if points < 1:
                await ctx.send("Bounty must be at least 1 point.")
                return

            data = load_data()
            data["bounties"][str(target.id)] = points
            save_data(data)

            embed = discord.Embed(
                title="🎯 Bounty Set!",
                description=f"{target.mention} is now worth **{points} pt{'s' if points != 1 else ''}** when found!",
                color=FOUND_COLOR
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in setbounty command: {e}")
            await ctx.send("Something went wrong setting that bounty. Please try again!")

    @commands.command(name="removebounty")
    async def removebounty(self, ctx):
        try:
            if not self.is_admin_or_mod(ctx.author):
                await ctx.send("You need to be an admin or mod to remove bounties.")
                return

            if not ctx.message.mentions:
                await ctx.send("You need to mention someone! Usage: `!removebounty @person`")
                return

            target = ctx.message.mentions[0]
            data = load_data()

            if str(target.id) not in data["bounties"]:
                await ctx.send(f"{target.display_name} doesn't have a custom bounty set.")
                return

            del data["bounties"][str(target.id)]
            save_data(data)

            embed = discord.Embed(
                title="🎯 Bounty Removed",
                description=f"{target.mention}'s bounty has been reset to **1 pt**.",
                color=FOUND_COLOR
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in removebounty command: {e}")
            await ctx.send("Something went wrong removing that bounty. Please try again!")

    @commands.command(name="bounties")
    async def bounties_cmd(self, ctx):
        try:
            data = load_data()

            if not data["bounties"]:
                await ctx.send("There are no active bounties right now.")
                return

            lines = []
            for user_id, points in sorted(data["bounties"].items(), key=lambda x: x[1], reverse=True):
                member = ctx.guild.get_member(int(user_id))
                name = member.display_name if member else f"Unknown ({user_id})"
                lines.append(f"**{name}** — {points} pt{'s' if points != 1 else ''}")

            embed = discord.Embed(
                title="🎯 Active Bounties",
                description="\n".join(lines),
                color=FOUND_COLOR
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in bounties command: {e}")
            await ctx.send("Something went wrong fetching bounties. Please try again!")

    @commands.command(name="foundhelp")
    async def foundhelp(self, ctx):
        embed = discord.Embed(
            title="📸 FOUND — How to Play",
            description=(
                "Spot a fellow member in the wild? Snap a pic, log the sighting, "
                "earn points. The more elusive the target, the bigger the reward."
            ),
            color=FOUND_COLOR
        )
        embed.add_field(
            name="🕹️ Log a sighting",
            value=(
                "`!found @person` — **with a photo attached**.\n"
                "Your message gets reposted in the #found channel as proof."
            ),
            inline=False
        )
        embed.add_field(
            name="💰 Points & Bounties",
            value=(
                "Everyone is worth **1 pt** by default. Mods can place a bounty "
                "to make someone worth more.\n`!bounties` — see who's worth extra."
            ),
            inline=False
        )
        embed.add_field(
            name="🏆 Leaderboards",
            value="`!leaderboard` — top finders and most-spotted members.",
            inline=False
        )
        embed.add_field(
            name="🛠️ Mod Commands",
            value=(
                "`!setbounty @person <points>` — set a custom bounty\n"
                "`!removebounty @person` — reset to 1 pt"
            ),
            inline=False
        )
        embed.add_field(
            name="✅ Rules",
            value=(
                "📸 Photo required — no pic, no points.\n"
                "🏷️ @mention the person you found.\n"
                "🤝 Keep sightings fun and consensual."
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        try:
            data = load_data()

            embed = build_leaderboard_embed(
                "🏆 Finders Leaderboard",
                get_finders_leaderboard(data),
                ctx.guild, "pt", "pts"
            )
            await ctx.send(embed=embed)

            embed = build_leaderboard_embed(
                "👁️ Most Spotted Leaderboard",
                get_found_leaderboard(data),
                ctx.guild, "time", "times"
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in leaderboard command: {e}")
            await ctx.send("Something went wrong fetching the leaderboard. Please try again!")


async def setup(bot):
    await bot.add_cog(Found(bot))
