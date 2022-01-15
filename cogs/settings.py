import discord
import database
import logging
import pytz
from datetime import datetime
from discord.ext import commands

logger = logging.getLogger(f"AmazingBot.{__name__}")

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="servertime")
    @commands.has_guild_permissions(administrator=True)
    async def servertime(self, ctx, channel_id, timezone = None):
        """Admin only | Set a channel to keep track of the Server's given timezone | `-servertime delete` will delete the server's settings"""
        if channel_id == "delete":
            await database.writeGuildSettings(ctx.guild.id, None, None)
            await ctx.send("Your settings have been deleted. To set them again, do `-servertime [channel_id] [timezone]`")
            logger.info(f'"{ctx.guild.name}" deleted their Servertime settings.')
        elif timezone not in pytz.all_timezones:
            await ctx.send("You have entered an invalid timezone. See here for valid timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568")
        else:
            channel_for_servertime = self.bot.get_channel(id=int(channel_id))
            if channel_for_servertime is not None:
                await database.writeGuildSettings(ctx.guild.id, channel_id, timezone)
                await ctx.send(f"Settings saved.")
                logger.info(f'"{ctx.guild.name}" changed their Servertime settings. Channel: {channel_id} | Timezone {timezone}')
            else:
                await ctx.send("The id provided is not valid. Check the desired channel's ID again.")
        return

    @commands.command(name="servertimefmt", hidden=True)
    @commands.has_guild_permissions(administrator=True)
    async def servertimefmt(self, ctx, *, fmt):
        """Admin only | Sets the server's time format setting
        Examples: **%H:%M %Z** outputs to 13:25 PST | **%I:%M %p** outputs to 1:25 PM | Default is %H:%M %Z
        Valid settings: https://strftime.org/"""
        pass


    @commands.command(name="prefix")
    @commands.has_guild_permissions(administrator=True)
    async def prefix(self, ctx, new_prefix):
        """Admin only | Set the bot's prefix for this server"""
        await database.writeGuildPrefix(ctx.guild.id, new_prefix)
        await ctx.send(f"Setting saved. Your new prefix is {new_prefix}")
        logger.info(f"'{ctx.guild.name}' changed their prefix to {new_prefix}")
        return    

def setup(bot):
    bot.add_cog(Settings(bot))