import asyncio
import re
import discord
import aiohttp
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
leagueapikey = os.getenv("LEAGUE_API_KEY")
runeterraapikey = os.getenv("RUNETERRA_API_KEY")


async def esports(ctx, endpoint, param, paramId):
    headers = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://esports-api.lolesports.com/persisted/gw/" + endpoint + "?hl=en-US&" + param + "=" + paramId,
            headers=headers,
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
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
                return
            response = await response.json()
            await session.close()
    return response
