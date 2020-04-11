import discord
import asyncio
from discord.ext import commands

modlist_file = "modlist.txt"
import logging

logger = logging.getLogger("AmazingBot." + __name__)


class Modding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @commands.has_role("Moderators")
    async def modlist(self, ctx):
        if ctx.invoked_subcommand is None:
            modlist = open(modlist_file, "r")
            await ctx.send(modlist.read())
            modlist.close()
        return

    @modlist.command(pass_context=True)
    async def add(self, ctx, name=None):
        modlist = open(modlist_file, "a")
        modlist.write(name + "\n")
        modlist.close()
        await ctx.send("Addition successful")
        return

    @modlist.command(pass_context=True)
    async def remove(self, ctx, name=None):
        modlist = open(modlist_file, "r")
        names = modlist.readlines()
        modlist.close()
        modlist = open(modlist_file, "w")
        for line in names:
            if line.strip() != name:
                modlist.write(line)
        modlist.close()
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
        
def setup(bot):
    bot.add_cog(Modding(bot))
