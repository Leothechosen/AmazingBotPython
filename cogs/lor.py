import discord
import aiohttp
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
apikey = os.getenv("RIOT_API_KEY")


class Lor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def lor(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are leaderboard")
        return

    @lor.command(pass_context=True)
    async def leaderboard(self, ctx, region=None):
        leaderboard_message = ""
        rank_message = ""
        valid_regions = ["americas", "europe", "asia"]
        if region == None:
            await ctx.send("Usage: `-lor leaderboards [region]`. Supported regions are: Americas, Asia, Europe")
            return
        if region.lower() not in valid_regions:
            await ctx.send("Invalid region. Supported regions are: Americas, Asia, Europe")
            return
        embed = discord.Embed(title="LoR Master Tier in " + region.title(), color=0xA9152B)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://" + region + ".api.riotgames.com/lor/ranked/v1/leaderboards?api_key=" + apikey
            ) as response:
                if response.status != 200:
                    await ctx.send(
                        "Riot API returned a bad request. Check for errors, or tell Leo to reset his API key."
                    )
                    return
                leaderboards = await response.json()
                for x in range(len(leaderboards["players"])):
                    rank_message += str(x + 1) + "\n"
                embed.add_field(name="Rank", value=rank_message, inline=True)
                for x in range(len(leaderboards["players"])):
                    leaderboard_message += leaderboards["players"][x]["name"] + "\n"
                embed.add_field(name="Name", value=leaderboard_message, inline=True)
        await session.close()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Lor(bot))
