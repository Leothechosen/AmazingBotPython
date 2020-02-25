import discord
import asyncio
import math
from discord.ext import commands


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll")
    async def poll(self, ctx, *, arguments=None):
        if arguments == None:
            await ctx.send(
                "Usage: `-poll [Question], [Answer1], [Answer2], ..., [Answer9], [Time in Seconds (Max: 300)]`"
            )
            return
        reaction_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        answers = ""
        answers_vote = ""
        arguments = arguments.split(",", 10)
        for x in range(len(arguments)):
            arguments[x] = arguments[x].strip()
        question = arguments[0].title()
        remainingseconds = 0
        timeremaining = 0
        try:
            int(arguments[-1])
        except ValueError:
            await ctx.send(
                "The last argument sent needs to be an integer indicating how long the poll should last in seconds (Max:300, rounded to the nearest 5 otherwise)"
            )
        if int(arguments[-1]) > 300:
            await ctx.send("Poll timer has been set to the maximum value of 300 seconds")
            remainingseconds = 300
        else:
            # Rounds to a multple of 5
            remainingseconds = round(int(arguments[-1]) / 5) * 5
        del arguments[-1]
        if question[-1] != "?":
            question += "?"
        for x in range(len(arguments)):
            if x == 0:
                continue
            else:
                answers += str(x) + ": " + arguments[x].title() + "\n"
        embed = discord.Embed(title="Question: " + question, color=0xA9152B)
        embed.add_field(name="Answers", value=answers, inline=True)
        if remainingseconds >= 60:
            timeremaining = str(int(remainingseconds / 60)) + " minutes, " + str(remainingseconds % 60) + " seconds"
        else:
            timeremaining = str(remainingseconds % 60) + " seconds"
        embed.add_field(name="Time Remaining", value=timeremaining, inline=False)
        msg = await ctx.send(embed=embed)
        for x in range(len(arguments)):
            if x == len(arguments) - 1:
                continue
            else:
                await discord.Message.add_reaction(msg, reaction_list[x])
        while remainingseconds != "done":
            if remainingseconds <= 0:
                embed.set_field_at(1, name="Time Remaining", value="Poll has finished", inline=False)
                await discord.Message.edit(msg, embed=embed)
                msg = await discord.User.fetch_message(ctx.channel, msg.id)
                reactors = {}
                for react in msg.reactions:
                    if react.emoji in reaction_list:
                        reactors.setdefault(react.count, [])
                        reactors[react.count].append(react.emoji)
                max_reacts = max(reactors, key=int)
                if len(reactors[max_reacts]) != 1:
                    if max_reacts == 1:
                        tie_message = "There were no votes cast"
                    else:
                        tie_message = 'There was a tie between: "'
                        for x in range(len(reactors[max_reacts])):
                            if x != len(reactors[max_reacts]) - 1:
                                tie_message += arguments[reaction_list.index(reactors[max_reacts][x]) + 1] + '" and "'
                            else:
                                tie_message += arguments[reaction_list.index(reactors[max_reacts][x]) + 1] + '"'
                    embed.add_field(name="Tie!", value=tie_message, inline=False)
                else:
                    embed.add_field(
                        name="Winner",
                        value=arguments[reaction_list.index(reactors[max_reacts][0]) + 1] + " wins!",
                        inline=False,
                    )
                for x in range(len(msg.reactions)):
                    if msg.reactions[x].emoji in reaction_list:
                        if msg.reactions[x].count == 2:
                            answers_vote += str(msg.reactions[x].count - 1) + " vote\n"
                        else:
                            answers_vote += str(msg.reactions[x].count - 1) + " votes\n"
                embed.insert_field_at(1, name="Votes", value=answers_vote, inline=True)
                await discord.Message.edit(msg, embed=embed)
                await discord.Message.clear_reactions(msg)
                remainingseconds = "done"
            else:
                timeremaining = 0
                if remainingseconds >= 60:
                    timeremaining = (
                        str(int(remainingseconds / 60)) + " minutes, " + str(remainingseconds % 60) + " seconds"
                    )
                else:
                    timeremaining = str(remainingseconds % 60) + " seconds"
                embed.set_field_at(1, name="Time Remaining", value=timeremaining, inline=False)
                await discord.Message.edit(msg, embed=embed)
                remainingseconds -= 5
                await asyncio.sleep(5)


def setup(bot):
    bot.add_cog(Poll(bot))
