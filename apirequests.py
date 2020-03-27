import asyncio
import re
import discord
import aiohttp
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logger = logging.getLogger("AmazingBot." + __name__)

load_dotenv()
leagueapikey = os.getenv("LEAGUE_API_KEY")
runeterraapikey = os.getenv("RUNETERRA_API_KEY")
twitchapikey = os.getenv("TWITCH_API_KEY")
esportsapikey = os.getenv("ESPORTS_API_KEY")
githubapikey = os.getenv("GITHUB_API_KEY")


async def esports(ctx, endpoint, param, paramId):
    headers = {"x-api-key": esportsapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://esports-api.lolesports.com/persisted/gw/" + endpoint + "?hl=en-US&" + param + "=" + paramId,
            headers=headers,
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
                logging.warning(
                    " eSports API returned a "
                    + response.status
                    + " response code. Endpoint: "
                    + endpoint
                    + " | Parameter_Name: "
                    + param
                    + " | Parameter_Value: "
                    + paramId
                )
                return
            response = await response.json()
            await session.close()
    return response


async def league(ctx, region, endpoint, param, paramId):
    headers = {"X-Riot-Token": leagueapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/lol/" + endpoint + "/v4/" + param + paramId, headers=headers
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
                logging.warning(
                    "Riot API returned a "
                    + response.status
                    + " response code. Region: "
                    + region
                    + " | Endpoint: "
                    + endpoint
                    + " | Parameter_Name: "
                    + param
                    + " | Parameter_Value: "
                    + paramId
                )
                return
            response = await response.json()
            await session.close()
    return response


async def tft(ctx, region, endpoint, param, paramId):
    headers = {"X-Riot-Token": ""}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/tft/" + endpoint + "/v1/" + param + paramId, headers=headers
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
                logging.warning(
                    "Riot API returned a "
                    + response.status
                    + " response code. Region: "
                    + region
                    + " | Endpoint: "
                    + endpoint
                    + " | Parameter_Name: "
                    + param
                    + " | Parameter_Value: "
                    + paramId
                )
                return
            response = await response.json()
            await session.close()
    return response


async def lor(ctx, region, endpoint, param, paramId):
    headers = {"X-Riot-Token": runeterraapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/lor/" + endpoint + "/v1/" + param + paramId, headers=headers
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
                logging.warning(
                    "Riot API returned a "
                    + response.status
                    + " response code. Region: "
                    + region
                    + " | Endpoint: "
                    + endpoint
                    + " | Parameter_Name: "
                    + param
                    + " | Parameter_Value: "
                    + paramId
                )
                return
            response = await response.json()
            await session.close()
    return response


async def twitch(user):
    headers = {"Accept": "application//vnd.twitchtv.v5+json", "Client-ID": twitchapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/kraken/streams/" + user + "?api_verson=5", headers=headers
        ) as response:
            twitchrequest = await response.json()
        await session.close()
    return twitchrequest


async def github():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Leothechosen",
        "Authorization": "token" + githubapikey,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.github.com/repos/Leothechosen/AmazingBotPython/commits", headers=headers) as response:
            githubrequest = await response.json()
            if response.status != 200:
                logger.info("github returned a " + response.status)
            await session.close()
    return githubrequest

async def foldingathome(ctx, endpoint, user_or_team):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://stats.foldingathome.org/api/" + endpoint + "/" + user_or_team) as response:
            try:
                foldingathomerequest = await response.json()
            except:
                await ctx.send("The Folding@Home API appears to be down right now. Sorry!")
                return
            if response.status != 200 or "error" in foldingathomerequest:
                logger.info("Folding@Home returned a " + str(response.status))
                await ctx.send("There was an error with the API request.")
                return
            await session.close()
    return foldingathomerequest
            

async def clash_user(ctx, region, summonerid):
    headers = {"X-Riot-Token": leagueapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/lol/clash/v1/players/by-summoner/" + summonerid, headers=headers
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + str(response.status) + " error.")
                logging.warning(
                    "Riot API returned a "
                    + response.status
                    + " response code. Region: "
                    + region
                    + " | Summoner_ID: "
                    + str(summonerid)
                )
                return
            response = await response.json()
            await session.close()
    return response

async def clash_team(ctx, region, teamid):
    headers = {"X-Riot-Token": leagueapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/lol/clash/v1/teams/" + teamid, headers=headers
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + str(response.status) + " error.")
                logging.warning(
                    "Riot API returned a "
                    + response.status
                    + " response code. Region: "
                    + region
                    + " | Team_ID: "
                    + str(teamid)
                )
                return
            response = await response.json()
            await session.close()
    return response