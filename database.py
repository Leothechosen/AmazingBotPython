import aiohttp
import asyncio
import sqlite3

def getTournamentId(self, tournament):
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
			
async def checkDB(self):
	try:
		dbfile = open('Predictions.db')
		dbfile.close()
	except IOError:
		print("File not accessible")
		await createdb()

async def createdb():
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
	
	async with aiohttp.ClientSession() as session:
		#Following array: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, LCSA
		tournaments = ["103462439438682788","103462459318635408","103540363364808496","103462420723438502","103535401218775284", "103478354329449186", "103495775740097550", "103540397353089204", "103462454280724883"]
		headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
		for x in range(len(tournaments)):
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getStandings?hl=en-US&tournamentId=" + tournaments[x], headers=headers) as response:
				standings_response = await response.json()
				rankings = (standings_response["data"]["standings"][0]["stages"][0]["sections"][0]["rankings"])
				for y in range(len(rankings)):
					for z in range(len(rankings[y]["teams"])):
						codes = rankings[y]
						c.execute("INSERT INTO Team(code, name) VALUES (?, ?)", (rankings[y]['teams'][z]['code'], rankings[y]['teams'][z]['name']))
		await session.close()
	
	
	conn.commit()
	conn.close()
	return
