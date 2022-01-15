import discord
from discord.ext import commands, tasks

import random
import asyncio
import logging

logger = logging.getLogger("AmazingBot." + __name__)

class Drinking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.card_desc = {"2": "For You - Pick someone to have 2 drinks",
                          "3": "For Me - Take 3 drinks yourself",
                          "4": "Floor - Point to the floor. Last one drinks",
                          "5": "Guys - All the fellas, have a drink",
                          "6": "Chicks - All the ladies, have a drink",
                          "7": "Heaven - Last to point up drinks",
                          "8": "Mate - Choose someone to drink when you do",
                          "9": "Rhyme - Pick a word. Everyone takes turns rhyming with it",
                          "10": "Categories - Pick a category. Everyone takes turns saying a word relating to it",
                          "Jack": "Never Have I Ever - First to put 3 fingers down loses. Drink for every finger.",
                          "Queen": "Question Master - Anytime you ask a question, everyone that answers drinks",
                          "King": "Invent a rule -  Make up a new rule that's valid until the end of the game",
                          "Ace": "Waterfall - Everyone drink. You cant stop until the person before you stops"
                         }
        self.players = []
        self.existing_game = False

    @commands.command(name='startdrinking')
    async def startdrinking(self, ctx):
        if self.existing_game == True:
            await ctx.send(f"There is already a game in progress. Type `{ctx.prefix}join` to play")
            return
        self.existing_game = True
        msg = await ctx.send(f"{ctx.author} wants to play the Kings Cup drinking game. Type `{ctx.prefix}join` to play. The game will start when there's at least 2 players.")
        self.text_channel = ctx.channel
        self.players.append(ctx.author)
        times_looped = 0
        while len(self.players) < 2 and times_looped < 300:
            times_looped += 1
            await asyncio.sleep(1)
        if times_looped >= 300:
            await ctx.send(f"Not enough players have joined.")
            await msg.delete()
            return
        await self.game()

    @commands.command(name='join')
    async def join(self, ctx):
        if self.existing_game == True:
            if ctx.author in self.players:
                await ctx.send("You're already in this game!")
                return
            self.players.append(ctx.author)
            await ctx.send(f"{ctx.author}, you have been added to the game.")
        else:
            await ctx.send(f"There is no game occuring.")

    async def game(self):
        draw_emoji = "✅"
        self.deck = ["2", "2", "2", "2",
                     "3", "3", "3", "3",
                     "4", "4", "4", "4",
                     "5", "5", "5", "5",
                     "6", "6", "6", "6",
                     "7", "7", "7", "7",
                     "8", "8", "8", "8",
                     "9", "9", "9", "9",
                     "10", "10", "10", "10",
                     "Jack", "Jack", "Jack", "Jack",
                     "Queen", "Queen", "Queen", "Queen",
                     "King", "King", "King", "King",
                     "Ace", "Ace", "Ace", "Ace"]
        house_rules = ""
        linked_players = ""
        question_masters = ""
        player_index = 0
        while len(self.players) >= 2 and len(self.deck) != 0:
            logger.info(self.deck)
            logger.info(self.players)
            embed = discord.Embed(title="Kings Cup Game", description=f'Cards remaining: {len(self.deck)}')
            if player_index > len(self.players)-1:
                player_index = 0
            current_player = self.players[player_index]
            player_index += 1
            embed.add_field(name=f"Turn", value=f"{current_player.mention}: Press {draw_emoji} to draw your card", inline=False)
            embed.add_field(name=f"House Rules", value=f'{house_rules if house_rules != "" else "None yet!"}', inline=False)
            embed.add_field(name=f"Linked Players", value=f'{linked_players if linked_players != "" else "None yet!"}', inline=False)
            embed.add_field(name=f"Question Masters", value=f'{question_masters if question_masters != "" else "None yet!"}', inline=False)
            msg = await self.text_channel.send(embed=embed)
            react = await self.reaction_check(msg, current_player, draw_emoji)
            if react == "Timeout":
                continue
            drawn_card = random.choice(self.deck)
            self.deck.remove(drawn_card)
            if drawn_card == "8":
                reaction_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                choosable_players = [player for player in self.players if player != current_player]
                choosable_players_msg = ""
                for player in choosable_players:
                    choosable_players_msg += f"{reaction_list[choosable_players.index(player)]}: {player}\n"
                embed.set_field_at(0, name=f"Turn", value=f"{current_player.mention} drew a {drawn_card} {self.card_desc.get(drawn_card)}\n\n{current_player.mention}, select the player you want to link to you.\n{choosable_players_msg}")
                embed.description = f"Cards remaining: {len(self.deck)}"
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                react = await self.reaction_check(msg, current_player, reaction_list[0:len(choosable_players)])
                if react == "Timeout":
                    chosen_player = random.choice(choosable_players)
                    embed.set_field_at(0, name ="Turn", value=f"{player.mention} did not choose a player. Therefore, a random player has been chosen. {chosen_player.mention} will now drink whenever {player.mention} drinks.")
                else:
                    chosen_player = choosable_players[reaction_list.index(react[0].emoji)]
                    embed.set_field_at(0, name=f"Turn", value=f"{chosen_player} now has to drink whenever {current_player} does.")
                linked_players += f"{current_player} - {chosen_player}"
                embed.set_field_at(2, name=f"Linked Players", value=f'{linked_players}')
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                await asyncio.sleep(10)
                await msg.delete()
            elif drawn_card == "Queen":
                question_masters += f"{current_player}\n"
                embed.set_field_at(3, name="Question Masters", value=question_masters, inline=False)
                embed.set_field_at(0, name="Turn", value=f"{current_player.mention} drew a {drawn_card}!\n{self.card_desc.get(drawn_card)}\n\n")
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                await asyncio.sleep(10)
                await msg.delete()
            elif drawn_card == "King":
                embed.set_field_at(0, name=f"Turn", value=f"{current_player.mention} drew a {drawn_card}!\n{self.card_desc.get(drawn_card)}\n\n{current_player.mention}, send a rule that you make up!")
                embed.description = f"Cards remaining: {len(self.deck)}"
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                new_rule = await self.message_check(self.text_channel, current_player)
                house_rules += f"{current_player}: {new_rule.clean_content}\n"
                embed.set_field_at(0, name=f"Turn", value=f"{current_player.mention} made a new rule: {new_rule.clean_content}")
                embed.set_field_at(1, name=f"House Rules", value=f'{house_rules}')
                await new_rule.delete()
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                await asyncio.sleep(10)
                await msg.delete()
            else:
                embed.set_field_at(0, name=f"Turn", value=f"{current_player.mention} drew a {drawn_card}! **{self.card_desc.get(drawn_card)}**")
                embed.description = f"Cards remaining: {len(self.deck)}"
                await msg.delete()
                msg = await self.text_channel.send(embed=embed)
                await asyncio.sleep(10)
                await msg.delete()
        embed.clear_fields()
        if len(self.deck) == 0:
            embed.add_field(name=f"The game is over!", value="The deck has run out of cards.")
        else:
            embed.add_field(name=f"The game has ended", value="There are not enough players to continue the game.")
        await self.text_channel.send(embed=embed)

    async def reaction_check(self, msg, player, allowed_reactions):
        for x in range(len(allowed_reactions)):
            await discord.Message.add_reaction(msg, allowed_reactions[x])
        
        def check(reaction, user):
            return user.id == player.id and reaction.emoji in allowed_reactions and reaction.message.id == msg.id

        try:
            react = await self.bot.wait_for(event="reaction_add", timeout=600.0, check=check)
        except asyncio.TimeoutError:
            return "Timeout"
        await discord.Message.clear_reactions(msg)
        return react

    async def message_check(self, channel, player):
        def check(m):
            return m.author == player and m.channel == channel

        msg = await self.bot.wait_for('message', timeout=600.0, check=check)
        return msg


def setup(bot):
    bot.add_cog(Drinking(bot))

# 2 - "For You" - Pick someone to have 2 drinks
# 3 - "For me" - Take 3 drinks yourself
# 4 - "Floor" - Point to the Floor! Last one drinks
# 5 - "Guys" - All the fellas, have a drink
# 6 - "Chicks" - All the ladies, have a drink
# 7 - "Heaven" - Last to point up drinks
# 8 - "Mate" - Choose osmeone to drink when you do
# 9 - "Rhyme" - Pick a word. Everyone takes turns rhyming with it
# 10 - "Categories" - Like Rhyme, but pick a category
# J - "Never have I ever" - First to put 3 fingers down loses. Drink for every finger
# Q - "Question Master" - Anytime you ask a question, everyone that answers drinks
# K - "Invert a rule" - Make up a new rule that's valid until the end of the game
# A - "Waterfall" - "Everyone drink. You cant stop until the person before you stops"