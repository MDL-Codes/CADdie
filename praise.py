import discord
import random
import os
from discord.ext import commands

class Praise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clap_gifs = self.load_gif_links('praise_gifs.txt')

    def load_gif_links(self, file_name):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, file_name)
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]

    def get_random_clap_gif(self):
        return random.choice(self.clap_gifs)

    @commands.command(name='praise')
    async def praise(self, ctx, *, message: str):
        try:
            members = []
            reason = ""
            words = message.split()

            for word in words:
                if word.startswith("<@") and word.endswith(">"):
                    user_id = int(word[2:-1].replace("!", ""))
                    member = ctx.guild.get_member(user_id)
                    if member:
                        members.append(member)
                else:
                    reason += word + " "

            reason = reason.strip()

            if not members:
                await ctx.send("You need to mention at least one member to praise.")
                return

            mentions = ", ".join([member.mention for member in members])
            embed = discord.Embed(
                title=":sparkles: PRAISE ALERT :sparkles:",
                description=f"{ctx.author.mention} praises {mentions}",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(
                text=f"Praised by {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )

            clap_gif_url = self.get_random_clap_gif()
            embed.set_image(url=clap_gif_url)

            #praise_channel_id = int(os.getenv("TEST_CHANNEL_ID"))
            praise_channel_id = int(os.getenv("PRAISE_CHANNEL_ID"))
            praise_channel = self.bot.get_channel(praise_channel_id)

            if praise_channel:
                await praise_channel.send(embed=embed)
            else:
                await ctx.send("Couldn't fine the praise channel.")

            await ctx.message.delete()


        except Exception as e:
            print(f"Error in praise command: {e}")
            await ctx.send("There was an error trying to praise the members. Please try again.")

async def setup(bot):
    await bot.add_cog(Praise(bot))