import logging
import discord
import database
import utils
import traceback
from datetime import datetime
from discord.ext import commands

logger = logging.getLogger("AmazingBot." + __name__)

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"AmazingBot connected to Discord | Discord.py Version {discord.__version__}")

    @commands.Cog.listener()
    async def on_connect(self):
        game = discord.Game("Created By Leo")
        await self.bot.change_presence(activity=game)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info(f' Message {ctx.message.content} - User: {ctx.message.author}')
        self.bot.startTimer = datetime.now()
        await ctx.trigger_typing()
        return

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logger.info(f"Completed in {datetime.now() - self.bot.startTimer}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("You do not have the proper Permissions to use this command.")
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"You are missing required parameters. Use `-help {ctx.invoked_with}` to check what is required.")
            return
        logger.error(f"Error in {ctx.command}\n{error}")
        logger.error("".join(traceback.format_tb(error.original.__traceback__)))
        owner = self.bot.get_user(self.bot.owner_id)
        await owner.send(f'Error in {ctx.command}\n{error}')
        await ctx.send("Sorry, but there has been an error on processing this command. A notification has been sent to Leo")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        logger.info(f'AmazingBot has joined "{guild.name}"" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id} | # of members: {len(guild.members)}')
        await self.bot.get_user(self.bot.owner_id).send(f'AmazingBot has joined "{guild.name}" \nGuild_ID: {guild.id}\nOwner_ID: {guild.owner_id}\n# of members: {len(guild.members)}')
        await database.writeGuildPrefix(guild.id, "-")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger.info(f'AmazingBot was removed from "{guild.name}" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id}')
        await self.bot.get_user(self.bot.owner_id).send(f'AmazingBot was removed from "{guild.name}"\nGuild_ID: {guild.id}\nOwner_ID: {guild.owner_id}')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            if payload.message_id != 701341554287181884:
                return
            role_reaction = await utils.role_reaction_emojis(str(payload.emoji))
            role_to_add = await utils.role_reaction_roles(str(role_reaction))
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_to_add)
            member = guild.get_member(payload.user_id)
            await member.add_roles(role)
        except:
            logger.exception("")
        return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        try:
            if payload.message_id != 701341554287181884:
                return
            role_reaction = await utils.role_reaction_emojis(str(payload.emoji))
            role_to_remove = await utils.role_reaction_roles(str(role_reaction))
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_to_remove)
            member = guild.get_member(payload.user_id)
            await member.remove_roles(role)
        except:
            logger.exception("")
        return

    @commands.command()
    async def ping(self, ctx):
        """Pong"""
        await ctx.send(f"Pong ({round(self.bot.latency*1000)}ms)")
        return

def setup(bot):
    bot.add_cog(Owner(bot))