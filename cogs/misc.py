import discord
import asyncio
import os
import utils
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
import apirequests
import subprocess
import logging
import random

logger = logging.getLogger("AmazingBot." + __name__)
load_dotenv()
amazingserverid = int(os.getenv("AMAZING_SERVER_ID"))
servertimechannel = int(os.getenv("SERVER_TIME_CHANNEL"))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("AmazingBot connected to Discord")
        await theserverTime(self)

    @commands.command(name="restartservertime")
    @commands.has_role("Moderators")
    async def restartservertime(self, ctx):
        await ctx.send("Restarting the clock...")
        await theserverTime(self)

    @commands.command(name="temp")
    async def temp(self, ctx, temper=None):
        if temper == None:
            await ctx.send("Usage: -temp [temperature]. For example: -temp 14F will return -10C")
            return
        try:
            tempunit = temper[-1].upper()
            temper = temper[:-1]
            print(tempunit)
            print(temper)
            if tempunit == "F":
                tempC = (float(temper) - 32) * (5 / 9)
                tempK = tempC + 273.15
                await ctx.send(temper + tempunit + " = " + str(tempC) + "C = " + str(tempK) + "K")
            elif tempunit == "C":
                tempF = (float(temper) * (9 / 5)) + 32
                tempK = float(temper) + 273.15
                await ctx.send(temper + tempunit + " = " + str(tempF) + "F = " + str(tempK) + "K")
            elif tempunit == "K":
                tempC = float(temper) - 273.15
                tempF = (tempC * (9 / 5)) + 32
                await ctx.send(temper + tempunit + " = " + str(tempC) + "C = " + str(tempF) + "F")
            else:
                await ctx.send("Invalid request")
        except:
            await ctx.send(
                "An error occurred. This is likely due to the fact that you have a non-numerical character in your request (excluding the trailing F/C)"
            )

    @commands.command(name="avatar")
    async def avatar(self, ctx):
        embed = discord.Embed(title="Avatar", color=0xA9152B)
        embed.set_image(url="https://i.imgur.com/TwEsQ4D.png")
        embed.add_field(
            name="Info",
            value="AmazingBot's Avatar was made by Sel.\n https://twitter.com/owocifer \n https://www.instagram.com/sel.bro",
            inline=False,
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="playlist")
    async def playlist(self, ctx):
        await ctx.send(
            "Maurice's stream playlist can be found here: https://open.spotify.com/playlist/3Ae9kHY7VgXTg6KwsbWVnn?si=gVNIAIuDSyWFb2ZULr-hZQ "
        )

    @commands.command(name="embedtest")
    @commands.is_owner()
    async def embedtest(self, ctx):
        discord_embed = await utils.embedgen(ctx)
        embed = discord.Embed.from_dict(discord_embed)
        await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def eight_ball(self, ctx):
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

    @commands.command(name="sourcecode")
    async def sourcecode(self, ctx):
        try:
            githubrequest = await apirequests.github()
            last_commit_time = str(
                datetime.strptime(githubrequest[0]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
            )
            last_commit_msg = githubrequest[0]["commit"]["message"]
            embed = discord.Embed(title="AmazingBot Source Code", color=0xA9152B)
            embed.add_field(name="Link", value="https://github.com/Leothechosen/AmazingBotPython", inline=False)
            embed.add_field(name="Last commit - " + last_commit_time + " UTC", value=last_commit_msg, inline=False)
            embed.set_footer(icon_url="https://i.imgur.com/TwEsQ4D.png", text="Created on 2020-01-06 at 05:55:11 UTC")
            await ctx.send(embed=embed)
            return
        except Exception as e:
            logging.error(e)
            return


async def theserverTime(self):
    minutecheck = datetime.now(timezone("CET"))
    fmt = "%H:%M %Z"
    fmt2 = "%s"
    minutecheck = int(minutecheck.strftime(fmt2))
    minutecheck = 61 - (minutecheck % 60)
    await asyncio.sleep(minutecheck)
    while True:
        servertime = self.bot.get_channel(id=servertimechannel)
        berlin = datetime.now(timezone("CET"))
        berlin = berlin.strftime(fmt)
        await servertime.edit(name=berlin)
        await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Misc(bot))
