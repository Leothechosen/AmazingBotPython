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
		await db.checkdiscord(ctx)
		if ctx.invoked_subcommand == None:
			await ctx.send("Work in progress")
		return
	
	@prediction.command(name = "pick")
	async def pick(self, ctx):
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
			return user.id == original_user and reaction.emoji in reaction_list and reaction.message.id == msg.id
		try:
			react = await self.bot.wait_for(event = "reaction_add", timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await ctx.send('Predictions have timed out. Please try again.')
		league = leagues_list[reaction_list.index(react[0].emoji)]
		block_name, matches = await db.get_next_block_and_matches(league)
		for x in range(len(matches)):
			await discord.Message.clear_reactions(msg)
			team_1, team_2 = await db.fetchTeamIds(matches[x][1], matches[x][2])
			embed.title = "Predictions: " + league + " " + block_name + " - " + team_1 + " vs " + team_2
			embed.set_field_at(0, name = "Which team do you predict will win?", value = "1: " + team_1 +'\n2: ' + team_2)
			await discord.Message.edit(msg, embed=embed)
			await discord.Message.add_reaction(msg, reaction_list[0])
			await discord.Message.add_reaction(msg, reaction_list[1])
			try:
				react = await self.bot.wait_for(event = "reaction_add", timeout=60.0, check=check)
			except asyncio.TimeoutError:
				embed.set_field_at(0, name = "Timeout", value = "Predictions have timed out. Please try again", inline=False)
				await discord.Message.edit(msg, embed=embed)
				await discord.Message.clear_reactions(msg)
				await ctx.send("Predictions have timed out. Please try again")
			if reaction_list.index(react[0].emoji) == 0:
				await db.writePredictions(team_1, matches[x][0], original_user) 
				end_message += "**" + team_1 + "** vs " + team_2 + '\n'
			else:
				await db.writePredictions(team_2, matches[x][0], original_user)
				end_message += team_1 + " vs **" + team_2 + '**\n'
		embed.title = "Predictions: " + league + " " + block_name
		embed.set_field_at(0, name = "Your Predictions", value = end_message, inline=False)
		await discord.Message.edit(msg, embed=embed)
		await discord.Message.clear_reactions(msg)
	
	@prediction.command(name = "view")
	async def view(self, ctx):
		original_user = ctx.author.id
		leagues_message = ""
		leagues_list = ["LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
		reaction_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
		leagues_predicted_array = []
		leagues_predicted = db.fetchLeaguesPredicted(original_user)
		if range(len(leagues_predicted)) == 0:
			await ctx.send("You have not made any predictions this week.")
			return
		for x in range(len(leagues_predicted)):
			leagues_predicted_array.append(leagues_list[leagues_predicted[x][0]])
		for x in range(len(leagues_predicted_array)):
			leagues_message += leagues_predicted_array[x]
		embed = discord.Embed(title = "View predictions", color = 0xa9152b)
		embed.add_field(name = "Which league would you like to view your predictions in?", value = leagues_message, inline=False)
		msg = await ctx.send(embed=embed)
		for x in range(len(leagues_predicted_array)):
			await discord.Message.add_reaction(msg, reaction_list[x])
		def check(reaction, user):
			return user.id == original_user and reaction.emoji in reaction_list and reaction.message.id == msg.id
		try:
			react = await self.bot.wait_for(event = "reaction_add", timeout=60.0, check=check)
		except asyncio.TimeoutError:
			embed.set_field_at(0, name = "Timeout", value = "Predictions have timed out. Please try again", inline=False)
			await discord.Message.edit(msg, embed=embed)
			await discord.Message.clear_reactions(msg)
			await ctx.send("Predictions have timed out. Please try again")
		league = leagues_list[reaction_list.index(react[0].emoji)]
		
		
	@prediction.command(name = "record")
	async def record(self, ctx):
		original_user = ctx.author.id
		record_message = ""
		leagues_message = ""
		leagues_list = ["Overall", "LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
		reaction_list = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
		for x in range(len(reaction_list)):
			leagues_message += str(x) + ": " + leagues_list[x] + '\n'
		embed = discord.Embed(title = "Prediction Record" , color = 0xa9152b)
		embed.add_field(name = "Which League would you like to view your record in?", value = leagues_message, inline=False)
		msg = await ctx.send(embed=embed)
		for x in range(len(reaction_list)):
			await discord.Message.add_reaction(msg, reaction_list[x])
		def check(reaction, user):
			return user.id == original_user and reaction.emoji in reaction_list and reaction.message.id == msg.id
		try: 
			react = await self.bot.wait_for(event = "reaction_add", timeout=60.0, check=check)
		except asyncio.TimeoutError:
			embed.set_field_at(0, name = "Timeout", value = "Predictions have timed out. Please try again", inline=False)
			await discord.Message.edit(msg, embed=embed)
			await discord.Message.clear_reactions(msg)
			await ctx.send("Predictions have timed out. Please try again")
		league = leagues_list[reaction_list.index(react[0].emoji)]
		block_name_msg, correct_pred_msg, wrong_pred_msg = await db.fetchCorrect(league, original_user)
		embed.title = "Prediction Record - " + league
		embed.set_field_at(0, name = "Block", value = block_name_msg, inline = True)
		embed.add_field(name = "Correct", value = correct_pred_msg, inline = True)
		embed.add_field(name = "Incorrect", value = wrong_pred_msg, inline = True)
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
