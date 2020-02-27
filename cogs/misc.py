import discord
import asyncio
import os
import utils
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv
import subprocess

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

    @commands.command(name="sourcecode", help="Links the source code to how I work!")
    async def sourcecode(self, ctx):
        await ctx.send("https://www.github.com/Leothechosen/AmazingBotPython")

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

    @commands.command(name="gitpull")
    @commands.is_owner()
    async def gitpull(self, ctx):
        try:
            subprocess.call(["git", "pull"])
        except:
            await ctx.send("gitpull error")

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
