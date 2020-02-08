import discord
import aiohttp
import asyncio
import os
import sqlite3
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
leagueapikey = os.getenv('LEAGUE_API_KEY')

try:
	f = open('Predictions.db')
except IOError:
	print("File not accessible")
	createdb()
finally:
	f.close()

class Predictions(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
def createdb():
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	
	c.executescript("""
	CREATE TABLE User (
		id integer PRIMARY KEY AUTOINCREMENT,
		discord_id integer,
		name text
	);

	CREATE TABLE Team (
		id integer PRIMARY KEY AUTOINCREMENT,
		code text,
		name text
	);

	CREATE TABLE League (
		id blob PRIMARY KEY AUTOINCREMENT,
		code text,
		name text
	);

	CREATE TABLE Match (
		id blob,
		id_team_1 integer,
		id_team_2 integer,
		id_league integer,
		score_team_1 integer,
		score_team_2 integer
	);

	CREATE TABLE Prediction (
		id integer PRIMARY KEY AUTOINCREMENT,
		id_user integer,
		id_match integer,
		id_team_predicted integer
	);
	""")
def setup(bot):
	bot.add_cog(Predictions(bot))
