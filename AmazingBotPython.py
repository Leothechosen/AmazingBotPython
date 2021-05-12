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
async def get_prefix(bot, message):
    try:
        prefix = await database.getGuildPrefix(message.guild.id)
        if prefix[0] is None:
            return "-"
        else:
            return prefix[0]
    except:
        return "-"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, owner_id=122919363656286212, intents=intents)
bot.uptimeStart = datetime.now()

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

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
