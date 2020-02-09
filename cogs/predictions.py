import discord
import aiohttp
import asyncio
import os
import sqlite3
import sys
sys.path.append('../database')
import database as db
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
leagueapikey = os.getenv('LEAGUE_API_KEY')

class Predictions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.Cog.listener()
	async def on_ready(self):
		await db.checkDB(self)
		
def setup(bot): 
	bot.add_cog(Predictions(bot))
