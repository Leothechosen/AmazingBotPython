import discord
import aiohttp
import asyncio
import os
import random
import apirequests
from discord.ext import commands
from dotenv import load_dotenv
import logging

logger = logging.getLogger("AmazingBot." + __name__)

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
        twitchrequest = await apirequests.twitch(amazing)
        # If not live while code thinks stream is live
        if twitchrequest["stream"] == None and streamlive == True:
            streamlive = False
            logger.info("Amazing has gone offline")
            continue
        # If live while code thinks stream isn't live
        elif twitchrequest["stream"] != None and streamlive == False:
            await announcementchannel.send(
                "@everyone " + random.choice(announcements) + " https://www.twitch.tv/amazingx"
            )
            streamlive = True
            logger.info("Amazing has gone online")
            continue
        await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Twitch(bot))
