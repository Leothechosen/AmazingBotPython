import discord
import asyncio
import os
import utils
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv
import apirequests
import logging
import random

logger = logging.getLogger("AmazingBot." + __name__)
load_dotenv()
amazingserverid = int(os.getenv("AMAZING_SERVER_ID"))
servertimechannel = int(os.getenv("SERVER_TIME_CHANNEL"))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.theserverTime.start() # pylint: disable=no-member

    @commands.Cog.listener()
    async def on_ready(self):
        print("AmazingBot connected to Discord")

    @commands.command(name="restartservertime")
    @commands.has_role("Moderators")
    async def restartservertime(self, ctx):
        await ctx.send("Restarting the clock...")
        self.theserverTime.start() # pylint: disable=no-member
    
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

    @commands.command(name="sourcecode", aliases=["github"])
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
    
    @commands.group(pass_context=True)
    async def fah(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are team and user. See pinned message for usage.")
        return
    
    @fah.command(pass_context=True)
    async def team(self, ctx, team=None):
        if team is None:
            await ctx.send("Usage: `-fah team [team_id]`. Amazingx Community's team id is 242203")
            return
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
    
    @fah.command(pass_context=True)
    async def user(self, ctx, user=None):
        if user is None:
            await ctx.send("Usage: `-fah user [user_name]`")
            return
        userresponse = await apirequests.foldingathome(ctx, "donor", user)
        stats_name_message = "Work Units" + '\n' + "Rank" + '\n' + "Date of Last WU" + '\n' + "Credits"
        stats_message = str(userresponse["wus"]) + '\n' + str(userresponse["rank"]) + '\n' + str(userresponse["last"]) + '\n' + str(userresponse["credit"])
        embed = discord.Embed(title="F@H " + userresponse["name"], color=0xA9152B)
        embed.add_field(name="Stats", value=stats_name_message, inline=True)
        embed.add_field(name="Value", value=stats_message, inline=True)
        embed.set_footer(text="Folding@Home API updates once or twice a day.")
        await ctx.send(embed=embed)
        return
    
    @commands.command(name="user", aliases=["User"])
    async def guild_user(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Usage: `-user [@user]`")
            return
        embed = discord.Embed(title=f"{user}'s Information", color = 0xA9152B)
        embed.add_field(name="Date User Created Account", value=user.created_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name="Date User Joined the Server", value=user.joined_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name="User's ID", value = user.id, inline=False)
        await ctx.send(embed=embed)


    @tasks.loop(minutes=1.0)
    async def theserverTime(self):
        try:
            fmt = "%H:%M %Z"
            servertime = self.bot.get_channel(id=servertimechannel)
            berlin = datetime.now(timezone("CET"))
            berlin = berlin.strftime(fmt)
            await servertime.edit(name=berlin)
        except:
            logger.exception("Server Time Error")
    
    @theserverTime.before_loop
    async def before_theserverTime(self):
        minutecheck = datetime.now(timezone("CET"))
        fmt2 = "%s"
        minutecheck = int(minutecheck.strftime(fmt2))
        minutecheck = 61 - (minutecheck % 60)
        await asyncio.sleep(minutecheck)

def setup(bot):
    bot.add_cog(Misc(bot))