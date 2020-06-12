# AmazingBotPython.py

import logging
import os
import discord
import database
import utils
import traceback
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

logging.basicConfig(
    filename="logging.log",
    level=logging.INFO,
    format="%(asctime)s;%(name)s;%(levelname)s;%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("AmazingBot")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
async def get_prefix(bot, message):
    prefix = await database.getGuildPrefix(message.guild.id)
    if prefix[0] is None:
        return "-"
    else:
        return prefix[0]

bot = commands.Bot(command_prefix=get_prefix, owner_id=122919363656286212)
bot.uptimeStart = datetime.now()

@bot.event
async def on_ready():
    logger.info(f"AmazingBot connected to Discord | Discord.py Version {discord.__version__}")

@bot.event
async def on_connect():
    game = discord.Game("Created By Leo")
    await bot.change_presence(activity=game)

@bot.event
async def on_command(ctx):
    logger.info(f' Message {ctx.message.content} - User: {ctx.message.author}')
    bot.startTimer = datetime.now()
    await ctx.trigger_typing()
    return

@bot.event
async def on_command_completion(ctx):
    logger.info(f"Completed in {datetime.now() - bot.startTimer}")

@bot.event
async def on_command_error(ctx, error):
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
    owner = bot.get_user(bot.owner_id)
    await owner.send(f'Error in {ctx.command}\n{error}')

@bot.event
async def on_guild_join(guild):
    logger.info(f'AmazingBot has joined "{guild.name}"" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id} | # of members: {len(guild.members)}')
    await bot.get_user(bot.owner_id).send(f'AmazingBot has joined "{guild.name}" \nGuild_ID: {guild.id}\nOwner_ID: {guild.owner_id}\n# of members: {len(guild.members)}')

@bot.event
async def on_guild_remove(guild):
    logger.info(f'AmazingBot was removed from "{guild.name}" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id}')
    await bot.get_user(bot.owner_id).send(f'AmazingBot was removed from "{guild.name}"\nGuild_ID: {guild.id}\nOwner_ID: {guild.owner_id}')

@bot.event
async def on_raw_reaction_add(payload):
    try:
        if payload.message_id != 701341554287181884:
            return
        role_reaction = await utils.role_reaction_emojis(str(payload.emoji))
        role_to_add = await utils.role_reaction_roles(str(role_reaction))
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(role_to_add)
        member = guild.get_member(payload.user_id)
        await member.add_roles(role)
    except:
        logger.exception("")
    return

@bot.event
async def on_raw_reaction_remove(payload):
    try:
        if payload.message_id != 701341554287181884:
            return
        role_reaction = await utils.role_reaction_emojis(str(payload.emoji))
        role_to_remove = await utils.role_reaction_roles(str(role_reaction))
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(role_to_remove)
        member = guild.get_member(payload.user_id)
        await member.remove_roles(role)
    except:
        logger.exception("")
    return
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    """Owner Only | Loads a cog"""
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} loaded")


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    """Owner Only | Unloads a cog"""
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} unloaded")


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    """Owner Only | Reloads a cog"""
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} reloaded")


@bot.command()
async def ping(ctx):
    """Pong"""
    await ctx.send(f"Pong ({round(bot.latency*1000)}ms)")
    return


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
