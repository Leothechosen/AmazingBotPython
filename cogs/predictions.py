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
			await db.checkdiscord(ctx)
	
	@prediction.command(name = "pick")
	async def pick(self, ctx):
		conn = sqlite3.connect('Predictions.db')
		c = conn.cursor()
		await db.checkdiscord(ctx)
		leagues_message = ""
		end_message = ""
		original_user = ctx.author.id
		reaction_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
		leagues_list = ["LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
		for x in range(len(reaction_list))	:
			leagues_message += (str(x+1) + ": " + leagues_list[x] + '\n')
		embed = discord.Embed(title = "Predictions: League", color = 0xa9152b)
		embed.add_field(name = "Which League would you like to predict?", value = leagues_message, inline=False)
		msg = await ctx.send(embed=embed)
		for x in range(len(reaction_list)):
			await discord.Message.add_reaction(msg, reaction_list[x])	
		def check(reaction, user):
			return user.id == original_user and reaction.emoji in reaction_list
		try:
			react = await self.bot.wait_for(event = "reaction_add", timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send('Predictions have timed out. Please try again.')
		league = leagues_list[reaction_list.index(react[0].emoji)]
		c.execute("select distinct min(o.block_name) from match o where o.id_league = (select id from league where name = ?) and strftime('%Y-%m-%d %H-%M-%S', 'now') < (select min(i.start_time) from match i where i.id_league = (select id from league where name = ?) and i.block_name = o.block_name)	", (league, league))
		block_name = c.fetchone()[0]
		c.execute("SELECT * from Match WHERE id_league = (SELECT id FROM league WHERE name = ?) and block_name = ?", (league, block_name))
		matches = c.fetchall()
		for x in range(len(matches)):
			await discord.Message.clear_reactions(msg)
			c.execute("SELECT name FROM Team WHERE id = ?", (matches[x][1],))
			team_1 = c.fetchone()[0]
			c.execute("SELECT name FROM Team WHERE id = ?", (matches[x][2],))
			team_2 = c.fetchone()[0]
			embed.title = "Predictions: LCS - " + team_1 + " vs " + team_2
			embed.set_field_at(0, name = "Which team do you predict will win?", value = "1: " + team_1 +'\n2: ' + team_2)
			await discord.Message.edit(msg, embed=embed)
			await discord.Message.add_reaction(msg, reaction_list[0])
			await discord.Message.add_reaction(msg, reaction_list[1])
			try:
				react = await self.bot.	wait_for(event = "reaction_add", timeout=60.0, check=check)
			except asyncio.TimeoutError:
				await ctx.send("Predictions have timed out. Please try again.")
			if reaction_list.index(react[0].emoji) == 0:
				c.execute("INSERT OR REPLACE INTO Prediction(id_user, id_match, id_team_predicted) VALUES ((SELECT id FROM User WHERE discord_id = ?), ?, ?)", (original_user, matches[x][0], matches[x][1]))
				end_message += "**" + team_1 + "** vs " + team_2 + '\n'
			else:	
				c.execute("INSERT OR REPLACE INTO Prediction(id_user, id_match, id_team_predicted) VALUES ((SELECT id FROM User WHERE discord_id = ?), ?, ?)", (original_user, matches[x][0], matches[x][2]))
				end_message += team_1 + " vs **" + team_2 + '**\n'
		conn.commit()
		conn.close()
		embed.title = "Predictions: " + league
		embed.set_field_at(0, name = "Your Predictions", value = end_message, inline=False)
		await discord.Message.edit(msg, embed=embed)
		await discord.Message.clear_reactions(msg)
	
	@prediction.command(name = "update")
	@commands.is_owner()
	async def update(self, ctx):
		await db.updatematch(ctx)

	

async def test():
	print("test")
	
def setup(bot): 
	bot.add_cog(Predictions(bot))
