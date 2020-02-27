import discord
import aiohttp
import asyncio
import utils
import apirequests
from discord.ext import commands
import logging

logger = logging.getLogger("AmazingBot." + __name__)

class League(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, aliases=["League"])
    async def league(self, ctx):
        logger.info(" Message: '" + ctx.message.content + "' - User: " + str(ctx.message.author))
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are rank and profile")
        return

    @league.command(pass_context=True, aliases=["Rank"])
    async def rank(self, ctx, name=None, region=None):
        if name == None:
            await ctx.send(
                "Usage: `-league rank [Summoner_name][region]`. Valid regions are: RU, KR, BR, OCE, JP, NA, EUNE, EUW, TR, LAN, and LAS."
            )
            return
        if region == None:
            await ctx.send("You did not specify a region")
            return
        embed = discord.Embed(title=name + "'s Ranks in " + region, color=0xA9152B)
        region = await utils.region_to_valid_region(region.upper())
        if region == "Invalid Region":
            await ctx.send("The server you entered is invalid, or it's a Garena server")
        else:
            summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", name)
            summonerid = summoneridrequest["id"]
            rankedrequest = await apirequests.league(ctx, region, "league", "entries/by-summoner/", summonerid)
            # tftrequest = await apirequests.league(ctx, region, "league", "entries/by-summoner", summonerid)
            if rankedrequest == []:  # and tftrequest == []:
                embed.add_field(name="Unranked", value=name + " is unranked in all queues")
                await ctx.send(embed=embed)
                return
            if rankedrequest != []:
                for x in range(len(rankedrequest)):
                    tier_rank_lp = (
                        rankedrequest[x]["tier"]
                        + " "
                        + rankedrequest[x]["rank"]
                        + " "
                        + str(rankedrequest[x]["leaguePoints"])
                        + "LP "
                    )
                    message = tier_rank_lp
                    if "miniSeries" in rankedrequest[x]:
                        message += "| Promo: "
                        for y in range(len(rankedrequest[x]["miniSeries"]["progress"])):
                            promo_game = rankedrequest[x]["miniSeries"]["progress"][y]
                            if promo_game == "W":
                                message += ":white_check_mark:"
                            elif promo_game == "N":
                                message += ":grey_question:"
                            elif promo_game == "L":
                                message += ":x:"
                    if rankedrequest[x]["queueType"] == "RANKED_SOLO_5x5":
                        embed.add_field(name="Solo", value=message, inline=False)
                    elif rankedrequest[x]["queueType"] == "RANKED_FLEX_SR":
                        embed.add_field(name="Flex", value=message, inline=False)
                    else:
                        continue
            # if tftrequest != []:
            # embed.add_field(name="TFT", value=tftrequest[0]["tier"] + " " + tftrequest[0]["rank"] + " " + str(tftrequest[0]["leaguePoints"]) + "LP",inline=True)
            await ctx.send(embed=embed)
            return

    @league.command(pass_context=True, aliases=["Profile"])
    async def profile(self, ctx, name=None, region=None):
        mastery_message = ""
        profileicon = ""
        summonerid = ""
        if name == None:
            await ctx.send(
                "Usage: `-league profile [Summoner_name] [region]`. Valid regions are: RU, KR, BR, OCE, JP, NA, EUNE, EUW, TR, LAN, and LAS."
            )
            return
        if region == None:
            await ctx.send("You did not specify a region")
            return
        embed = discord.Embed(title=name + "'s Profile on " + region.upper(), color=0xA9152B)
        region = await utils.region_to_valid_region(region.upper())
        summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", name)
        profileicon = summoneridrequest["profileIconId"]
        # accountid = summoneridrequest['accountId']
        # summonerlevel = summoneridrequest['summonerLevel']
        summonerid = summoneridrequest["id"]
        embed.set_thumbnail(
            url="http://ddragon.leagueoflegends.com/cdn/10.3.1/img/profileicon/" + str(profileicon) + ".png"
        )
        masteries = await apirequests.league(
            ctx, region, "champion-mastery", "champion-masteries/by-summoner/", summonerid
        )
        for x in range(3):
            champions = await utils.championid_to_champion(str(masteries[x]["championId"]))
            masterypoints = str(masteries[x]["championPoints"])
            mastery_message += champions + " | " + masterypoints + "\n"
        embed.add_field(name="Top 3 Masteries", value=mastery_message, inline=False)
        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(League(bot))
