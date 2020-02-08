import discord
import aiohttp
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
leagueapikey = os.getenv('LEAGUE_API_KEY')

class League(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.group(pass_context=True, aliases = ["League"])
	async def league(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send("Subcommands are rank")
		return
	
	@league.command(pass_context=True, aliases = ["Rank"])
	async def rank(self, ctx, name = None, region = None):
		if name == None:
			await ctx.send("Usage: `-league rank [Summoner_name][region]`. Valid regions are: RU, KR, BR, OCE, JP, NA, EUNE, EUW, TR, LAN, and LAS.")
			return
		if region == None:
			await ctx.send("You did not specify a region")
			return
		embed = discord.Embed(title = name + "'s Ranks in " + region, color=0xa9152b)	
		region = region.upper()
		region = region_to_valid_region(region)
		if region == "Invalid Region":
			await ctx.send("The server you entered is invalid, or it's a Garena server")
		else:
			async with aiohttp.ClientSession() as session:
				async with session.get("https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + leagueapikey) as response:
					if response.status != 200:
						await ctx.send("Riot API returned a bad request. Check for errors in your request, or tell Leo to reset his API key.")
						return;
					summoneridrequest = await response.json()
					summonerid = summoneridrequest['id']
				async with session.get("https://" + region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerid + "?api_key=" + leagueapikey) as response:
					rankedrequest = await response.json()
				#async with session.get("https://" + region + ".api.riotgames.com/tft/league/v1/entries/by-summoner/" + summonerid + "?api_key=" + apikey) as response:
					#tftrequest = await response.json()
				await session.close()
				if rankedrequest != []:
						for x in range(len(rankedrequest)):
							if rankedrequest[x]["queueType"] == "RANKED_SOLO_5x5":
								message = ""
								message += (rankedrequest[x]["tier"] + " " + rankedrequest[x]["rank"] + " " + str(rankedrequest[x]["leaguePoints"]) + "LP ")
								if "miniSeries" in rankedrequest[x]:
									message += ("| Promo: ")
									for y in range(len(rankedrequest[x]["miniSeries"]["progress"])):
										if rankedrequest[x]["miniSeries"]["progress"][y] == 'W':
											message += (":white_check_mark:")
										elif rankedrequest[x]["miniSeries"]["progress"][y] == "N":
											message += (":grey_question:")
										elif rankedrequest[x]["miniSeries"]["progress"][y] == "L":
											message += (":x:")
								embed.add_field(name="Solo", value=message, inline=False)
							elif rankedrequest[x]["queueType"] == "RANKED_FLEX_SR":
								message = (rankedrequest[x]["tier"] + " " + rankedrequest[x]["rank"] + " " + str(rankedrequest[x]["leaguePoints"]) + "LP ")
								if "miniSeries" in rankedrequest[x]:
									message += ("| Promo: ")
									for y in range(len(rankedrequest[x]["miniSeries"]["progress"])):
										if rankedrequest[x]["miniSeries"]["progress"][y] == 'W':
											message += (":white_check_mark:")
										elif rankedrequest[x]["miniSeries"]["progress"][y] == "N":
											message += (":grey_question:")
										elif rankedrequest[x]["miniSeries"]["progress"][y] == "L":
											message += (":x:")
								embed.add_field(name="Flex", value=message, inline=False)
							else:
								continue
				#if tftrequest != []:
					#embed.add_field(name="TFT", value=tftrequest[0]["tier"] + " " + tftrequest[0]["rank"] + " " + str(tftrequest[0]["leaguePoints"]) + "LP",inline=True)
				if rankedrequest == []: #and tftrequest == []:
					embed.add_field(name="Unranked", value=name + " is unranked in all queues")
			await ctx.send(embed=embed)

	@league.command(pass_context=True, aliases = ["Profile"])
	async def profile(self, ctx, name = None, region = None):
		if name == None:
			await ctx.send("Usage: `-league profile [Summoner_name] [region]`. Valid regions are: RU, KR, BR, OCE, JP, NA, EUNE, EUW, TR, LAN, and LAS.")
			return
		if region == None:
			await ctx.send("You did not specify a region")
			return
		region = region.upper()
		region = region_to_valid_region(region)
		embed = discord.Embed(title = name + "Profile on " + region, color=0xa9152b)
		async with aiohttp.ClientSession() as session:
			async with session.get("https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + leagueapikey) as response:
				if response.status != 200:
					await ctx.send("Riot API returned a" + response.status)
				summonderidrequest = await response.json()
				embed.set_thumbnail(url=summonerid)
				accountid = summoneridrequest['accountId']
				summonerlevel = summoneridrequest['summonerLevel']
				summonerid = summoneridrequest['id']
		return
				
	
def region_to_valid_region(region: str):
	switcher = {
		'RU':'RU',
		'KR':'KR',
		'BR':'BR1',
		'OCE':'OC1',
		'JP':'JP1',
		'NA':'NA1',
		'EUNE':'EUN1',
		'EUW':'EUW1',
		'TR':'TR1',
		'LAN':'LA1',
		'LAS':'LA2'
			}
	return switcher.get(region, "Invalid Region")	
def setup(bot):
	bot.add_cog(League(bot))
