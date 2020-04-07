from discord.ext import commands
import utils
import database as db
import discord
import asyncio
import sys
import importlib
import logging

logger = logging.getLogger("AmazingBot." + __name__)
sys.path.append("../database")


class Predictions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(db.checkDB())
        self.updating = False

    @commands.command(name="refreshcache")
    @commands.is_owner()
    async def refreshcache(self, ctx):
        importlib.reload(db)
        await ctx.send("DB Cache refreshed")

    @commands.group(pass_context=True, aliases=["Prediction", "predictions"])
    async def prediction(self, ctx):
        await db.checkdiscord(ctx)
        if self.updating == False:
            self.updating = True
            await db.updatematch(ctx)
            self.updating = False
        if ctx.invoked_subcommand == None:
            await ctx.send("Subcommands are pick, view, record and leaderboard")
        return

    @prediction.command(name="pick")
    async def pick(self, ctx):
        await db.checkdiscord(ctx)
        leagues_message = ""
        end_message = ""
        original_user = ctx.author.id
        reaction_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        leagues_list = ["LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
        for x in range(len(reaction_list)):
            leagues_message += f'{x+1}: {leagues_list[x]}\n'
        embed = discord.Embed(title="Predictions: League", color=0xA9152B)
        embed.add_field(name="Which League would you like to predict?", value=leagues_message, inline=False)
        msg = await ctx.send(embed=embed)
        react = await reaction_check(self, ctx, msg, original_user, reaction_list, embed)
        if isinstance(react, bool) is True:
            return
        league = leagues_list[reaction_list.index(react[0].emoji)]
        try:
            block_name, matches = await db.get_next_block_and_matches(league)
        except:
            await ctx.send(f"Unfortunately, {league} doesn't have any matches to predict. If you believe this is an error, ping Leo.")
        allowed_reactions = ["1️⃣", "2️⃣"]
        try:
            for x in range(len(matches)):
                team_1, team_2 = await db.fetchTeamIds(matches[x][1], matches[x][2])
                embed.title = f'Predictions: {league} {block_name} - {team_1} vs {team_2}'
                embed.set_field_at(0, name="Which team do you predict will win?", value=f'1: {team_1} \n2: {team_2}')
                await discord.Message.edit(msg, embed=embed)
                react = await reaction_check(self, ctx, msg, original_user, allowed_reactions, embed)
                if reaction_list.index(react[0].emoji) == 0:
                    await db.writePredictions(team_1, matches[x][0], original_user)
                    end_message += f'**{team_1}** vs {team_2}'
                else:
                    await db.writePredictions(team_2, matches[x][0], original_user)
                    end_message += f'{team_1} vs **{team_2}**'
        except:
            embed.set_field_at(0, name="Error", value=f'Unfortunately, {league} {block_name} is not able to be predicted yet. Once the entirity of teams in {block_name} is determined, you will be able to predict it')
            await discord.Message.edit(msg, embed=embed)
            return
        embed.title = f'Predictions: {league} {block_name}'
        embed.set_field_at(0, name="Your Predictions", value=end_message, inline=False)
        await discord.Message.edit(msg, embed=embed)
        await discord.Message.clear_reactions(msg)
        return

    @prediction.command(name="view")
    async def view(self, ctx):
        original_user = ctx.author.id
        leagues_message = ""
        leagues_list = ["LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
        predicted_leagues_names = []
        reaction_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        allowed_reactions = []
        blocks_msg = ""
        # Get all leagues where a user has ever made a prediction
        leagues_predicted = await db.fetchLeaguesPredicted(original_user)
        team_1_msg = ""
        team_2_msg = ""
        if leagues_predicted == None:
            await ctx.send("You have not made any predictions.")
            return
        for x in range(len(leagues_predicted)):
            leagues_message += str(x + 1) + ": " + leagues_list[leagues_predicted[x][0] - 1] + "\n"
            predicted_leagues_names.append(leagues_list[leagues_predicted[x][0] - 1])
            allowed_reactions.append(reaction_list[x])
        embed = discord.Embed(title="View predictions", color=0xA9152B)
        embed.add_field(
            name="Which league would you like to view your predictions in?", value=leagues_message, inline=False
        )
        msg = await ctx.send(embed=embed)
        react = await reaction_check(self, ctx, msg, original_user, allowed_reactions, embed)
        league = predicted_leagues_names[reaction_list.index(react[0].emoji)]
        # Get all blocks in a league that a user has made a prediction in. i.e Week 4, Week 5
        prediction_blocks = await db.fetchBlocksPredicted(original_user, league)
        allowed_reactions = []
        for x in range(len(prediction_blocks)):
            blocks_msg += str(x + 1) + ": " + prediction_blocks[x][0] + "\n"
            allowed_reactions.append(reaction_list[x])
        embed.title = league.upper() + " - Block Selection"
        embed.set_field_at(
            0, name="Which block would you like to view your predictions in?", value=blocks_msg, inline=False
        )
        await discord.Message.edit(msg, embed=embed)
        react = await reaction_check(self, ctx, msg, original_user, allowed_reactions, embed)
        block_name = prediction_blocks[reaction_list.index(react[0].emoji)][0]
        # Get a block of predictions in a league
        user_predictions = await db.fetchPredictions(original_user, league, block_name)
        for x in range(len(user_predictions)):
            # If Team 1 was the predicted team
            if user_predictions[x][0] == user_predictions[x][2]:
                team_1_msg += "**" + user_predictions[x][0] + "**\n"
                team_2_msg += user_predictions[x][1] + "\n"
            else:  # If Team 2 was the predicted team
                team_1_msg += user_predictions[x][0] + "\n"
                team_2_msg += "**" + user_predictions[x][1] + "**\n"
        embed.title = league.upper() + " - " + block_name + " Predictions"
        embed.set_field_at(0, name="Team 1", value=team_1_msg, inline=True)
        embed.add_field(name="Team 2", value=team_2_msg, inline=True)
        await discord.Message.edit(msg, embed=embed)
        await discord.Message.clear_reactions(msg)
        return

    @prediction.command(name="record")
    async def record(self, ctx):
        original_user = ctx.author.id
        leagues_message = "0: Overall\n"
        leagues_list = ["Overall", "LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
        reaction_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        allowed_reactions = ["0️⃣"]
        leagues_predicted = await db.fetchLeaguesPredicted(original_user)
        if leagues_predicted == None:
            await ctx.send("You have not made any predictions.")
            return
        for x in range(len(leagues_predicted)):
            leagues_message += str(x + 1) + ": " + leagues_list[leagues_predicted[x][0]] + "\n"
            allowed_reactions.append(reaction_list[x + 1])
        embed = discord.Embed(title="View predictions", color=0xA9152B)
        embed.add_field(name="Which League would you like to view your record in?", value=leagues_message, inline=False)
        msg = await ctx.send(embed=embed)
        await discord.Message.add_reaction(msg, reaction_list[0])
        react = await reaction_check(self, ctx, msg, original_user, allowed_reactions, embed)
        league = leagues_list[reaction_list.index(react[0].emoji)]
        block_name_msg, correct_pred_msg, wrong_pred_msg = await db.fetchCorrect(league, original_user)
        embed.title = "Prediction Record - " + league
        embed.set_field_at(0, name="Block", value=block_name_msg, inline=True)
        embed.add_field(name="Correct", value=correct_pred_msg, inline=True)
        embed.add_field(name="Incorrect", value=wrong_pred_msg, inline=True)
        await discord.Message.edit(msg, embed=embed)
        await discord.Message.clear_reactions(msg)
        return

    @prediction.command(name="leaderboard")
    async def leaderboard(self, ctx):
        original_user = ctx.author.id
        leagues_list = ["Overall", "LCS", "LEC", "LCK", "LPL", "OCE-OPL", "CBLOL", "TCL", "LJL", "LCSA"]
        reaction_list = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        users_msg = ""
        record_msg = ""
        rank_msg_array = []
        rank_msg = ""
        leagues_message = ""
        for x in range(len(leagues_list)):
            leagues_message += str(x) + ": " + leagues_list[x] + "\n"
        embed = discord.Embed(title="Predictions Leaderboard", color=0xA9152B)
        embed.add_field(
            name="Which League would you like to view the leaderboard in?", value=leagues_message, inline=False
        )
        msg = await ctx.send(embed=embed)
        react = await reaction_check(self, ctx, msg, original_user, reaction_list, embed)
        league = leagues_list[reaction_list.index(react[0].emoji)]
        leaderboard_users, leaderboard_records = await db.fetchLeaderboard(league)
        for x in range(len(leaderboard_users)):
            if x == 0:
                rank_msg_array.append(str(x + 1))
            else:
                if leaderboard_records[x] == leaderboard_records[x - 1]:
                    rank_msg_array.append(rank_msg_array[-1])
                else:
                    rank_msg_array.append(str(x + 1))
            if ctx.guild.get_member(leaderboard_users[x]) is None:
                users_msg += 'User has left the server\n'
            else:
                users_msg += ctx.guild.get_member(leaderboard_users[x]).display_name + "\n"
            record_msg += leaderboard_records[x] + "\n"
        for x in range(len(rank_msg_array)):
            rank_msg += await utils.integerPrefix(rank_msg_array[x]) + "\n"
        embed.title = "Prediction Leaderboard - " + league
        embed.set_field_at(0, name="Rank", value=rank_msg, inline=True)
        embed.add_field(name="User", value=users_msg, inline=True)
        embed.add_field(name="Record", value=record_msg, inline=True)
        await discord.Message.edit(msg, embed=embed)
        await discord.Message.clear_reactions(msg)
        return

    @prediction.command(name="update")
    @commands.has_any_role("Moderators", "Bot Tester")
    async def update(self, ctx):
        try:
            update_check = await db.updatematch(ctx)
            if update_check != False:
                await ctx.send("Update Match didn't crash")
        except:
            await ctx.send("There was an error")
        return


async def reaction_check(self, ctx, msg, original_user, allowed_reactions, embed):
    for x in range(len(allowed_reactions)):
        await discord.Message.add_reaction(msg, allowed_reactions[x])

    def check(reaction, user):
        return user.id == original_user and reaction.emoji in allowed_reactions and reaction.message.id == msg.id

    try:
        react = await self.bot.wait_for(event="reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        embed.set_field_at(0, name="Timeout", value="Predictions have timed out. Please try again", inline=False)
        await discord.Message.edit(msg, embed=embed)
        await discord.Message.clear_reactions(msg)
        return False
    await discord.Message.clear_reactions(msg)
    return react


def setup(bot):
    bot.add_cog(Predictions(bot))
