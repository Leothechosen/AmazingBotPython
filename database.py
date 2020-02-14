import aiohttp
import asyncio
import sqlite3

async def checkDB():
	try:
		dbfile = open('Predictions.db')
		print("Database accessed")
		dbfile.close()
		return
	except IOError:
		print("Database not accessible")
		await createdb()
		return

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
		id_winning_team integer,
		id_league integer,
		block_name text,
		start_time datetime
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
		#Following array: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, LCSA (All spring split)
		leagues = ["98767991299243165", "98767991302996019", "98767991310872058", "98767991314006698", "98767991331560952", "98767991332355509", "98767991343597634", "98767991349978712", "99332500638116286"]
		for x in range(len(leagues)):
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US&leagueId=" + leagues[x], headers=headers) as response:
				schedule_response = await response.json()
				scheduled = schedule_response["data"]["schedule"]["events"]
				d = "2020-01-01T00:00:00Z"
				for y in range(len(scheduled)):
					if d < scheduled[y]["startTime"]:
						if scheduled[y]["state"] == "unstarted":
							c.execute("INSERT INTO Match(id, id_team_1, id_team_2, id_winning_team, id_league, block_name, start_time) VALUES (?, (SELECT id From Team WHERE code LIKE ?), (SELECT id FROM Team WHERE code LIKE ?), ?, (SELECT id FROM League WHERE code LIKE ?), ?, ?)", (scheduled[y]["match"]["id"], scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], None, scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"]))
						elif scheduled[y]["match"]["teams"][0]["result"]["outcome"] == "win":
							c.execute("INSERT INTO Match(id, id_team_1, id_team_2, id_winning_team, id_league, block_name, start_time) VALUES (?, (SELECT id From Team WHERE code LIKE ?), (SELECT id FROM Team WHERE code LIKE ?), ?, (SELECT id FROM League WHERE code LIKE ?), ?, ?)", (scheduled[y]["match"]["id"], scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"]))
						else:
							c.execute("INSERT INTO Match(id, id_team_1, id_team_2, id_winning_team, id_league, block_name, start_time) VALUES (?, (SELECT id From Team WHERE code LIKE ?), (SELECT id FROM Team WHERE code LIKE ?), ?, (SELECT id FROM League WHERE code LIKE ?), ?, ?)", (scheduled[y]["match"]["id"], scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"]))
							
	conn.commit()
	conn.close()
	await session.close()
	return

async def checkdiscord(ctx):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	c.execute("SELECT * FROM User WHERE discord_id = ?", (ctx.author.id,))
	data = c.fetchone()
	if data == None:
		c.execute("INSERT INTO User(discord_id, name) VALUES (?, ?)", (ctx.author.id, ctx.author.name))
	conn.commit()
	conn.close()
	
async def updatematch(ctx):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	#Following array: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, LCSA (All spring split)
	leagues = ["98767991299243165", "98767991302996019", "98767991310872058", "98767991314006698", "98767991331560952", "98767991332355509", "98767991343597634", "98767991349978712", "99332500638116286"]
	headers = {'x-api-key': '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'}
	async with aiohttp.ClientSession() as session:
		for x in range(len(leagues)):
			async with session.get("https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-US&leagueId=" + leagues[x], headers=headers) as response:
				schedule_response = await response.json()
				scheduled = schedule_response["data"]["schedule"]["events"]
				c.execute("SELECT min(id) FROM Match WHERE id_winning_team is NULL")
				match_id = c.fetchone()
				d = "2020-01-01T00:00:00Z"
				for y in range(len(scheduled)):
					if d < scheduled[y]["startTime"]:
						if scheduled[y]["state"] == "unstarted":
							c.execute("UPDATE Match SET id_team_1 = (SELECT id FROM Team WHERE code LIKE ?), id_team_2 = (SELECT id FROM Team WHERE code LIKE ?), id_winning_team = ?, id_league = (SELECT id FROM League WHERE code LIKE ?), block_name = ?, start_time = ? WHERE id = ?", (scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], None, scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"], scheduled[y]["match"]["id"]))
						elif scheduled[y]["match"]["teams"][0]["result"]["outcome"] == "win":
							c.execute("UPDATE Match SET id_team_1 = (SELECT id FROM Team WHERE code LIKE ?), id_team_2 = (SELECT id FROM Team WHERE code LIKE ?), id_winning_team = ?, id_league = (SELECT id FROM League WHERE code LIKE ?), block_name = ?, start_time = ? WHERE id = ?", (scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"], scheduled[y]["match"]["id"]))
						else:
							c.execute("UPDATE Match SET id_team_1 = (SELECT id FROM Team WHERE code LIKE ?), id_team_2 = (SELECT id FROM Team WHERE code LIKE ?), id_winning_team = ?, id_league = (SELECT id FROM League WHERE code LIKE ?), block_name = ?, start_time = ? WHERE id = ?", (scheduled[y]["match"]["teams"][0]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["match"]["teams"][1]["code"], scheduled[y]["league"]["slug"], scheduled[y]["blockName"], scheduled[y]["startTime"], scheduled[y]["match"]["id"]))
	conn.commit()
	conn.close()
	await session.close()
	await ctx.send("Updatematch function didn't crash")
	return

async def get_next_block_and_matches(league_name):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	c.execute("SELECT DISTINCT o.block_name FROM Match o WHERE o.id_league = (SELECT id FROM League WHERE name = ?) and strftime('%Y-%m-%d %H-%M-%S', 'now') < (SELECT min(i.start_time) FROM Match i WHERE i.id_league = (SELECT id FROM League WHERE name = ?) and i.block_name = o.block_name) ORDER BY start_time", (league_name, league_name))
	block_name = c.fetchone()[0]
	c.execute("SELECT * from Match WHERE id_league = (SELECT id FROM league WHERE name = ?) and block_name = ?", (league_name, block_name))
	matches = c.fetchall()
	return block_name, matches

async def fetchTeamIds(team_1, team_2):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	c.execute("SELECT name FROM Team WHERE id = ?", (team_1,))
	team_1 = c.fetchone()[0]
	c.execute("SELECT name FROM Team WHERE id = ?", (team_2,))
	team_2 = c.fetchone()[0]
	conn.close()
	return team_1, team_2

async def writePredictions(predicted_team, match, user):
	predictioncheck = None
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	c.execute("SELECT id_match FROM Prediction WHERE id_match = ? and id_user = (SELECT id FROM User WHERE discord_id = ?)", (match, user))
	predictioncheck = c.fetchone()
	if predictioncheck == None:
		c.execute("INSERT INTO Prediction (id_user, id_match, id_team_predicted) VALUES ((SELECT id FROM User WHERE discord_id = ?), ?, (SELECT id FROM Team WHERE name = ?))", (user, match, predicted_team))
	else:
		c.execute("UPDATE Prediction SET id_team_predicted = (SELECT id FROM Team WHERE name = ?) WHERE id_user = (SELECT id FROM User WHERE discord_id = ?) and id_match = ?", (predicted_team, user, match))
	conn.commit()
	conn.close()
	
async def fetchLeaguesPredicted(user):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	c.execute("select distinct id_league from match where id in (select id_match from prediction p where p.id_user = (select id from user where discord_id = ?)) order by 1", (user,))
	predicted_leagues = c.fetchall()
	return predicted_leagues
	
async def fetchPredictions(user, league):
	return
		

async def fetchCorrect(league, discord_id):
	conn = sqlite3.connect('Predictions.db')
	c = conn.cursor()
	block_name_msg = ""
	correct_pred_msg = ""
	wrong_pred_msg = ""
	if league == "Overall":
		c.execute("select c.block block, c.correct correct, (select count(*) from prediction p, match m where m.id = p.id_match and p.id_user = (select id from user where discord_id = ?) and m.block_name = c.block group by m.block_name) - c.correct wrong from (select m.block_name block, count(*) correct from prediction p, match m where m.id = p.id_match and p.id_team_predicted = m.id_winning_team and p.id_user = (select id from user where discord_id = ?) group by m.block_name) c", (discord_id, discord_id)) #All Leagues Per Block
		overall_per_block = c.fetchall()
		for x in range(len(overall_per_block)):
			block_name_msg += str(overall_per_block[x][0]) + '\n'
			correct_pred_msg += str(overall_per_block[x][1]) + '\n'
			wrong_pred_msg += str(overall_per_block[x][2]) + '\n'
		c.execute("select c.correct correct, (select count(*) from prediction p, match m where m.id = p.id_match and p.id_user = (select id from user where discord_id = ?)) - c.correct wrong from (select count(*) correct from prediction p, match m where m.id = p.id_match and p.id_team_predicted = m.id_winning_team and p.id_user = (select id from user where discord_id = ?)) c;", (discord_id, discord_id)) #All Leagues Overall
		overall = c.fetchone()
		block_name_msg += "Overall"
		correct_pred_msg += str(overall[0])
		wrong_pred_msg += str(overall[1])
	else:
		c.execute("select c.block block, c.correct correct, (select count(*) from prediction p, match m where m.id = p.id_match and p.id_user = (select id from user where discord_id = ?) and m.id_league = (select id from league where name = ?) and m.block_name = c.block group by m.block_name) - c.correct wrong from (select m.block_name block, count(*) correct from prediction p, match m where m.id = p.id_match and p.id_team_predicted = m.id_winning_team and p.id_user = (select id from user where discord_id = ?) and m.id_league = (select id from league where name = ?) group by m.block_name) c;", (discord_id, league, discord_id, league)) #1 League, Per Block
		league_per_block = c.fetchall()
		for x in range(len(league_per_block))	:
			block_name_msg += str(league_per_block[x][0]) + '\n'
			correct_pred_msg += str(league_per_block[x][1]) + '\n'
			wrong_pred_msg += str(league_per_block[x][2]) + '\n'
		c.execute("select c.correct correct, (select count(*) from prediction p, match m where m.id = p.id_match and p.id_user = (select id from user where discord_id = ?) and m.id_league = (select id from league where name = ?)) - c.correct wrong from (select count(*) correct from prediction p, match m where m.id = p.id_match and p.id_team_predicted = m.id_winning_team and p.id_user = (select id from user where discord_id = ?) and m.id_league = (select id from league where name = ?)) c;", (discord_id, league, league, discord_id)) #1 League, Overall
		league_overall = c.fetchone()
		block_name_msg += "Overall"
		correct_pred_msg += str(league_overall[0])
		wrong_pred_msg += str(league_overall[1])
	conn.close()
	return block_name_msg, correct_pred_msg, wrong_pred_msg
