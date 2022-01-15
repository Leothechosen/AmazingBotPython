import discord
import os
import random
import apirequests
import database
from discord.ext import commands, tasks
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
    "Lmao you call yourself an Amazing fan? I'm fucking loaded on channel points bro. I highlight every message because I'm just that jacked. Try talking in chat again when you're a true fan",
    "I hope Maurice wins xD. I'm an Amazingx simp and he's just so hot!!! People get so swooned by the hair, and his muscles are so swole like when he stretches LOL! He's super good but also smarter than he looks, just like me xD",
    "My mom just entered my room and asked me to stop watching garbage. I told her that League of Legends was a respectable esport with millions of player around the world. She responded: “I know. I was talking about Amazingx, he's trash” KEKW.",
    "Amazingx is real. I don't care what you want to say. Amazingx isn't 'imaginary'. He posts real tweets, feels real emotions, makes real bad plays...All you trolls are MALDING because he doesn't reply to your twitch messages probably. Not me though.. I have full faith in him. That's why he replied to me a couple minutes ago when I talked to him...he literally replied? And said 'shut the fuck up??'",
    "Amazingx is fantastic, just needs to work on communication, map awareness, laning, vision control, csing, poking, landing skillshots, objective control, early game, mid game, late game, ganking, and getting kills",
    "Hey, Amazing! Big fan of the stream, I can't believe you're not playing professionally anymore..RIP. I guess that's what happens when you become a coach, lol. Anyways, I'm trying to learn to play Shaco. I just have a question about the skill build: Should I max Backstab like you got backstabbed by Nicothepico, Decieve like you decieved Misfits into thinking they were a playoffs team, or Hallucinate like you made Origin hallucinate about being able to win Worlds 2015?",
    "I want to date Amazing so bad. He is so cute and I love him so much. He has a cute smile and a cute face. He’s a gamer like me and has a amazing personality. I would love to tell him every night “I love you” and rub his feet while he is streaming We would go out when he isn’t doing gamer stuff and have fun together. He is also really good at gaming so I would be able to get carried by my very own BF. God I want to date Amazing",
    "Who is amazing? 🙄🤭🤔🤫😰 in math: my solution ➗😊 in history: my king 👑😣 in art: my canvas 🎨🥳 in science: my oxygen 💨😝 in geography: my world 🌎🤯",
    "Last Saturday, I found Amazing wet and unconscious on a beach. I quickly asked a lifeguard to watch over him while I get help. The lifeguard walks away muttering that he 'doesnt watch washed up streamers'",
    "Jungle too complicated. I'd like to just rightclick the minimap once and autoclear every camp. Also: recalling should be automated once I killed the crab, else the skill ceiling is too high to differentiate between good and bad players"
]

class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.streamlive = True
        self.amazingStream.start() # pylint: disable=no-member
        self.amazingClips.start() # pylint: disable=no-member
        # self.amazingSubs.start() # pylint: disable=no-member

    @tasks.loop(minutes=1.0)
    async def amazingStream(self):
        announcementchannel = int(os.getenv("AMAZING_ANNOUNCEMENT_ID"))
        announcementchannel = self.bot.get_channel(announcementchannel)
        twitchrequest = await apirequests.twitch(amazing)
        # If not live while code thinks stream is live
        if twitchrequest["stream"] == None and self.streamlive == True:
            self.streamlive = False
            logger.info("Amazing has gone offline")
        # If live while code thinks stream isn't live
        elif twitchrequest["stream"] != None and self.streamlive == False:
            announcement = random.choice(announcements)
            if announcements.index(announcement) == 11:
                with open("who-is-amazing.png", "rb") as f:
                    picture = discord.File(f)
                    await announcementchannel.send(content="@everyone https://www.twitch.tv/amazingx", file=picture)
            else:
                await announcementchannel.send(
                    "@everyone " + announcement + " https://www.twitch.tv/amazingx"
                )
            self.streamlive = True
            logger.info("Amazing has gone online")
        return

    @amazingStream.before_loop
    async def amazingStreamBefore(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5.0)
    async def amazingClips(self):
        clips_channel = int(os.getenv("AMAZING_CLIPS_CHANNEL"))
        clips_channel = self.bot.get_channel(clips_channel)
        clipsrequest = await apirequests.clips(amazing)
        if clipsrequest is None:
            return
        clips = clipsrequest["data"]
        clips_in_database = await database.getCurrentClips()
        for clip in clips:
            if clip["id"] in clips_in_database:
                pass
            else:
                clips_message = await clips_channel.send(f"A new clip has been created by {clip['creator_name']}\n{clip['url']}")
                await database.addClip(clip["id"], clips_message.id)
    
    @amazingClips.before_loop
    async def amazingClipsBefore(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_role(654107107171237908) #Mod role in Amazing Server
    async def removeclip(self, ctx, clip_id):
        clip_message_id = await database.getClipMessageID(clip_id)
        if len(clip_message_id) != 1:
            await ctx.send("Sorry, the clip_id you sent has returned more than one result. Please use a longer clip_id")
            return
        if clip_message_id[0] is None:
            await ctx.send("Sorry, the clip that you've requested does not have an associated message id. Please go manually delete it.")
            return
        clip_message = await ctx.fetch_message(clip_message_id[0])
        await clip_message.delete()

    # @tasks.loop(minutes=1.0)
    # async def amazingSubs(self):
    #     subsrequest = await apirequests.twitch_subs(amazing)
    #     logger.info(subsrequest)
    
    # @amazingSubs.before_loop
    # async def amazingSubsBefore(self):
    #     await self.bot.wait_until_ready()
    
    # #Automatic Sub Role
    # #Either subscribe to Subscription events or constantly check Subs via API
    # #When a new sub is detected, send them a random string and instruct them to send it to AmazingBot
    # #Once AmazingBot gets the message, store the discord-twitch relationship in a database and check every so often if people are still subscribed.
    
def setup(bot):
    bot.add_cog(Twitch(bot))
