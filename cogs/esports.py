import discord
import aiohttp
import asyncio
import os
import re
import math
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
		embed = discord.Embed(title = tournament.upper() + " Standings", color=0xa9152b)
		ordinal_message = ""
		teams_message = ""
		records_message = ""
		tournamentId = await getTournamentId(self, tournament)
		if tournamentId == "Invalid League":
			await ctx.send("League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		async with aiohttp.ClientSession() as session:
			headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getStandings?hl=en-US&tournamentId=" + tournamentId, headers=headers) as response:
				standings_response = await response.json()
				rankings = (standings_response["data"]["standings"][0]["stages"][0]["sections"][0]["rankings"])
				for x in range(len(rankings)):
					ordinal = str(rankings[x]['ordinal'])
					def integerPrefix(ordinal):
						switcher = {
							"1":"1st",
							"2":"2nd",
							"3":"3rd",
							"4":"4th",
							"5":"5th",
							"6":"6th",
							"7":"7th",
							"8":"8th",
							"9":"9th",
							"10":"10th"
							}
						return switcher.get(ordinal, "???")
					ordinal = integerPrefix(ordinal)
					for y in range(len(rankings[x]["teams"])):
						ordinal_message += (ordinal + '\n')
				embed.add_field(name="Place", value=ordinal_message, inline=True)
				for x in range(len(rankings)):
					for y in range(len(rankings[x]["teams"])):
						teams_message += str(rankings[x]["teams"][y]["name"]) + '\n'
				embed.add_field(name="Team", value=teams_message, inline=True)
				for x in range(len(rankings)):
					for y in range(len(rankings[x]["teams"])):
						records_message += str(rankings[x]["teams"][y]["record"]["wins"]) + "-" + str(rankings[x]["teams"][y]["record"]["losses"]) + '\n'
				embed.add_field(name="Record", value=records_message, inline=True)
			await session.close()
		await ctx.send(embed=embed)

	@esports.command(pass_context=True)
	async def schedule(self, ctx, league = None, team = None):
		schedule_message = ""
		teams1_message = ""
		teams2_message = ""
		opponent_message = ""
		thumbnail = ""
		next_4_matches = 0
		if league == None:
			await ctx.send("Usage: `-esports schedule [league] (Optional: [team abbreviation])`. Supported leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		league = await sanitizeinput(self, league)
		if team == None:
			embed = discord.Embed(title = league.upper() + " Schedule (Next 7 days)", color=0xa9152b)
		else:
			embed = discord.Embed(title = team.upper() + "'s Schedule (Next 4 Matches)", color=0xa9152b)
		league = await getLeagueId(self, league)
		if league == "Invalid League":
			await ctx.send("League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)")
			return
		async with aiohttp.ClientSession() as session:
			headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US&leagueId=" + league, headers=headers) as response:
				schedule_response = await response.json()
				await session.close()
				currenttime = datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S")
				currenttime = datetime.strptime(currenttime, "%Y-%m-%d %H:%M:%S")
				scheduled_matches = schedule_response["data"]["schedule"]["events"]
				for x in range(len(scheduled_matches)):
					if scheduled_matches[x]["state"] == "unstarted":
						if team == None:
							starttime = re.sub('[T]', " ", scheduled_matches[x]["startTime"])
							starttime = re.sub('[Z]', "", starttime)
							starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
							if currenttime + timedelta(days=7) > starttime:
								days, hours, minutes = await days_hours_minutes(starttime - currenttime)
								remainingtime = await timeformatting(days, hours, minutes)
								schedule_message += remainingtime
								teams1_message += "**" + scheduled_matches[x]["match"]["teams"][0]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][0]["record"]["losses"]) + ")" + "**\n"
								teams2_message += "**" + scheduled_matches[x]["match"]["teams"][1]["name"] + " (" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["wins"]) + "-" + str(scheduled_matches[x]["match"]["teams"][1]["record"]["losses"]) + ")" + "**\n"
						else:
							if next_4_matches != 4:
								if scheduled_matches[x]["match"]["teams"][0]["code"] == team or scheduled_matches[x]["match"]["teams"][1]["code"] == team:
									starttime = re.sub('[T]', " ", scheduled_matches[x]["startTime"])
									starttime = re.sub('[Z]', "", starttime)
									starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
									days, hours, minutes = await days_hours_minutes(starttime - currenttime)
									remainingtime = await timeformatting(days, hours, minutes)
									schedule_message += remainingtime
									if scheduled_matches[x]["match"]["teams"][0]["code"] == team:
										opponent_message += scheduled_matches[x]["match"]["teams"][1]["name"] + '\n'
										thumbnail = scheduled_matches[x]["match"]["teams"][0]["image"]
									else:
										opponent_message += scheduled_matches[x]["match"]["teams"][0]["name"] + '\n'
										thumbnail = scheduled_matches[x]["match"]["teams"][1]["image"]	
									next_4_matches += 1
				if schedule_message == "":
					await ctx.send("Team could not be found.")
					return
				embed.add_field(name = "Time Remaining", value = schedule_message, inline = True)
				if team == None:
					embed.add_field(name = "Team 1", value = teams1_message, inline = True)
					embed.add_field(name = "Team 2", value = teams2_message, inline = True)
				else:
					embed.add_field(name = "Opponent", value = opponent_message, inline = True)
				embed.set_thumbnail(url=thumbnail)
			await ctx.send(embed=embed)
		
	@esports.command(pass_context=True)
	async def team(self, ctx, team = None):
		role_message = ""
		name_message = ""
		if team == None:
			await ctx.send("Usage: `-esports team [team]. Example: -esports team TSM`. If the team has spaces, replace the spaces with dashes. For example: Counter-Logic-Gaming")
			return
		team = await sanitizeinput(team)
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
	
