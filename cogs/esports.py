import discord
import asyncio
import math
import utils
import apirequests
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands
import logging

logger = logging.getLogger("AmazingBot." + __name__)

class eSports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, help="Subcommands: standings and team")
    async def esports(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are standings, team and schedule. See pinned message for usage.")
        return

    @esports.command(pass_context=True)
    async def standings(self, ctx, tournament=None):
        if tournament == None:
            await ctx.send(
                "Usage: `-esports standings [league]`. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)"
            )
            return
        ordinal_message = ""
        teams_message = ""
        records_message = ""
        tournamentId = await utils.getTournamentId(tournament)
        if tournamentId == "Invalid League":
            await ctx.send(
                "League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)"
            )
            return
        standings_response = await apirequests.esports(ctx, "getStandings", "tournamentId", tournamentId)
        rankings = standings_response["data"]["standings"][0]["stages"][0]["sections"][0]["rankings"]
        for x in range(len(rankings)):
            for y in range(len(rankings[x]["teams"])):
                team = rankings[x]["teams"][y]
                ordinal = str(rankings[x]["ordinal"])
                ordinal = await utils.integerPrefix(ordinal)
                ordinal_message += ordinal + "\n"
                teams_message += f'{team["name"]}\n'
                records_message += f'{team["record"]["wins"]} - {team["record"]["losses"]}\n'
        embed = discord.Embed(title=tournament.upper() + " Standings", color=0xA9152B)
        embed.add_field(name="Place", value=ordinal_message, inline=True)
        embed.add_field(name="Team", value=teams_message, inline=True)
        embed.add_field(name="Record", value=records_message, inline=True)
        await ctx.send(embed=embed)

    @esports.command(pass_context=True)
    async def schedule(self, ctx, league=None, team=None):
        schedule_message = ""
        teams1_message = ""
        teams2_message = ""
        opponent_message = ""
        thumbnail = ""
        team_record = ""
        next_4_matches = 0
        if league is None:
            await ctx.send(
                "Usage: `-esports schedule [league] (Optional: [team abbreviation])`. Supported leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)"
            )
            return
        leaguename = await utils.sanitizeinput(league)
        leagueid = await utils.getLeagueId(league)
        if leagueid == "Invalid League":
            await ctx.send(
                "League not supported. Supported Leagues are: LCS, LEC, LCK, LPL, OPL, CBLOL, TCL, LJL, and LCSA(cademy)"
            )
            return
        schedule_response = await apirequests.esports(ctx, "getSchedule", "leagueId", leagueid)
        currenttime = datetime.utcnow()
        scheduled_matches = schedule_response["data"]["schedule"]["events"]
        for x in range(len(scheduled_matches)):
            if scheduled_matches[x]["state"] == "unstarted":
                team_1 = scheduled_matches[x]["match"]["teams"][0]
                team_2 = scheduled_matches[x]["match"]["teams"][1]
                if team_1["record"] != None:
                    team_1_record = "(" + str(team_1["record"]["wins"]) + "-" + str(team_1["record"]["losses"]) + ")"
                else:
                    team_1_record = None
                if team_2["record"] != None:
                    team_2_record = "(" + str(team_2["record"]["wins"]) + "-" + str(team_2["record"]["losses"]) + ")"
                else:
                    team_1_record = None
                if team is None:
                    starttime = await utils.get_start_time(scheduled_matches[x]["startTime"])
                    if currenttime + timedelta(days=7) > starttime:
                        days, hours, minutes = await utils.days_hours_minutes(starttime - currenttime)
                        remainingtime = await utils.timeformatting(days, hours, minutes)
                        schedule_message += remainingtime
                        if leaguename == "LCSA":
                            teams1_message += "**" + team_1["name"][:-8] + " " + team_1_record + "**\n"
                            teams2_message += "**" + team_2["name"][:-8] + " " + team_2_record + "**\n"
                        else:
                            teams1_message += "**" + team_1["name"] + " " + team_1_record + "**\n"
                            teams2_message += "**" + team_2["name"] + " " + team_2_record + "**\n"
                else:
                    if next_4_matches != 4:
                        if team_1["code"] == team or team_2["code"] == team:
                            starttime = await utils.get_start_time(scheduled_matches[x]["startTime"])
                            days, hours, minutes = await utils.days_hours_minutes(starttime - currenttime)
                            remainingtime = await utils.timeformatting(days, hours, minutes)
                            schedule_message += remainingtime
                            if team_1["code"] == team:
                                team_record = team_1_record
                                opponent_message += "**" + team_2["name"] + " " + team_2_record + "**\n"
                                thumbnail = team_1["image"]
                            else:
                                team_record = team_2_record
                                opponent_message += "**" + team_1["name"] + " " + team_1_record + "**\n"
                                thumbnail = team_2["image"]
                            next_4_matches += 1
        if schedule_message == "":
            await ctx.send("Team could not be found.")
            return
        if team == None:
            embed = discord.Embed(title=leaguename.upper() + " Schedule", color=0xA9152B)
            embed.add_field(name="Time Remaining", value=schedule_message, inline=True)
            embed.add_field(name="Team 1", value=teams1_message, inline=True)
            embed.add_field(name="Team 2", value=teams2_message, inline=True)
            embed.set_footer(text="Next 7 Days")
        else:
            embed = discord.Embed(title=team.upper() + " " + team_record, color=0xA9152B)
            embed.add_field(name="Time Remaining", value=schedule_message, inline=True)
            embed.add_field(name="Opponent", value=opponent_message, inline=True)
            embed.set_footer(text="Next 4 Matches")
            embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

    @esports.command(pass_context=True)
    async def team(self, ctx, team=None):
        role_message = ""
        name_message = ""
        if team == None:
            await ctx.send(
                "Usage: `-esports team [team]. Example: -esports team TSM`. If the team has spaces, replace the spaces with dashes. For example: Counter-Logic-Gaming"
            )
            return
        team = await utils.sanitizeinput(team)
        team_response = await apirequests.esports(ctx, "getTeams", "id", team.lower())
        if team_response["data"]["teams"] == []:
            await ctx.send(
                "Invalid team name. If the team has spaces, replace the spaces with dashes. For example: Counter-Logic-Gaming. Otherwise, check spelling, or try an abbreviation, e.g TSM"
            )
            return
        embed = discord.Embed(title=team.upper() + " Roster", color=0xA9152B)
        names = team_response["data"]["teams"][0]["players"]
        for x in range(len(names)):
            role_message += (names[x]["role"]).title() + "\n"
        embed.add_field(name="Role", value=role_message, inline=True)
        for x in range(len(names)):
            name_message += names[x]["firstName"] + " '" + names[x]["summonerName"] + "' " + names[x]["lastName"] + "\n"
        embed.add_field(name="Name", value=name_message, inline=True)
        embed.set_thumbnail(url=team_response["data"]["teams"][0]["image"])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(eSports(bot))
