import discord
import apirequests
from discord.ext import commands
import logging

logger = logging.getLogger("AmazingBot." + __name__)


class Lor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def lor(self, ctx):
        """Legends of Runeterra | Currently, the only subcommand is leaderboard
        Valid regions are Americas, Europe, and Asia"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are leaderboard")
        return

    @lor.command()
    async def leaderboard(self, ctx, region=None):
        """Returns the leaderboard for a given region"""
        leaderboard_message = ""
        rank_message = ""
        valid_regions = ["americas", "europe", "asia"]
        if region == None:
            await ctx.send("Usage: `-lor leaderboards [region]`. Supported regions are: Americas, Asia, Europe")
            return
        if region.lower() not in valid_regions:
            await ctx.send("Invalid region. Supported regions are: Americas, Asia, Europe")
            return
        leaderboards = await apirequests.lor(ctx, region, "ranked", "leaderboards", "")
        for x in range(len(leaderboards["players"])):
            rank_message += str(x + 1) + "\n"
            leaderboard_message += leaderboards["players"][x]["name"] + "\n"
        embed = discord.Embed(title="LoR Master Tier in " + region.title(), color=0xA9152B)
        embed.add_field(name="Rank", value=rank_message, inline=True)
        embed.add_field(name="Name", value=leaderboard_message, inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lor(bot))
