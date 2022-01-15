from discord.ext import commands
from paginator import Pages
import discord
import asyncio
import itertools
from datetime import datetime
import logging
import database
import psutil
import utils
import apirequests


logger = logging.getLogger("AmazingBot." + __name__)


class HelpPaginator(Pages):
    def __init__(self, help_command, ctx, entries, *, per_page=4):
        super().__init__(ctx, entries=entries, per_page=per_page)
        self.reaction_emojis.append(('\N{WHITE QUESTION MARK ORNAMENT}', self.show_bot_help))
        self.total = len(entries)
        self.help_command = help_command
        self.prefix = help_command.clean_prefix
        self.is_bot = False

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title = f'{cog} Commands'
        self.description = description
        return commands

    def prepare_embed(self, entries, page, *, first=False):
        self.embed.clear_fields()
        self.embed.description = self.description
        self.embed.title = self.title

        if self.is_bot:
            value ='For more help, join the official bot support server: https://discord.gg/N35Mqun'
            self.embed.add_field(name='Support', value=value, inline=False)

        self.embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')

        for entry in entries:
            signature = f'{entry.qualified_name} {entry.signature}'
            self.embed.add_field(name=signature, value=entry.short_doc or "No help given", inline=False)

        if self.maximum_pages:
            self.embed.set_author(name=f'Page {page}/{self.maximum_pages} ({self.total} commands)')

    async def show_help(self):
        """shows this message"""

        self.embed.title = 'Paginator help'
        self.embed.description = 'Hello! Welcome to the help page.'

        messages = [f'{emoji} {func.__doc__}' for emoji, func in self.reaction_emojis]
        self.embed.clear_fields()
        self.embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)

        self.embed.set_footer(text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def show_bot_help(self):
        """shows how to use the bot"""

        self.embed.title = 'Using the bot'
        self.embed.description = 'Hello! Welcome to the help page.'
        self.embed.clear_fields()

        entries = (
            ('<argument>', 'This means the argument is __**required**__.'),
            ('[argument]', 'This means the argument is __**optional**__.'),
            ('[A|B]', 'This means the it can be __**either A or B**__.'),
            ('[argument...]', 'This means you can have multiple arguments.\n' \
                              'Now that you know the basics, it should be noted that...\n' \
                              '__**You do not type in the brackets!**__')
        )

        self.embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

        for name, value in entries:
            self.embed.add_field(name=name, value=value, inline=False)

        self.embed.set_footer(text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user),
            'help': 'Shows help about the bot, a command, or a category'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        def key(c):
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = 0

        for cog, commands in itertools.groupby(entries, key=key):
            commands = sorted(commands, key=lambda c: c.name)
            if len(commands) == 0:
                continue

            total += len(commands)
            actual_cog = bot.get_cog(cog)
            # get the description if it exists (and the cog is valid) or return Empty embed.
            description = (actual_cog and actual_cog.description) or discord.Embed.Empty
            nested_pages.extend((cog, description, commands[i:i + per_page]) for i in range(0, len(commands), per_page))

        # a value of 1 forces the pagination session
        pages = HelpPaginator(self, self.context, nested_pages, per_page=1)

        # swap the get_page implementation to work with our nested pages.
        pages.get_page = pages.get_bot_page
        pages.is_bot = True
        pages.total = total
        #await self.context.release()
        await pages.paginate()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f'{cog.qualified_name} Commands'
        pages.description = cog.description

        #await self.context.release()
        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        page_or_embed.title = self.get_command_signature(command)
        if command.description:
            page_or_embed.description = f'{command.description}\n\n{command.help}'
        else:
            page_or_embed.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)

        #await self.context.release()
        await pages.paginate()

