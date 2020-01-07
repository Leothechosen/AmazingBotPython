# AmazingBotPython.py | Note to self: learn aiohttp

import os
import random
from dotenv import load_dotenv
from discord.ext import commands
import requests
import pprint
import time
from datetime import datetime
import threading
import discord
from pytz import timezone
import asyncio
import aiohttp

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('LEO_TEST_SERVER_NAME')
apikey = os.getenv('RIOT_API_KEY')
twitchtoken = os.getenv('TWITCH_API_KEY')
amazing = os.getenv('AMAZING_CHANNEL')
leo = os.getenv('LEO_CHANNEL')
leotext = os.getenv('LEO_TEST_TEXT')
leovoice = os.getenv('LEO_TEST_VOICE')
timechannel = os.getenv('SERVER_TIME_CHANNEL')
amazingserver = os.getenv('AMAZING_SERVER_NAME')
leoserver = os.getenv('LEO_TEST_SERVER_NAME')


bot = commands.Bot(command_prefix='-')
servertimechannel = None
announcementchannel = None

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord')
	await theserverTime()
	
@bot.event
async def on_connect():
	await amazingLive()

@bot.command(name='rank', help = "-rank [Summoner_Name] [region] will return your rank")
async def rank(ctx, name: str, region: str):
	message = ""
	region = region.upper()
	def region_to_valid_region(region: str):
		switcher = {
			'RU':'RU',
			'KR':'KR',
			'BR':'BR1',
			'OC':'OC1',
			'JP':'JP1',
			'NA':'NA1',
			'EUNE':'EUN1',
			'EUW':'EUW1',
			'TR':'TR1',
			'LAN':'LA1',
			'LAS':'LA2'
				}
		return switcher.get(region, "Invalid Region")
	region = region_to_valid_region(region)
	if region == "Invalid Region":
		ctx.send("The server you entered is invalid, or it's a Garena server")
	else:
		message = ""				
		async with aiohttp.ClientSession() as session0:
			async with session0.get("https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + apikey) as response:
				summoneridrequest = await response.json()
				summonerid = summoneridrequest['id']
				await session0.close()
		async with aiohttp.ClientSession() as session1:
			async with session1.get("https://" + region + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerid + "?api_key=" + apikey) as response:
				rankedrequest = await response.json()
				await session1.close()
		if rankedrequest != []:
			for x in range(len(rankedrequest)):
				if rankedrequest[x]["queueType"] == "RANKED_SOLO_5x5":
					message += (rankedrequest[x]["tier"] + " " + rankedrequest[x]["rank"] + " " + str(rankedrequest[x]["leaguePoints"]) + "LP in Ranked Solo\n")
				elif rankedrequest[x]["queueType"] == "RANKED_FLEX_SR":
					message += (rankedrequest[x]["tier"] + " " + rankedrequest[x]["rank"] + " " + str(rankedrequest[x]["leaguePoints"]) + "LP in Ranked Flex\n")
				else:
					continue
		async with aiohttp.ClientSession() as session2:
			async with session2.get("https://" + region + ".api.riotgames.com/tft/league/v1/entries/by-summoner/" + summonerid + "?api_key=" + apikey) as response:
				tftrequest = await response.json()
				await session2.close()
		if tftrequest != []:
				message += (tftrequest[0]["tier"] + " " + tftrequest[0]["rank"] + " " + str(tftrequest[0]["leaguePoints"]) + "LP in Ranked TFT")
		await ctx.send(name + "\n" + message)

@bot.command(name='register', help = "-register [Summoner_Name] [Region] will allow you to just type -rank in the future to get your rank.")
async def register(ctx, summoner_name:str, summoner_region:str):
	await ctx.send("Register command")
	
@bot.command(name='sourcecode', help = "Links the source code to how I work!")
async def sourcecode(ctx):
	await ctx.send("https://www.github.com/Leothechosen/AmazingBot")
	
@bot.command(name='shitlist', help = "Mod command only. [add/remove] [user]")
async def shitlist(ctx, addremove = None, user = None):
	return
	
async def theserverTime():
	while True:
		minutecheck = datetime.now(timezone('CET'))
		fmt = '%H:%M %Z'
		fmt2 ='%s'
		minutecheck = minutecheck.strftime(fmt2)
		minutecheck = int(minutecheck)
		minutecheck = minutecheck % 60
		minutecheck = 61 - minutecheck
		await asyncio.sleep(minutecheck)
		guild = discord.utils.get(bot.guilds, name = leoserver)
		servertimechannel = discord.utils.get(guild.voice_channels)
		berlin = datetime.now(timezone('CET'))
		berlin = berlin.strftime(fmt)
		await servertimechannel.edit(name = berlin)
		await asyncio.sleep(60)
	

async def amazingLive():
	streamlive = True # Assume the stream is live
	guild = discord.utils.get(bot.guilds, name = leoserver)
	announcementchannel = discord.utils.get(guild.channels, name='test')
	while True:
		twitchrequest = twitchrequest = requests.get("https://api.twitch.tv/kraken/streams/" + amazing + "?api_verson=5", headers={"Accept": "application/vnd.twitchtv.v5+json", "Client-ID": twitchtoken})
		if twitchrequest.json()['stream'] == None and streamlive == True: #If not live while code thinks stream is live
			announcementchannel.send("Amazing is no longer live")
			streamlive = False
		elif twitchrequest.json()['stream'] != None and streamlive == False: #If live while code thinks stream isn't live
			announcementchannel.send("Amazing is live")
			streamlive = True
		
		await asyncio.sleep(60)
		
		
		
async def testdef():
	print("testdef worked")
	
bot.run(TOKEN)


