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

logger = logging.getLogger("AmazingBot." + __name__)
load_dotenv()
amazingserverid = int(os.getenv("AMAZING_SERVER_ID"))
servertimechannel = int(os.getenv("SERVER_TIME_CHANNEL"))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.theserverTime.start() # pylint: disable=no-member

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
    
    @commands.group()
    async def fah(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are team and user. See pinned message for usage.")
        return
    
    @fah.command()
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
    
    @fah.command()
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
    
    @commands.command(name="bugreport", aliases=["bug"])    
    async def bug_report(self, ctx, *args):
        if args == ():
            await ctx.send("Usage: `-bugreport [message]`")
            return
        owner = self.bot.get_user(self.bot.owner_id)
        if ctx.guild == None:
            await owner.send(f"Error reported by {ctx.author} in a DM: {ctx.message.content}")
        else:
            await owner.send(f"Error reported by {ctx.author} in {ctx.guild}: {ctx.message.content}")
        await ctx.send("Your report has been sent, thank you.")
    
    @commands.command(name="suggestion")
    async def suggestion(self, ctx, *args):
        if args == ():
            await ctx.send("Usage: `-suggestion [message]`")
            return
        owner = self.bot.get_user(self.bot.owner_id)
        if ctx.guild == None:
            await owner.send(f"Suggestion from {ctx.author} in a DM: {ctx.message.content}")
        else:
            await owner.send(f"Suggestion by {ctx.author} in {ctx.guild}: {ctx.message.content}")
        await ctx.send("Your suggestion has been sent, thank you.")

    @commands.command(name="status")
    @commands.is_owner()
    async def status(self, ctx, status=None):
        if status == None:
            await self.bot.change_presence(activity=None)
        elif status == "default":
            await self.bot.change_presence(activity=discord.Game("Created by Leo"))
        else:
            await self.bot.change_presence(activity=discord.Game(status))
        return

    @commands.command(name="botinfo")
    async def botinfo(self, ctx):
        embed = discord.Embed(title="AmazingBot Info", color=0xA9152B)
        embed.add_field(name="Uptime", value= str(datetime.now() - self.bot.uptimeStart)[:-7], inline = True)
        embed.add_field(name="Created On", value = "2019-12-28", inline=True)
        embed.add_field(name="** **", value = "** **", inline=True)
        embed.add_field(name="Guilds Serving", value = len(self.bot.guilds), inline=True)
        embed.add_field(name="Users Serving", value = len(self.bot.users), inline=True)
        embed.add_field(name="** **", value = "** **", inline=True)
        embed.add_field(name="Bot Invite Link", value="https://discordapp.com/api/oauth2/authorize?client_id=660329366940680227&permissions=8&scope=bot", inline=True)
        embed.set_footer(text="Created By Leo឵#8788", icon_url="https://i.imgur.com/SGmbIdj.png")
        embed.set_thumbnail(url="https://i.imgur.com/TwEsQ4D.png")
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        features = [f'{feature}\n' for feature in ctx.guild.features]
        logger.info(ctx.guild.icon)
        prefix = await database.getGuildPrefix(ctx.guild.id)
        embed = discord.Embed(title=f"{ctx.guild.name}'s Info", description=f"Server prefix: {prefix[0]}", color = 0xA9152B)
        embed.add_field(name="Region", value=str(ctx.guild.region).title(), inline=True)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(name="Created On", value=str(ctx.guild.created_at)[:-7], inline=True)
        embed.add_field(name="Features", value = f"{features}", inline=True)
        embed.add_field(name="# of Members", value=f"{ctx.guild.member_count}", inline=True)
        embed.add_field(name="# of Boosts", value=f"{ctx.guild.premium_subscription_count}", inline=True)
        try:
            if ctx.guild.is_icon_animated():    
                embed.set_thumbnail(url=ctx.guild.icon_url_as(format="gif"))
            else:
                embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
        except:
            pass
        await ctx.send(embed=embed)


    @commands.command(name="help")
    async def help(self, ctx, subclass=None):
        await ctx.send("""```
-league
    rank [summoner_name] [server]
    profile [summoner_name] [server]
    match [summoner_name] [server]
    clash [summoner_name] [server]
-lor
    leaderboard [lor_region]
-esports
    standings [league]
    team [team]
    schedule [league or team]
-prediction
    pick
    view
    record
    leaderboard
-fah (Folding@Home)
    team [team_id]
    user [user_name or user_id]
-poll [question], [answer1], [answer2], ..., [answer9], [time_in_seconds (Max: 300)]
-temp [temperatureF/C/K]
-8ball
-avatar
-sourcecode or github
-bugreport [message]
-suggestion [message]
-botinfo
-serverinfo

Admin only commands: 
-servertime [channel_id] [timezone] (Set a channel to display the server's local timezone via channel name)
-prefix [new_prefix] (Set a new prefix for the bot to respond to) ```""")

    @commands.command(name="servertime")
    @commands.has_guild_permissions(administrator=True)
    async def servertime(self, ctx, channel_id=None, timezone=None):
        if channel_id == None and timezone == None:
            await ctx.send("To set a channel to display Server Time: `-servertime [channel_id] [timezone]`\nTo delete your Server Time settings: `-servertime delete`\nValid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568")
        elif channel_id == "delete":
            await database.writeGuildSettings(ctx.guild.id, None, None)
            await ctx.send("Your settings have been deleted. To set them again, do `-servertime [channel_id] [timezone]`")
        elif timezone == None:
            await ctx.send("You must specify a timezone. See here for valid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568")
        elif timezone not in pytz.all_timezones:
            await ctx.send("You have entered an invalid timezone. See here for valid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568")
        else:
            channel_for_servertime = self.bot.get_channel(id=int(channel_id))
            if channel_for_servertime is not None:
                await database.writeGuildSettings(ctx.guild.id, channel_id, timezone)
                await ctx.send("Settings saved.")
            else:
                await ctx.send("The id provided is not valid. Check the desired channel's ID again.")
        return

    @commands.command(name="prefix")
    @commands.has_guild_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix = None):
        if new_prefix is None:
            await ctx.send("Usage: `-prefix [new_prefix]`")
            return
        await database.writeGuildPrefix(ctx.guild.id, new_prefix)
        await ctx.send(f"Setting saved. Your new prefix is {new_prefix}")
        return

    @tasks.loop(minutes=1.0)
    async def theserverTime(self):
        allGuildSettings = await database.getAllGuildSettings()
        fmt = "%H:%M %Z"
        for guild in allGuildSettings:
            try:
                if guild[1] is not None:
                    channel_for_servertime = self.bot.get_channel(id=guild[1])
                    serverTime = datetime.now(timezone(guild[2]))
                    serverTime = serverTime.strftime(fmt)
                    await channel_for_servertime.edit(name=serverTime)
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