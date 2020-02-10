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

	@commands.command(name="temp")
	async def temp(self, ctx, temper = None):
		if temper == None:
			await ctx.send("Usage: -temp [temperature]. For example: -temp 14F will return -10C")
			return
		try:
			if temper[-1] == "F":
				temper = ((float(temper[:-1]) - 32) * (5/9))
				await ctx.send(str(temper) + "C")
			elif temper[-1] == "C":
				temper = ((float(temper[:-1])) * (9/5) + 32)
				await ctx.send(str(temper) + "F")
			else:
				await ctx.send("Invalid request")
		except:
			await ctx.send("An error occurred. This is likely due to the fact that you have a non-numerical character in your request (excluding the trailing F/C)")
			
		
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
