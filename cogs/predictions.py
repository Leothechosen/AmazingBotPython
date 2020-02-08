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
		id integer PRIMARY KEY AUTOINCREMENT,
		code text,
		name text
	);

	CREATE TABLE Match (
		id integer,
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
	c.executescript("""
	INSERT INTO League(code, name) VALUES ("lcs", "LCS");
	INSERT INTO League(code, name) VALUES ("lec", "LEC");
	INSERT INTO League(code, name) VALUES ("lck", "LCK");
	INSERT INTO League(code, name) VALUES ("lpl", "LPL");
	INSERT INTO League(code, name) VALUES ("oce-opl", "OPL");
	INSERT INTO League(code, name) VALUES ("cblol-brazil", "CBLOL");
	INSERT INTO League(code, name) VALUES ("turkiye-sampiyonluk-ligi", "TCL");
	INSERT INTO League(code, name) VALUES ("ljl-japan", "LJL");
	INSERT INTO League(code, name) VALUES ("lcs-academy", "LCSA");
	""")
def setup(bot): 
	bot.add_cog(Predictions(bot))
