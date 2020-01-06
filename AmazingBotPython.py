# AmazingBotPython.py

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
	await isAmazingNotLive()
	await serverTime()
	
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
		summoneridrequest = requests.get('https://' + region + '.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + name + '?api_key=' + apikey)
		summonerid = (summoneridrequest.json()['id'])
		rankedrequest = requests.get('https://' + region + '.api.riotgames.com/lol/league/v4/entries/by-summoner/' + summonerid + '?api_key=' + apikey)
		if rankedrequest.json() != []:
			for x in range(2):
				if rankedrequest.json()[x]["queueType"] == "RANKED_FLEX_SR":
					message += (rankedrequest.json()[x]["tier"] + " " + rankedrequest.json()[x]["rank"] + " " + str(rankedrequest.json()[x]["leaguePoints"]) + "LP in Ranked Flex\n")
				elif rankedrequest.json()[x]["queueType"] == "RANKED_SOLO_5x5":
					message += (rankedrequest.json()[x]["tier"] + " " + rankedrequest.json()[x]["rank"] + " " + str(rankedrequest.json()[x]["leaguePoints"]) + "LP in Ranked Solo\n")
		tftrequest = requests.get("https://" + region + ".api.riotgames.com/tft/league/v1/entries/by-summoner/" + summonerid + "?api_key=" + apikey)
		if tftrequest.json() != []:
				message += (tftrequest.json()[0]["tier"] + " " + tftrequest.json()[0]["rank"] + " " + str(tftrequest.json()[0]["leaguePoints"]) + "LP in Ranked TFT")
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
	
async def serverTime():
	print("serverTime activated")
	berlin = datetime.now(timezone('CET'))
	print(berlin)
	fmt = '%H:%M %Z'
	fmt2 ='%s'
	servertime = berlin.strftime(fmt)
	minutecheck = berlin.strftime(fmt2)
	print(minutecheck)
	guild = discord.utils.get(bot.guilds, name = leoserver)
	servertimechannel = discord.utils.get(guild.voice_channels)
	await servertimechannel.edit(name = servertime)
	await asyncio.sleep(60)
	print("Server Time timer")
	await serverTime()
	
async def isAmazingLive():
	guild = discord.utils.get(bot.guilds, name = leoserver)
	announcementchannel = discord.utils.get(guild.text_channels) #Only returns the first text channel. Fix.
	print(announcementchannel)
	twitchrequest = requests.get("https://api.twitch.tv/kraken/streams/" + leo + "?api_verson=5", headers={"Accept": "application/vnd.twitchtv.v5+json", "Client-ID": twitchtoken})
	if twitchrequest.json()['stream'] == None: #If not live
		await asyncio.sleep(60)
		await isAmazingLive()
		
	elif twitchrequest.json()['stream'] != None: #If live
		await announcementchannel.send("Amazing is live")
		await isAmazingNotLive()
		return; 
		
	
async def isAmazingNotLive():
	twitchrequest = requests.get("https://api.twitch.tv/kraken/streams/" + leo + "?api_verson=5", headers={"Accept": "application/vnd.twitchtv.v5+json", "Client-ID": twitchtoken})
	if twitchrequest.json()['stream'] == None: #If not live
		await isAmazingLive()
	elif twitchrequest.json()['stream'] != None: #If live
		await asyncio.sleep(60)
		await isAmazingNotLive()
		return;
		
bot.run(TOKEN)


