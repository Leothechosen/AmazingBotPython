import discord
import aiohttp
import asyncio
import os
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
twitchtoken = os.getenv("TWITCH_API_KEY")
amazingserverid = int(os.getenv("AMAZING_SERVER_ID"))
amazing = os.getenv("AMAZING_CHANNEL")
announcements = [
    "Go, get in there!",
    "Tune in and find out why they call him the Anaconda",
    "Come watch and soon you'll be Amazing yourself",
    "Don't knock him before you try him",
]


class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await amazingLive(self)


async def amazingLive(self):
    announcementchannel = int(os.getenv("AMAZING_ANNOUNCEMENT_ID"))
    streamlive = True  # Assume the stream is live
    announcementchannel = self.bot.get_channel(id=announcementchannel)
    while True:
        async with aiohttp.ClientSession() as session:
            headers = {"Accept": "application//vnd.twitchtv.v5+json", "Client-ID": twitchtoken}
            async with session.get(
                "https://api.twitch.tv/kraken/streams/" + amazing + "?api_verson=5", headers=headers
            ) as response:
                twitchrequest = await response.json()
            await session.close()
        # If not live while code thinks stream is live
        if twitchrequest["stream"] == None and streamlive == True:
            streamlive = False
            print("Amazing has gone offline")
            continue
        # If live while code thinks stream isn't live
        elif twitchrequest["stream"] != None and streamlive == False:
            await announcementchannel.send(
                "@everyone " + random.choice(announcements) + " https://www.twitch.tv/amazingx"
            )
            streamlive = True
            print("Amazing has gone online")
            continue
        await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Twitch(bot))
