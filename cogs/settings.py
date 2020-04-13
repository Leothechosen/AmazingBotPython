import discord
import database
import logging
import pytz
from discord.ext import commands

logger = logging.getLogger(f"AmazingBot.{__name__}")

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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

def setup(bot):
    bot.add_cog(Settings(bot))