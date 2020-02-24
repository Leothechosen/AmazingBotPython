import discord
import aiohttp
import asyncio
import os
import re
import math
import utils
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv

class eSports(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.group(pass_context=True, help = "Subcommands: standings and team")	
	async def esports(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Subcommands are standings, team and schedule. See pinned message for usage.	")
		return
			
	@esports.command(pass_context=True)
	async def standings(self, ctx, tournament = None):
		if tournament == None:
			await ctx.send("Usage: `-esports standings [league]`. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		ordinal_message = ""
		teams_message = ""
		records_message = ""
		tournamentId = await utils.getTournamentId(tournament)
		if tournamentId == "Invalid League":
			await ctx.send("League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		async with aiohttp.ClientSession() as session:
			headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getStandings?hl=en-US&tournamentId=" + tournamentId, headers=headers) as response:
				standings_response = await response.json()
				await session.close()
				rankings = (standings_response["data"]["standings"][0]["stages"][0]["sections"][0]["rankings"])
				for x in range(len(rankings)):
					for y in range(len(rankings[x]["teams"])):
						ordinal = str(rankings[x]['ordinal'])
						ordinal = await utils.integerPrefix(ordinal)
						ordinal_message += (ordinal + '\n')
						teams_message += str(rankings[x]["teams"][y]["name"]) + '\n'
						records_message += str(rankings[x]["teams"][y]["record"]["wins"]) + "-" + str(rankings[x]["teams"][y]["record"]["losses"]) + '\n'
				embed = discord.Embed(title = tournament.upper() + " Standings", color=0xa9152b)
				embed.add_field(name="Place", value=ordinal_message, inline=True)
				embed.add_field(name="Team", value=teams_message, inline=True)
				embed.add_field(name="Record", value=records_message, inline=True)
		await ctx.send(embed=embed)

	@esports.command(pass_context=True)
	async def schedule(self, ctx, league = None, team = None):
		schedule_message = ""
		teams1_message = ""
		teams2_message = ""
		opponent_message = ""
		thumbnail = ""
		team_record = ""
		next_4_matches = 0
		if league is None:
			await ctx.send("Usage: `-esports schedule [league] (Optional: [team abbreviation])`. Supported leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		leaguename = await utils.sanitizeinput(league)
		if leaguename == "LPL":
			await ctx.send("Unfortunately, LPL is on hiatus due to the Coronavirus. This means that there is no schedule for the time being.")
			return
		leagueid = await utils.getLeagueId(league)
		if leagueid == "Invalid League":
			await ctx.send("League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		async with aiohttp.ClientSession() as session:
			headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US&leagueId=" + leagueid, headers=headers) as response:
				schedule_response = await response.json()
				await session.close()
				print(datetime.now())
				currenttime = datetime.utcnow()
				scheduled_matches = schedule_response["data"]["schedule"]["events"]
				for x in range(len(scheduled_matches)):
					if scheduled_matches[x]["state"] == "unstarted":
						if team is None:
							starttime = re.sub('[T]', " ", scheduled_matches[x]["startTime"])
							starttime = re.sub('[Z]', "", starttime)
							starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
							if currenttime + timedelta(days=7) > starttime:
								days, hours, minutes = await utils.days_hours_minutes(starttime - currenttime)
								remainingtime = await utils.timeformatting(days, hours, minutes)
								schedule_message += remainingtime
								if leaguename == "LCSA":
									teams1_message += "**" + scheduled_matches[x]["match"]["teams"][0]["name"][:-8] + " (" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["losses"]) + ")" + "**\n"
									teams2_message += "**" + scheduled_matches[x]["match"]["teams"][1]["name"][:-8] + " (" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["losses"]) + ")" + "**\n"
								else: 
									teams1_message += "**" + scheduled_matches[x]["match"]["teams"][0]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["losses"]) + ")" + "**\n"
									teams2_message += "**" + scheduled_matches[x]["match"]["teams"][1]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["losses"]) + ")" + "**\n"
						else:
							if next_4_matches != 4:
								if scheduled_matches[x]["match"]["teams"][0]["code"] == team or scheduled_matches[x]["match"]["teams"][1]["code"] == team:
									starttime = re.sub('[T]', " ", scheduled_matches[x]["startTime"])
									starttime = re.sub('[Z]', "", starttime)
									starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
									days, hours, minutes = await utils.days_hours_minutes(starttime - currenttime)
									remainingtime = await utils.timeformatting(days, hours, minutes)
									schedule_message += remainingtime
									if scheduled_matches[x]["match"]["teams"][0]["code"] == team:
										team_record = "(" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["losses"]) + ")"
										opponent_message += '**' + scheduled_matches[x]["match"]["teams"][1]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["losses"]) + ")**\n"
										thumbnail = scheduled_matches[x]["match"]["teams"][0]["image"]
									else:
										team_record = "(" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["losses"]) + ")"
										opponent_message += '**' + scheduled_matches[x]["match"]["teams"][0]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["losses"]) + ")**\n"
										thumbnail = scheduled_matches[x]["match"]["teams"][1]["image"]	
									next_4_matches += 1
				if schedule_message == "":
					await ctx.send("Team could not be found.")
					return
				if team == None:
					embed = discord.Embed(title = leaguename.upper() + " Schedule", color = 0xa9152b)
					embed.add_field(name = "Time Remaining", value = schedule_message, inline = True)
					embed.add_field(name = "Team 1", value = teams1_message, inline = True)
					embed.add_field(name = "Team 2", value = teams2_message, inline = True)
					embed.set_footer(text = "Next 7 Days")
				else:
					embed = discord.Embed(title = team.upper() + " " + team_record, color = 0xa9152b)
					embed.add_field(name = "Time Remaining", value = schedule_message, inline = True)
					embed.add_field(name = "Opponent", value = opponent_message, inline = True)
					embed.set_footer(text = "Next 4 Matches")
					embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)
		
	@esports.command(pass_context=True)
	async def team(self, ctx, team = None):
		role_message = ""
		name_message = ""
		if team == None:
			await ctx.send("Usage: `-esports team [team]. Example: -esports team TSM`. If the team has spaces, replace the spaces with dashes. For example: Counter-Logic-Gaming")
			return
		team = await utils.sanitizeinput(team)
		async with aiohttp.ClientSession() as session:
			headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-US&id=" + team.lower(),headers=headers) as response:
				team_response = await response.json()
				await session.close()
				if team_response["data"]["teams"] == []:
					await ctx.send("Invalid team name. If the team has spaces, replace the spaces with dashes. For example: Counter-Logic-Gaming. Otherwise, check spelling, or try an abbreviation, e.g TSM")
					return
				embed = discord.Embed(title = team.upper() + " Roster", color=0xa9152b)
				names = team_response["data"]["teams"][0]["players"]
				for x in range(len(names)):
					role_message += (names[x]['role']).title() + '\n'
				embed.add_field(name="Role", value=role_message, inline=True)
				for x in range(len(names)):
					name_message += names[x]['firstName'] + " '" + names[x]['summonerName'] + "' " + names[x]['lastName'] + '\n'
				embed.add_field(name="Name", value=name_message, inline=True)
				embed.set_thumbnail(url=team_response["data"]["teams"][0]["image"])
		await ctx.send(embed=embed)
	
def setup(bot):
	bot.add_cog(eSports(bot))
