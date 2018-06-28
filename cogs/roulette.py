import discord
import random
import numpy as np
import lotto_dao as db
import asyncio
import re
from discord.ext import commands

def spin():
    return random.randint(1,37)

outside_dict = {'red':([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],2),
                'black':([2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35],2),
                '1-18':([range(1,19)],2),
                '19-36':([range(19,37)],2),
                'Even':([range(2,37,2)],2),
                'Odd':([range(1,36,2)],2),
                '1st':([1,4,7,10,13,16,19,22,25,28,31,34],3),
                '2nd':([2,5,8,11,14,17,20,23,26,29,32,35],3),
                '3rd':([3,6,9,12,15,18,21,24,27,30,33,36],3),
                '1-12':([range(1,13)],3),
                '13-24':([range(13,25)],3),
                '25-36':([range(25,37)],3)
                }

def determine_outside(number):
    results = []
    for group, numbers in outside_dict.items():
        if number in numbers[0]:
            results.append(group)
    return results

class RouletteGame:

    def __init__(self, user_id, bet, amount):
        self.bets = {user_id:[bet, amount]}


class Roulette:

    def __init__(self, bot):
        self.bot = bot
        self.game = None

    @commands.group(invoke_without_command=True, hidden=True)
    async def roulette(self, ctx, bet, amount: int):
        user_id = db.get_user(ctx.author.id)
        balance = db.get_user_balance(user_id)
        if bet > balance:
            await ctx.send("You only have {} u bitch".format(balance))
            return
        if str(bet) not in outside_dict or bet not in range(1,37):
            await ctx.send("{} is not a valid bet".format(bet))
        winning_number = spin()
        results = determine_outside(winning_number)
        await ctx.send("Result is:{} {}".format(winning_number, results))
        if str(bet) in results:
            payout = outside_dict[str(bet)][2] * amount
        if bet == winning_number:
            payout = 36 * amount
        new_balance = db.modify_user_balance(payout)
        await ctx.send("{} won {}, new balance is {}".format(ctx.author.name, payout, new_balance))

def setup(bot):
    bot.add_cog(Roulette(bot))
