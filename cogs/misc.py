import discord
import asyncio
import os
from pytz import timezone
from datetime import datetime, timedelta
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
amazingserverid = int(os.getenv('AMAZING_SERVER_ID'))
servertimechannel = int(os.getenv('SERVER_TIME_CHANNEL'))
class Misc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		print("AmazingBot connected to Discord")
		await theserverTime(self)
	
	@commands.command(name='sourcecode', help = "Links the source code to how I work!")
	async def sourcecode(self, ctx):
		await ctx.send("https://www.github.com/Leothechosen/AmazingBotPython")	
	
	@commands.command(name='restartservertime')
	@commands.has_role("Moderators")
	async def restartservertime(self, ctx):
		await ctx.send("Restarting the clock...")
		await theserverTime(self)
		
async def theserverTime(self):
	minutecheck = datetime.now(timezone('CET'))
	fmt = '%H:%M %Z'
	fmt2 ='%s'
	minutecheck = minutecheck.strftime(fmt2)
	minutecheck = int(minutecheck)
	minutecheck = minutecheck % 60
	minutecheck = 61 - minutecheck
	await asyncio.sleep(minutecheck)
	while True:
		guild = self.bot.get_guild(id = amazingserverid)
		servertime = self.bot.get_channel(id = servertimechannel)
		berlin = datetime.now(timezone('CET'))
		berlin = berlin.strftime(fmt)
		await servertime.edit(name = berlin)			
		await asyncio.sleep(60)
		
def setup(bot):
	bot.add_cog(Misc(bot))
