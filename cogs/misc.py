import discord
import asyncio
import os
import utils
import pytz
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv
import apirequests
import logging
import random
import database
import matplotlib.pyplot as plt
import psutil
import platform

logger = logging.getLogger("AmazingBot." + __name__)
load_dotenv()
amazingserverid = int(os.getenv("AMAZING_SERVER_ID"))
servertimechannel = int(os.getenv("SERVER_TIME_CHANNEL"))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.theserverTime.start() # pylint: disable=no-member
    
    @commands.command(name="temp")
    async def temp(self, ctx, temperature_and_unit):
        """Returns a given temperature in the other two common units. Example: `-temp 32F` returns `32F = 0C = 273.15K`"""
        try:
            tempunit = temperature_and_unit[-1].upper()
            temper = temperature_and_unit[:-1]
            if tempunit == "F":
                tempC = (float(temper) - 32) * (5 / 9)
                tempK = tempC + 273.15
                await ctx.send(f'{temper}{tempunit} = {tempC}C = {tempK}K')
            elif tempunit == "C":
                tempF = (float(temper) * (9 / 5)) + 32
                tempK = float(temper) + 273.15
                await ctx.send(f'{temper}{tempunit} = {tempF}F = {tempK}K')
            elif tempunit == "K":
                tempC = float(temper) - 273.15
                tempF = (tempC * (9 / 5)) + 32
                await ctx.send(f'{temper}{tempunit} = {tempC}C = {tempF}F')
            else:
                await ctx.send("Invalid request")
        except:
            await ctx.send(
                "An error occurred. This is likely due to the fact that you have a non-numerical character in your request (excluding the trailing F/C)"
            )

    @commands.command(name="playlist")
    async def playlist(self, ctx):
        """Returns a link to Amazing's stream playlist"""
        await ctx.send(
            "Maurice's stream playlist can be found here: https://open.spotify.com/playlist/3Ae9kHY7VgXTg6KwsbWVnn?si=gVNIAIuDSyWFb2ZULr-hZQ "
        )

    @commands.command(name="8ball")
    async def eight_ball(self, ctx):
        """Returns a classic 8ball response"""
        responses = [
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful",
            "Without a doubt.",
            "Yes.",
            "Yes- definitely",
            "You may rely on it",
        ]
        await ctx.send(responses[random.randint(0, len(responses))])
    
    @commands.group()
    async def fah(self, ctx):
        """Folding@Home | Subcommands are team and user"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are team and user. See pinned message for usage.")
        return
    
    @fah.command()
    async def team(self, ctx, team):
        """Returns information on the given team. Amazing's team code is 242203"""
        teamresponse = await apirequests.foldingathome(ctx, "team", team)
        user_message = ""
        credit_message = ""
        rank_message = ""
        for x in range(len(teamresponse["donors"])):
            user_message += teamresponse["donors"][x]["name"] + '\n'
            credit_message += str(teamresponse["donors"][x]["credit"]) + '\n'
            if "rank" in teamresponse["donors"][x]:
                rank_message += str(teamresponse["donors"][x]["rank"]) + '\n'
            else:
                rank_message += "N/A" + '\n'
        embed = discord.Embed(title="F@H " + teamresponse["name"], color=0xA9152B)
        embed.add_field(name="User", value=user_message, inline=True)
        embed.add_field(name="Credits", value=credit_message, inline=True)
        embed.add_field(name="Rank", value=rank_message, inline=True)
        embed.set_footer(text="Folding@Home API updates once or twice a day.")
        await ctx.send(embed=embed)
        return
    
    @fah.command()
    async def user(self, ctx, user):
        """Returns information on the given user"""
        userresponse = await apirequests.foldingathome(ctx, "donor", user)
        stats_name_message = "Work Units" + '\n' + "Rank" + '\n' + "Date of Last WU" + '\n' + "Credits"
        stats_message = str(userresponse["wus"]) + '\n' + str(userresponse["rank"]) + '\n' + str(userresponse["last"]) + '\n' + str(userresponse["credit"])
        embed = discord.Embed(title="F@H " + userresponse["name"], color=0xA9152B)
        embed.add_field(name="Stats", value=stats_name_message, inline=True)
        embed.add_field(name="Value", value=stats_message, inline=True)
        embed.set_footer(text="Folding@Home API updates once or twice a day.")
        await ctx.send(embed=embed)
        return

    @commands.command(name="online")
    async def piechart(self, ctx):
        """Returns a pie chart of users online, idle, DND, and offline"""
        online = 0
        offline = 0
        dnd = 0
        idle = 0
        for member in ctx.guild.members:
            status = str(member.status)
            if status == "online":
                online += 1
            elif status == "idle":
                idle += 1
            elif status == "dnd" or status == "do_not_disturb":
                dnd += 1
            elif status  == "offline" or status == "invisible":
                offline += 1
            else:
                logger.info(f"Error with member: {member} | Status: {member.status}")
        total = online+offline+dnd+idle
        labels = f'Online ({online})', f'Idle ({idle})', f'DND ({dnd})', f'Offline ({offline})'
        slices = (online/total, idle/total, dnd/total, offline/total)
        fig, axes = plt.subplots()
        axes.pie(slices, labels = labels, autopct = '%.1f%%', colors=("green", "orange", "red", "DarkGray"))
        axes.axis('equal')
        axes.margins(tight=True)
        fig.savefig("test.png")
        await ctx.send(file=discord.File('test.png'))
        os.remove("test.png")
        return


    @commands.command(name="reactionroles", hidden=True)
    @commands.is_owner()
    async def reactionroles(self, ctx):
        reactions = await utils.role_reaction_emojis()
        embed = discord.Embed(title="Add/remove a reaction to add/remove the corresponding role", color=0xA9152B)
        embed.add_field(name="Regional Roles", value=f'{reactions["NA"]} (NA)\n{reactions["EUNE"]} (EUNE)\n{reactions["EUW"]} (EUW)\n{reactions["OCE"]} (OCE)', inline=False)
        embed.add_field(name="Channel Roles", value=f'{reactions["18"]} (Access to #dirty-leo-chat)', inline=False)
        reactionRoleMsg = await ctx.send(embed=embed)
        for reaction in reactions:
            await discord.Message.add_reaction(reactionRoleMsg, reactions[reaction])
        return

    @tasks.loop(seconds=301)
    async def theserverTime(self):
        allGuildSettings = await database.getAllGuildSettings()
        fmt = "%H:%M %Z"
        for guild in allGuildSettings:
            if guild[1] is not None:
                channel_for_servertime = self.bot.get_channel(id=guild[1])
                serverTime = datetime.now(timezone(guild[2]))
                serverTime = serverTime.strftime(fmt)
                await channel_for_servertime.edit(name=serverTime)
                await asyncio.sleep(0.1)
    
    @theserverTime.before_loop
    async def before_theserverTime(self):
        time_now = datetime.now(timezone("CET"))
        fmt2 = "%M"
        fmt3 = "%S"
        minutecheck = int(time_now.strftime(fmt2))%5
        secondcheck = int(time_now.strftime(fmt3))
        if minutecheck != 0:
            minutecheck = (5-minutecheck)*60
            logger.info(minutecheck-secondcheck)
            await asyncio.sleep(minutecheck-secondcheck)
        else:
            secondcheck = 62-secondcheck
            logger.info(secondcheck)
            await asyncio.sleep(secondcheck)

def setup(bot):
    bot.add_cog(Misc(bot))