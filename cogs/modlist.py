import discord
import asyncio
from discord.ext import commands

modlist_file = "modlist.txt"


class Modlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @commands.has_role("Moderators")
    async def modlist(self, ctx):
        if ctx.invoked_subcommand is None:
            modlist = open(modlist_file, 'r')
            await ctx.send(modlist.read())
            modlist.close()
        return

    @modlist.command(pass_context=True)
    async def add(self, ctx, name=None):
        modlist = open(modlist_file, 'a')
        modlist.write(name+'\n')
        modlist.close()
        await ctx.send("Addition successful")
        return

    @modlist.command(pass_context=True)
    async def remove(self, ctx, name=None):
        modlist = open(modlist_file, 'r')
        names = modlist.readlines()
        modlist.close()
        modlist = open(modlist_file, 'w')
        for line in names:
            if line.strip() != name:
                modlist.write(line)
        modlist.close()
        return


def setup(bot):
    bot.add_cog(Modlist(bot))
