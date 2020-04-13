# AmazingBotPython.py

import logging
import os
import discord
import database
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
    if prefix is None:
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
    await ctx.trigger_typing()
    return

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
    logger.exception(f"Error in {ctx.command}")
    owner = bot.get_user(bot.owner_id)
    await owner.send(f'Error in {ctx.command}\n{error}')

@bot.event
async def on_guild_join(guild):
    logger.info(f'AmazingBot has joined "{guild.name}"" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id} | # of members: {len(guild.members)}')

@bot.event
async def on_guild_remove(guild):
    logger.info(f'AmazingBot was removed from "{guild.name}" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id}')


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
    await ctx.send("Pong")
    return


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
