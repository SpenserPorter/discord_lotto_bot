import discord
import random
import lotto_dao as db
import asyncio
from discord.ext import commands

outside_dict = {'red':([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],2),
                'black':([2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35],2),
                'even':(range(2,37,2),2),
                'odd':(range(1,36,2),2),
                '1-18':(range(1,19),2),
                '19-36':(range(19,37),2),
                '1st':([1,4,7,10,13,16,19,22,25,28,31,34],3),
                '2nd':([2,5,8,11,14,17,20,23,26,29,32,35],3),
                '3rd':([3,6,9,12,15,18,21,24,27,30,33,36],3),
                '1-12':(range(1,13),3),
                '13-24':(range(13,25),3),
                '25-36':(range(25,37),3)
                }
def spin():
    return random.randint(1,36)

def determine_outside(number):
    results = []
    for group, numbers in outside_dict.items():
        if number in numbers[0]:
            results.append(group)
    return results

class Wager:

    def __init__(self, amount, space):
        self.amount = amount
        self.space = space

class RouletteGame():

    def __init__(self, bot, ctx):
        self.ctx = ctx
        self.bot = bot
        self.wager_dict = {}

    async def add_wagers(self, user_id, amount, spaces):
        for space in spaces:
            if user_id not in self.wager_dict:
                self.wager_dict[user_id] = [Wager(amount, space)]
            else:
                self.wager_dict[user_id].append(Wager(amount, space))

    async def resolve(self):
        winning_number = spin()
        results = determine_outside(winning_number)
        await self.ctx.send("Result is: {}{}".format(winning_number, ', '.join(results)))
        for user_id, wager_list in self.wager_dict.items():
            payout = 0
            for wager in wager_list:
                if str(wager.space) in results:
                    payout += outside_dict[str(wager.space)][1] * wager.amount
                elif wager.space == str(winning_number):
                    payout += 36 * wager.amount
            new_balance = db.modify_user_balance(user_id, payout)
            user = await self.bot.fetch_user(user_id)
            await self.ctx.send("{} won {:,}, new balance is {:,}".format(user.name, payout, new_balance))

class Roulette(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.game = None

    @commands.group(invoke_without_command=True)
    async def roulette(self, ctx, amount:int, *spaces):
        user_id = ctx.author.id
        balance = db.get_user_balance(user_id)

        #Validate user balance is sufficient and space is valid
        try:
            num_bets = len(spaces)
            total_amount = amount * num_bets
        except:
            total_amount = amount
            num_bets = 1
            spaces = [spaces]
        if total_amount > balance:
            await ctx.send("That would cost {} but you only have {} u broke ass bitch".format(total_amount, balance))
            return
        for space in spaces:
            if str(space) not in outside_dict:
                try:
                    if int(space) not in range(1,37):
                        await ctx.send("{} is not a valid number, please choose 1-36".format(space))
                        return
                except:
                    await ctx.send("{} is not a valid space u mook".format(space))
                    return

        #Initiate new game if no current game, add wager to current game otherwise.
        db.modify_user_balance(user_id, -1 * total_amount)
        if self.game is not None:
            await self.game.add_wagers(user_id, amount, spaces)
            output_brackets = ["{}"] * num_bets
            output_string = "{} bet {:,} on {}".format(ctx.author, amount, ', '.join(output_brackets))
            await ctx.send(output_string.format(*spaces))
        else:
            output_brackets = ["{}"] * num_bets
            output_string = "{} bet {:,} on {}".format(ctx.author, amount, ', '.join(output_brackets))
            await ctx.send(output_string.format(*spaces))
            self.game = RouletteGame(self.bot, ctx)
            await self.game.add_wagers(user_id, amount, spaces)
            await ctx.send("A new game of Not Rigged Roulette has started! User $roulette <amount> <space> to raise your bets!")
            await ctx.send("31s remaining!")
            async with ctx.typing():
                await asyncio.sleep(21)
                await ctx.send("10 seconds remaining, RAISE UR BETS!")
            async with ctx.typing():
                await asyncio.sleep(10)
                await self.game.resolve()
            self.game = None

def setup(bot):
    bot.add_cog(Roulette(bot))
