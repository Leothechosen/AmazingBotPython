import discord
import aiohttp
import asyncio
import os
import sqlite3
import sys
import importlib
sys.path.append('../database')
import database as db
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
leagueapikey = os.getenv('LEAGUE_API_KEY')

class Predictions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.loop.create_task(db.checkDB())
	
	@commands.command(name = "refreshcache")
	@commands.is_owner()
	async def refreshcache(self, ctx):
		importlib.reload(db)
		await ctx.send("DB Cache refreshed")
		
	@commands.group(pass_context=True, aliases = ["Prediction"])
	async def prediction(self, ctx):
		if ctx.invoked_subcommand == None:
			#await ctx.send("Work in progress")
			await db.checkdiscord(ctx)
	
	@prediction.command(name = "pick")
	async def pick(self, ctx):
		reaction = []
		embed = discord.Embed(title = "Pick testings", color = 0xa9152b)
		embed.add_field(name = "Make your choice", value = "1 or 2?", inline=False)
		msg = await ctx.send(embed=embed)
		await discord.Message.add_reaction(msg, '1️⃣')
		await discord.Message.add_reaction(msg, '2️⃣')
		def check(reaction, message, user):
			return user == ctx.author and (str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '1️⃣') and reaction.message == msg
		try:
			reaction, user = await commands.Bot.wait_for(self, event = 'reaction_add', timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send('Timeout')
		else:
			await ctx.send('Good?')
			
	@prediction.command(name = "update")
	@commands.is_owner()
	async def update(self, ctx):
		await db.updatematch(ctx)

	

async def test():
	print("test")
	
def setup(bot): 
	bot.add_cog(Predictions(bot))