async def getTournamentId(self, tournament):
	tournament = tournament.upper()
	switcher = {
		"LCS":"103462439438682788",
		"LEC":"103462459318635408",
		"LCK":"103540363364808496",
		"LPL":"103462420723438502",
		"OPL":"103535401218775284",	
		"CBLOL":"103478354329449186",
		"TCL":"103495775740097550",
		"LJL":"103540397353089204",
		"LCSA":"103462454280724883"
			}
	return switcher.get(tournament, "Invalid League")
	
async def getLeagueId(self, league):
	league = league.upper()
	switcher = {
		"EUM":"100695891328981122",
		"TAL":"101097443346691685",
		"LLA":"101382741235120470",
		"WORLDS":"98767975604431411",
		"ALL-STARS":"98767991295297326",
		"LCS":"98767991299243165",
		"LEC":"98767991302996019",
		"LCK":"98767991310872058",
		"LPL":"98767991314006698",
		"MSI":"98767991325878492",
		"OPL":"98767991331560952",
		"CBLOL":"98767991332355509",
		"TCL":"98767991343597634",
		"NAC":"98767991349120232",
		"LCSA":"99332500638116286",
		"LJL":"98767991349978712"
			}
	return switcher.get(league, "Invalid League")
	
async def timeformatting(days, hours, minutes):
	if days == "0":
		if hours == "0":
			if minutes == "0":
				remainingtime = ("Starting soon!\n")
			elif minutes == "1":
				remainingtime = (minutes + " minute\n")
			else:
				remainingtime = (minutes + " minutes\n")
		if hours == "1":
			if minutes == "0":
				remainingtime = (hours + " hour\n")
			elif minutes == "1":
				remainingtime = (hours + " hour, " + minutes + " minute\n")
			else:
				remainingtime = (hours + " hour, " + minutes + " minutes\n")
		else:
			if minutes == "0":
				remainingtime = (hours + " hours\n")
			elif minutes == "1":
				remainingtime = (hours + " hours, " + minutes + " minute\n")
			else:
				remainingtime = (hours + " hours, " + minutes + " minutes\n")
	elif days == "1":
		if hours == "0":
			if minutes == "0":
				remainingtime = (days + " day\n")
			elif minutes == "1":
				remainingtime = (days + " day, " + minutes + " minute\n")
			else:
				remainingtime = (days + " day, " + minutes + " minutes\n")
		if hours == "1":
			if minutes == "0":
				remainingtime = (days + " day, " + hours + " hour\n")
			elif minutes == "1":
				remainingtime = (days + " day, " + hours + " hour\n")
			else:
				remainingtime = (days + " day, " + hours + " hour\n")
		else:
			if minutes == "0":
				remainingtime = (days + " day, " + hours + " hours\n")
			elif minutes == "1":
				remainingtime = (days + " day, " + hours + " hours\n")
			else:
				remainingtime = (days + " day, " + hours + " hours\n")
	else:
		if hours == "0":
			if minutes == "0":
				remainingtime = (days + " days\n")
			elif minutes == "1":
				remainingtime = (days + " days, " + minutes + " minute\n")
			else:
				remainingtime = (days + " days, " + minutes + " minutes\n")
		if hours == "1":
			if minutes == "0":
				remainingtime = (days + " days, " + hours + " hour\n")
			elif minutes == "1":
				remainingtime = (days + " days, " + hours + " hour\n")
			else:
				remainingtime = (days + " days, " + hours + " hour\n")
		else:
			if minutes == "0":
				remainingtime = (days + " days, " + hours + " hours\n")
			elif minutes == "1":
				remainingtime = (days + " days, " + hours + " hours\n")
			else:
				remainingtime = (days + " days, " + hours + " hours\n")
	return remainingtime
	
async def sanitizeinput(self, inputs):
	return re.sub(r'[^a-zA-Z0-9-]', "", inputs)
async def days_hours_minutes(td):
	return str(td.days), str(td.seconds//3600), str((td.seconds//60)%60)
def setup(bot):
	bot.add_cog(eSports(bot))
