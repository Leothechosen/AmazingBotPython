from tkinter import N
from discord.ext import commands
import utils
import database as db
import discord
import asyncio
import sys
import importlib
import logging

logger = logging.getLogger("AmazingBot." + __name__)

class Pickems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(db.checkDB())
        self.updating = False

    @commands.command(name="refreshcache", hidden=True)
    @commands.is_owner()
    async def refreshcache(self, ctx):
        """Reloads the AmazingBot Database"""
        importlib.reload(db)
        await ctx.send("DB Cache refreshed")

    @commands.group(aliases=["Pickem", "pickem", "Pickems"])
    async def pickems(self, ctx):
        """League of Legends | Subcommands are pick, view, record, and leaderboard
        Allows users to predict upcoming matches and keep track of Correct/Wrong Predictions"""
        await db.checkdiscord(ctx)
        if not self.updating:
            self.updating = True
            await db.updatematch(ctx)
            self.updating = False
        if ctx.invoked_subcommand == None:
            option_chosen = None
            view = self.PickemsOptionsView()
            msg = await ctx.send(content="Pick which option you would like to do.", view=view)
            await view.wait()
            if option_chosen is None:
                await self.pickems_timeout(msg)
            elif option_chosen == "pick":
                await self.pick(ctx)
            elif option_chosen == "view":
                await self.view(ctx)
            elif option_chosen == "record":
                await self.record(ctx)
            elif option_chosen == "leaderboard":
                await self.leaderboard(ctx)
        return


    @pickems.command(name="pick")
    async def pick(self, ctx, league=None):
        try:
            await db.checkdiscord(ctx)
            league_chosen = None
            leagues_list = ["LCS", "LEC", "LCK", "LPL", "CBLOL", "TCL", "LJL"]
            if league is None or league not in leagues_list:
                view = self.LeaguesView()
            msg = await ctx.send(content=f"{ctx.author}: Pick the league you want to predict.", view=view)
            await view.wait()
            league_chosen = view.league_chosen
            logger.info(f"{ctx.author} has picked {league_chosen}")
            if league_chosen is None:
                await self.pickems_timeout(msg)
                return
            embed = discord.Embed(title=f"Pickems: {league_chosen}")
            embed.add_field(name="Processing", value = "One moment...")
            msg = await msg.edit(content=None, embed=embed, view=None)
            block_name, matches = await db.get_next_block_and_matches(league)
            matches_msg = ""
            picks_msg = ""
            for x in range(len(matches)):
                team_1, team_2 = await db.fetchTeamIds(matches[x][1], matches[x][2])
                team_1_button = self.TeamButton(team_1, discord.ButtonStyle.blurple)
                team_2_button = self.TeamButton(team_2, discord.ButtonStyle.red)
                view = self.MatchesView(team_1_button, team_2_button)
                await msg.edit("Pick which team you think will win", embed=None, view=view)
                await view.wait()
                if view.pick == None:
                    await self.pickems_timeout(msg)
                else:
                    await db.writePredictions(view.pick, matches[x][0], ctx.author.id)
                    matches_msg += f"{team_1} vs {team_2}\n"
                    picks_msg += f"{view.pick}\n"
            embed = discord.Embed(title=f"Pickems: {league_chosen} - {block_name}")
            embed.add_field(name="Matches", value=matches_msg, inline=True)
            embed.add_field(name="Picks", value=picks_msg, inline=True)
            await msg.edit(content=None, embed=embed, view=None)
        except:
            embed = discord.Embed(title=f"Pickems Error")
            embed.add_field(name="Error", value="Sorry, there has been an unexpected error. This has been logged and sent to the bot owner.")
            await msg.edit(content=None, embed=embed, view=None)
            return

    @pickems.command(name="view")
    async def view(self, ctx):
        view = self.LeaguesView()
        leagues_predicted = await db.fetchLeaguesPredicted(ctx.author.id)
        if leagues_predicted is None:
            await ctx.send("You have not made any predictions")
            return
        for child in view.children:
            if child.label not in leagues_predicted:
                child.disabled = True
        msg = await ctx.send(content=f"{ctx.author}: Pick which league you would like to view your predictions in", view=view)
        await view.wait()
        league_chosen = view.league_chosen if view.league_chosen else None
        if league_chosen is None:
            await self.pickems_timeout(msg)
            return
        predicted_blocks = await db.fetchBlocksPredicted(ctx.author.id, view.league_chosen)
        if len(predicted_blocks) > 1:
            buttons = [self.BlockButton(block) for block in predicted_blocks]
            view = self.BlockOptionsView(buttons)
            await msg.edit(content=f"{ctx.author}: Pick which block you would like to view your predictions in for the {league_chosen}", view=view)
            await view.stop()
            block_chosen = view.block_chosen
        else:
            block_chosen = predicted_blocks[0]
        user_predictions = await db.fetchPredictions(ctx.author.id, league_chosen, block_chosen)
        team_1_msg = ""
        team_2_msg = ""
        for x in range(len(user_predictions)):
            if user_predictions[x][0] == user_predictions[x][2]:
                team_1_msg += f"**{user_predictions[x][0]}**\n"
                team_2_msg += f"{user_predictions[x][1]}\n"
            else:
                team_1_msg += f"{user_predictions[x][0]}\n"
                team_2_msg += f"**{user_predictions[x][0]}**\n"
        embed = discord.Embed(title=f"{league_chosen} - {block_chosen} Predictions")
        embed.add_field(name="Team 1", value=team_1_msg, inline=True)
        embed.add_field(name="Team 2", value=team_2_msg, inline=True)
        await msg.edit(content=None, embed=embed, view=None)
        return

    @pickems.command(name="record")
    async def record(self, ctx, league=None):
        pass

    @pickems.command(name="leaderboard")
    async def leaderboard(self, ctx, league=None):
        pass

    class LeaguesView(discord.ui.View):
        def __init__(self, *, timeout=60.0):
            super().__init__(timeout=timeout)
            self.league_chosen = None
    
        @discord.ui.button(label="LCS")
        async def LCS(self, button, interaction):
            self.league_chosen = "LCS"
            self.stop()
        
        @discord.ui.button(label="LEC")
        async def LEC(self, button, interaction):
            self.league_chosen = "LEC"
            self.stop()
        
        @discord.ui.button(label="LCK")
        async def LCK(self, button, interaction):
            self.league_chosen = "LCK"
            self.stop()

        @discord.ui.button(label="CBLOL")
        async def CBLOL(self, button, interaction):
            self.league_chosen = "CBLOL"
            self.stop()
        
        @discord.ui.button(label="TCL")
        async def TCL(self, button, interaction):
            self.league_chosen = "TCL"
            self.stop()

        @discord.ui.button(label="LJL")
        async def LJL(self, button, interaction):
            self.league_chosen = "LJL"
            self.stop()

    class MatchesView(discord.ui.View):
        def __init__(self, team1button, team2button):
            super().__init__(timeout=60)
            self.add_item(team1button)
            self.add_item(team2button)
            self.pick = None

    class TeamButton(discord.ui.Button):
        def __init__(self, label, style):
            super().__init__(style=style, label=label, custom_id=label)
        
        async def callback(self, interaction):
            self.view.pick = interaction.data['custom_id']
            self.view.stop()
    
    class PickemsOptionsView(discord.ui.View):
        def __init__(self, *, timeout=60.0):
            super().__init__(timeout=timeout)
            self.option_picked = None

        @discord.ui.button(label="Pick")
        async def pick_button(self, button, interaction):
            self.option_picked = "pick"
            self.stop()

        @discord.ui.button(label="View")
        async def view_button(self, button, interaction):
            self.option_picked = "view"
            self.stop()

        @discord.ui.button(label="Record")
        async def record_button(self, button, interaction):
            self.option_picked = "record"
            self.stop()

        @discord.ui.button(label="Leaderboard")
        async def leaderboard_button(self, button, interaction):
            self.option_picked = "leaderboard"
            self.stop()

    class BlockButton(discord.ui.Button):
        def __init__(self, label):
            super().__init__(style=discord.ButtonStyle.primary, label=label, custom_id=label)
        
        async def callback(self, interaction):
            self.view.block_chosen = interaction.data["custom_id"]
            self.view.stop()
    
    class BlockOptionsView(discord.ui.View):
        def __init__(self, *buttons):
            super().__init__(timeout=60)
            for button in buttons:
                self.add_item(button)
            self.block_chosen = None

    async def pickems_timeout(self, msg):
        embed = discord.Embed(title="Pickems")
        embed.add_field(name="Timeout", value="This interaction has timed out. Please try again.")
        await msg.edit(content=None, embed=embed, view=None)
        return
