# AmazingBotPython.py

import logging
import os
import discord
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
bot = commands.Bot(command_prefix="-", owner_id=122919363656286212)
bot.remove_command('help')
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
    logger.error(f'Error in {ctx.command}')
    logger.error(f'{error}')
    owner = bot.get_user(bot.owner_id)
    await owner.send(f'Error in {ctx.command}\n{error}')

@bot.event
async def on_guild_join(guild):
    logger.info(f'AmazingBot has joined "{guild.name}"" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id} | # of members: {len(guild.members)}')

@bot.event
async def on_guild_remove(guild):
    logger.info(f'AmazingBot was removed from "{guild.name}" | Guild_ID: {guild.id} | Owner_ID: {guild.owner_id}')


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} loaded")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} unloaded")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} reloaded")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong")
    return


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
