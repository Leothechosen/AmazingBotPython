import discord
import aiohttp
import asyncio
import utils
import apirequests
from discord.ext import commands
import logging
import time
import database

logger = logging.getLogger("AmazingBot." + __name__)

class League(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["League"])
    async def league(self, ctx):
        """For League of Legends | Contains the Rank, Profile, Match, and Clash subcommands.
        Current valid regions are: RU, KR, BR, OCE, JP, NA, EUNE, EUW, TR, LAN, and LAS."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands are rank, profile, and clash")
        return

    @league.command(aliases=["Rank"])
    async def rank(self, ctx, user_name, region):
        """Returns user's rank. """
        embed = discord.Embed(title=user_name + "'s Ranks in " + region, color=0xA9152B)
        region = await utils.region_to_valid_region(region.upper())
        if region == "Invalid Region":
            await ctx.send("The server you entered is invalid, or it's a Garena server")
        else:
            summonerInfo = await database.checkSummonerInfo(user_name)
            if summonerInfo is None:
                summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", user_name)
                await database.writeSummonerInfo(user_name, summoneridrequest)
                summonerid = summoneridrequest["id"]
            else:
                summonerid = summonerInfo[2]
            rankedrequest = await apirequests.league(ctx, region, "league", "entries/by-summoner/", summonerid)
            # tftrequest = await apirequests.league(ctx, region, "league", "entries/by-summoner", summonerid)
            if rankedrequest == []:  # and tftrequest == []:
                embed.add_field(name="Unranked", value=user_name + " is unranked in all queues")
                await ctx.send(embed=embed)
                return
            if rankedrequest != []:
                oldRankInfo = await database.checkRankedInfo(user_name)
                old_solo_rank = "N/A"
                old_flex_rank = "N/A"
                #old_tft_rank = "N/A"
                if oldRankInfo is not None:
                    try:
                        old_solo_rank = oldRankInfo[1] + "LP"
                        old_flex_rank = oldRankInfo[2] + "LP"
                        #old_tft_rank = oldRankInfo[3] + "LP"
                    except:
                        pass
                for x in range(len(rankedrequest)):
                    tier_rank_lp = f'{rankedrequest[x]["tier"]} {rankedrequest[x]["rank"]} {rankedrequest[x]["leaguePoints"]}LP '
                    message = tier_rank_lp
                    if "miniSeries" in rankedrequest[x]:
                        message += "| Promo: "
                        for y in range(len(rankedrequest[x]["miniSeries"]["progress"])):
                            promo_game = rankedrequest[x]["miniSeries"]["progress"][y]
                            if promo_game == "W":
                                message += ":white_check_mark:"
                            elif promo_game == "N":
                                message += ":grey_question:"
                            elif promo_game == "L":
                                message += ":x:"
                    if rankedrequest[x]["queueType"] == "RANKED_SOLO_5x5":
                        embed.add_field(name="Solo/Duo (Last Query -> Today)", value=f'{old_solo_rank} -> {message}', inline=False)
                    elif rankedrequest[x]["queueType"] == "RANKED_FLEX_SR":
                        embed.add_field(name="Flex (Last Query -> Today)", value=f'{old_flex_rank} -> {message}', inline=False)
                    else:
                        continue
                await database.writeRankedInfo(user_name, rankedrequest)
            # if tftrequest != []:
            # embed.add_field(name="TFT", value=tftrequest[0]["tier"] + " " + tftrequest[0]["rank"] + " " + str(tftrequest[0]["leaguePoints"]) + "LP",inline=True)
            await ctx.send(embed=embed)
            return

    @league.command(aliases=["Profile"])
    async def profile(self, ctx, user_name, region):
        """Returns user's profile"""
        mastery_message = ""
        profileicon = ""
        summonerid = ""
        region = await utils.region_to_valid_region(region.upper())
        summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", user_name)
        profileicon = summoneridrequest["profileIconId"]
        accountid = summoneridrequest['accountId']
        summonerlevel = summoneridrequest['summonerLevel']
        summonerid = summoneridrequest["id"]
        masteries = await apirequests.league(
            ctx, region, "champion-mastery", "champion-masteries/by-summoner/", summonerid
        )
        for x in range(3):
            champions = await utils.championid_to_champion(str(masteries[x]["championId"]))
            masterypoints = str(masteries[x]["championPoints"])
            mastery_message += f'{champions} | {masterypoints}\n'
        matches_played = await apirequests.league(ctx, region, "match", "matchlists/by-account/", accountid + "?endIndex=1&beginIndex=0")
        embed = discord.Embed(title=user_name + "'s Profile on " + region.upper(), description=f'Summoner Level: {summonerlevel}',color=0xA9152B)
        embed.set_thumbnail(
            url="http://ddragon.leagueoflegends.com/cdn/10.3.1/img/profileicon/" + str(profileicon) + ".png"
        )
        embed.add_field(name="Top 3 Masteries", value=mastery_message, inline=False)
        if matches_played != None:
            match_id = matches_played["matches"][0]["gameId"]
            champ_id_played = matches_played["matches"][0]["champion"]
            champ_played = await utils.championid_to_champion(str(champ_id_played))
            #champ_emoji = await utils.champion_to_emoji(champ_played)
            match_info = await apirequests.league(ctx, region, "match", "matches/", match_id)
            time_started = time.strftime('%m/%d', time.localtime(match_info["gameCreation"]/1000))
            user_match_info = None
            for participant in match_info["participantIdentities"]:
                if participant["player"]["accountId"] == accountid:
                    participant_id = participant["participantId"]
            for participant in match_info["participants"]:
                if participant["participantId"] == participant_id:
                    user_match_info = participant
            if user_match_info != None:
                user_stats = user_match_info["stats"]
                if user_stats['win'] == False:
                    match_result = "Loss"
                else:
                    match_result = "Win"
                KDA = (f'{user_stats["kills"]}/{user_stats["deaths"]}/{user_stats["assists"]}')
                if user_match_info["timeline"]["role"] == "DUO_CARRY" or user_match_info["timeline"]["role"] == "DUO_SUPPORT":
                    role = await utils.valid_role(user_match_info["timeline"]["role"])
                else:
                    role = await utils.valid_role(user_match_info["timeline"]["lane"])
                embed.add_field(name=f'Last Game Played ({time_started})', value=(f'{match_result} as {champ_played} {role}: ({KDA})'), inline=False)
        await ctx.send(embed=embed)
        return

    @league.command(aliases=["Clash"])
    async def clash(self, ctx, user_name, region):
        """Returns user's clash team, if any"""
        region = await utils.region_to_valid_region(region.upper())
        if region == "Invalid Region":
            await ctx.send("The server you entered is invalid, or it's a Garena server")
            return
        summonerInfo = await database.checkSummonerInfo(user_name)
        if summonerInfo is None:
            summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", user_name)
            await database.writeSummonerInfo(user_name, summoneridrequest)
            summonerid = summoneridrequest["id"]
        else:
            summonerid = summonerInfo[2]
        clash_user_response = await apirequests.clash_user(ctx, region, summonerid)
        if clash_user_response == []:
            await ctx.send(f'{user_name} is not in a Clash team at this time.')
            return
        clash_team_response = await apirequests.clash_team(ctx, region, clash_user_response[0]['teamId'])
        user_message = ""
        role_message = ""
        for x in range(len(clash_team_response['players'])):
            player_name = (await apirequests.league(ctx, region, "summoner", "summoners/", clash_team_response['players'][x]['summonerId']))['name']
            user_message += f'{player_name}\n'
            role_message += f'{clash_team_response["players"][x]["position"]}\n'
        embed = discord.Embed(title="Clash Team: " + "[" + clash_team_response['abbreviation'] + "] " + clash_team_response['name'] , description = "Tier: " + str(clash_team_response['tier']), color=0xA9152B)
        embed.add_field(name="User", value=user_message, inline=True)
        embed.add_field(name="Role", value=role_message, inline=True)
        embed.set_thumbnail(url="http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/" + str(clash_team_response['iconId']) + "/1.png")
        await ctx.send(embed=embed)
        return

    @league.command(aliases=["Match"])
    async def match(self, ctx, user_name, region):
        """If the user is in a match, send current match info along with a spectate file"""
        region = await utils.region_to_valid_region(region.upper())
        if region == "Invalid Region":
            await ctx.send("The server you entered is invalid, or it's a Garena server")
            return
        summonerInfo = await database.checkSummonerInfo(user_name)
        if summonerInfo is None:
            summoneridrequest = await apirequests.league(ctx, region, "summoner", "summoners/by-name/", user_name)
            await database.writeSummonerInfo(user_name, summoneridrequest)
            summonerid = summoneridrequest["id"]
        else:
            summonerid = summonerInfo[2]
        spectator_response = await apirequests.league(ctx, region, "spectator", "active-games/by-summoner/", summonerid)
        if spectator_response is None:
            return
        team_1_msg = ""
        team_2_msg = ""
        for player in spectator_response["participants"]:
            if player['teamId'] == 100:
                team_1_msg += (await apirequests.league(ctx, region, "summoner", "summoners/", player['summonerId']))['name'] + " (" + (await utils.championid_to_champion(str(player["championId"]))) + ")" + '\n'
            elif player['teamId'] == 200:
                team_2_msg += "(" + (await utils.championid_to_champion(str(player["championId"]))) + ") " + (await apirequests.league(ctx, region, "summoner", "summoners/", player['summonerId']))['name'] + '\n'
        in_game_timer = round(time.time() - spectator_response["gameStartTime"]/1000)
        if in_game_timer/60 >= 10:
            time_remaining = str(int(in_game_timer/60)) + ":"
        else:
            time_remaining = "0" + str(int(in_game_timer/60)) + ":"
        if in_game_timer%60 >= 10:
            time_remaining += str(int(in_game_timer%60))
        else:
            time_remaining += "0" + str(int(in_game_timer%60))
        embed = discord.Embed(title=user_name + " Match", description="In-Game Time: " + time_remaining, color=0xA9152B)
        embed.add_field(name="Team 1", value=team_1_msg, inline=True)
        embed.add_field(name="Team 2", value=team_2_msg, inline=True)
        embed.set_footer(text="In-Game Time is approximate.")
        await ctx.send(embed=embed)
        spectate_file = await utils.spectategen(ctx, region, spectator_response["gameId"], spectator_response["observers"]['encryptionKey'])
        if spectate_file == False:
            return
        await ctx.send("If you would like to spectate, download this file and run it (Windows Only, NA/EUW Only)", file = discord.File('Spectate.bat'))
        return

def setup(bot):
    bot.add_cog(League(bot))
