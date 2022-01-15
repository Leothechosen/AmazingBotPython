import asyncio
import re
import discord
import aiohttp
import os
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logger = logging.getLogger("AmazingBot." + __name__)

load_dotenv()
leagueapikey = os.getenv("LEAGUE_API_KEY")
runeterraapikey = os.getenv("RUNETERRA_API_KEY")
twitchapikey = os.getenv("TWITCH_API_KEY")
twitchapisecret = os.getenv("TWITCH_API_SECRET")
esportsapikey = os.getenv("ESPORTS_API_KEY")
githubapikey = os.getenv("GITHUB_API_KEY")
token_expire_time = None
twitch_oauth_token = None


async def esports(ctx, endpoint, param, paramId):
    headers = {"x-api-key": esportsapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://esports-api.lolesports.com/persisted/gw/" + endpoint + "?hl=en-US&" + param + "=" + paramId,
            headers=headers,
        ) as response:
            if response.status != 200:
                await ctx.send("Riot API returned a " + response.status + " error.")
                logger.warning(f'eSports API returned a {response.status} response code. Endpoint: {endpoint} | Parameter_Name: {param} | Parameter_Value: {paramId}')
                return
            response = await response.json()
            await session.close()
    return response

async def league(ctx, region, endpoint, param, paramId):
    headers = {"X-Riot-Token": leagueapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://" + region + ".api.riotgames.com/lol/" + endpoint + "/v4/" + param + str(paramId), headers=headers
        ) as response:
            if response.status != 200:
                if endpoint == "spectator":
                    await ctx.send("User is not currently in a game.")
                    return
                elif endpoint == "match":
                    return
                await ctx.send("Riot API returned a " + str(response.status) + " error.")
                logger.warning(f'League API returned a {response.status} response code. Endpoint: {endpoint} | Parameter_Name: {param} | Parameter_Value: {paramId}')
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
                logger.warning(f'TFT API returned a {response.status} response code. Endpoint: {endpoint} | Parameter_Name: {param} | Parameter_Value: {paramId}')
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
                logger.warning(f'LoR API returned a {response.status} response code. Endpoint: {endpoint} | Parameter_Name: {param} | Parameter_Value: {paramId}')
                return
            response = await response.json()
            await session.close()
    return response

async def twitch_oauth():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://id.twitch.tv/oauth2/token?client_id={twitchapikey}&client_secret={twitchapisecret}&grant_type=client_credentials&scope=channel:read:subscriptions") as response:
            oauthrequest = await response.json()
            logger.info(oauthrequest)
            global token_expire_time
            token_expire_time = datetime.now() + timedelta(seconds=oauthrequest["expires_in"])
            global twitch_oauth_token
            twitch_oauth_token = oauthrequest["access_token"]
            logger.info(f"Twitch OAUTH Token: {twitch_oauth_token} expires at {token_expire_time}")
        await session.close()
    return

async def twitch(user):
    headers = {"Accept": "application//vnd.twitchtv.v5+json", "Client-ID": twitchapikey}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/kraken/streams/" + user + "?api_verson=5", headers=headers
        ) as response:
            if response.status != 200:
                logger.warning(f'Twitch API returned a {response.status} response code.')
            twitchrequest = await response.json()
        await session.close()
    return twitchrequest

# TODO: Need User Access Token
# async def twitch_subs(user):
#     if twitch_oauth_token is None:
#         await twitch_oauth()
#     elif datetime.now() > token_expire_time:
#         await twitch_oauth()
#     headers = {"Authorization": f"Bearer {twitch_oauth_token}", "Client-ID": twitchapikey}
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={user}", headers=headers) as response:
#             if response.status != 200:
#                 logger.warning(f"Twitch API returned a {response.status} response code in Clips.")
#                 response = await response.json()
#                 logger.info(response)
#                 return None
#             response = await response.json()
#         await session.close()
#     return response

async def clips(user):
    # Twitch Get Clips will only return clips in order of views, which impedes with posting a new clip when it's generated
    # Luckily, I can pass a started_at query to all clips that were made after that start date
    # Set started_at query to a day before the query. 
    # Then store the clip IDs in a database
    # Compare all the clip IDs in the response JSON to what's in the database
    # If a clip is not in the database, send it to the clips channel in Amazing's Discord, then add the clip to the ID. 
    if twitch_oauth_token is None:
        await twitch_oauth()
    elif datetime.now() > token_expire_time:
        await twitch_oauth()
    headers = {"Authorization": f"Bearer {twitch_oauth_token}", "Client-ID": twitchapikey}
    started_at = datetime.utcnow() - timedelta(days=1)
    started_at = started_at.isoformat("T") + "Z"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.twitch.tv/helix/clips/?broadcaster_id={user}&started_at={started_at}", headers=headers
        ) as response:
            if response.status != 200:
                logger.warning(f"Twitch API returned a {response.status} response code in Clips.")
                return None
            response = await response.json()
        await session.close()
    return response

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
                logger.info(f'Github API returned a {response.status}')
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
                logger.warning(f'Clash User API returned a {response.status} response code. Region: {region} | Summoner_ID: {summonerid}')
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
                logger.warning(f'Clash Team API returned a {response.status} response code. Region {region} | Team_ID: {teamid}')
                return
            response = await response.json()
            await session.close()
    return response