class Meta(commands.Cog):
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self
    
    @commands.command(name="avatar")
    async def avatar(self, ctx):
        """Returns the fullsize version of the bot's avatar, made by `@owocifer` on twitter"""
        embed = discord.Embed(title="Avatar", color=0xA9152B)
        embed.set_image(url="https://i.imgur.com/TwEsQ4D.png")
        embed.add_field(
            name="Info",
            value="AmazingBot's Avatar was made by Sel.\n https://twitter.com/owocifer \n https://www.instagram.com/sel.bro",
            inline=False,
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="sourcecode", aliases=["github"])
    async def sourcecode(self, ctx):
        """Returns a link to AmazingBot's github"""
        try:
            githubrequest = await apirequests.github()
            last_commit_time = str(
                datetime.strptime(githubrequest[0]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
            )
            last_commit_msg = githubrequest[0]["commit"]["message"]
            embed = discord.Embed(title="AmazingBot Source Code", color=0xA9152B)
            embed.add_field(name="Link", value="https://github.com/Leothechosen/AmazingBotPython", inline=False)
            embed.add_field(name="Last commit - " + last_commit_time + " UTC", value=last_commit_msg, inline=False)
            embed.set_footer(icon_url="https://i.imgur.com/TwEsQ4D.png", text="Created on 2020-01-06 at 05:55:11 UTC")
            await ctx.send(embed=embed)
            return
        except Exception as e:
            logging.error(e)
            return

    @commands.command(name="bugreport", aliases=["bug"])    
    async def bug_report(self, ctx, *args):
        """If you see what you believe to be unintentional behavior, please report it through this command"""
        if args == ():
            await ctx.send("Usage: `-bugreport [message]`")
            return
        owner = self.bot.get_user(self.bot.owner_id)
        if ctx.guild == None:
            await owner.send(f"Error reported by {ctx.author} in a DM: {ctx.message.content}")
        else:
            await owner.send(f"Error reported by {ctx.author} in {ctx.guild}: {ctx.message.content}")
        await ctx.send("Your report has been sent, thank you.")

    @commands.command(name="suggestion")
    async def suggestion(self, ctx, *args):
        """If you have a suggestion on what else this bot should do, send it through this command"""
        if args == ():
            await ctx.send("Usage: `-suggestion [message]`")
            return
        owner = self.bot.get_user(self.bot.owner_id)
        if ctx.guild == None:
            await owner.send(f"Suggestion from {ctx.author} in a DM: {ctx.message.content}")
        else:
            await owner.send(f"Suggestion by {ctx.author} in {ctx.guild}: {ctx.message.content}")
        await ctx.send("Your suggestion has been sent, thank you.")
    
    @commands.command(name="status", hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, status):
        """Owner Only | Sets the bot's status in Discord"""
        if status == "none":
            await self.bot.change_presence(activity=None)
            await ctx.send("Status deleted")
        elif status == "default":
            await self.bot.change_presence(activity=discord.Game("Created by Leo"))
            await ctx.send("Status is now `Created By Leo`")
        else:
            await self.bot.change_presence(activity=discord.Game(status))
            await ctx.send(f"Status is now {status}")
        return

    @commands.command(name="botinfo")
    async def botinfo(self, ctx):
        """Returns some of AmazingBot's information"""
        embed = discord.Embed(title="AmazingBot Info", color=0xA9152B)
        embed.add_field(name="Uptime", value= str(datetime.now() - self.bot.uptimeStart)[:-7], inline = True)
        embed.add_field(name="Created On", value = "2019-12-28", inline=True)
        embed.add_field(name="** **", value = "** **", inline=True)
        embed.add_field(name="Guilds Serving", value = len(self.bot.guilds), inline=True)
        embed.add_field(name="Users Serving", value = len(self.bot.users), inline=True)
        embed.add_field(name="** **", value = "** **", inline=True)
        embed.add_field(name="Bot Invite Link", value="https://discordapp.com/api/oauth2/authorize?client_id=660329366940680227&permissions=8&scope=bot", inline=True)
        embed.set_footer(text="Created By Leo឵#8788", icon_url="https://i.imgur.com/SGmbIdj.png")
        embed.set_thumbnail(url="https://i.imgur.com/TwEsQ4D.png")
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Returns some of the server's information"""
        features = [f'{feature}\n' for feature in ctx.guild.features]
        prefix = await database.getGuildPrefix(ctx.guild.id)
        if prefix:
            embed = discord.Embed(title=f"{ctx.guild.name}'s Info", description=f"Server prefix: {prefix[0]}", color = 0xA9152B)
        else:
            embed = discord.Embed(title=f"{ctx.guild.name}'s Info", description=f"Server prefix: -", color = 0xA9152B)
        embed.add_field(name="Region", value=str(ctx.guild.region).title(), inline=True)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(name="Created On", value=str(ctx.guild.created_at)[:-7], inline=True)
        embed.add_field(name="Features", value = f"{features}", inline=True)
        embed.add_field(name="# of Members", value=f"{ctx.guild.member_count}", inline=True)
        embed.add_field(name="# of Boosts", value=f"{ctx.guild.premium_subscription_count}", inline=True)
        try:
            if ctx.guild.is_icon_animated():    
                embed.set_thumbnail(url=ctx.guild.icon_url_as(format="gif"))
            else:
                embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
        except:
            pass
        await ctx.send(embed=embed)

    @commands.command(name="systeminfo")
    async def systeminfo(self, ctx):
        """Returns system info"""
        cpu_msg = ""
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            cpu_msg += f"Core {i}: {percentage}%\n"
        sys_mem = psutil.virtual_memory()
        sys_mem_total = await utils.get_size(sys_mem.total)
        sys_mem_used = await utils.get_size(sys_mem.used)
        sys_mem_perc = f"{sys_mem.percent}%"
        embed = discord.Embed(title="AmazingBot System Info", color=0xA9152B)
        embed.add_field(name="CPU usage", value = cpu_msg, inline=True)
        embed.add_field(name="RAM usage", value = f"{sys_mem_used} / {sys_mem_total} ({sys_mem_perc})", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="guilds", hidden=True)
    @commands.is_owner()
    async def guilds(self, ctx):
        """Returns guilds that the bot is in"""
        guild_msg = ""
        members_msg = ""
        for guild in self.bot.guilds:
            guild_msg += f"{guild}\n"
            members_msg += f"{guild.member_count}\n"
        embed = discord.Embed(title="Guilds AmazingBot Is In", color=0xA9152B)
        embed.add_field(name="Guild Name", value = guild_msg, inline=True)
        embed.add_field(name="# of Members", value = members_msg, inline=True)
        await ctx.send(embed=embed)
        return

    
    

def setup(bot):
    bot.add_cog(Meta(bot))