import discord
import re
from random import randint
import lotto_dao as db
import asyncio
from discord.ext import commands

class Ticket(object):

    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return "{}-{}-{}-M{}".format(*[n for n in self.numbers])

def quickpick(number_of_tickets=1):
    '''Returns a number of QP tickets'''
    qp_ticket_list = []
    for unused in range(number_of_tickets):
        numbers = []
        numlist=[1,2,3,4,5,6,7,8,9,10]
        for unused in range(3):
            numbers.append(numlist.pop(randint(0,len(numlist)-1)))
        megaball = randint(1,13)
        numbers.append(megaball)
    return Ticket(numbers)


def parse_ticket(winner, ticket):
    win_num = winner.numbers
    tick_num = ticket.numbers
    match = [x for x in tick_num[:3] if x in win_num[:3]]
    mega = True if win_num[3] == tick_num[3] else False
    return len(match), mega

def determine_payout(match, mega):
    if not mega:
        if match == 0:
            return 0
        if match == 1:
            return 2000
        if match == 2:
            return 6000
        if match == 3:
            return 120000
    if match == 0:
        return 13000
    if match == 1:
        return 24000
    if match == 2:
        return 74000
    if match == 3:
        return 'Jackpot'

class Lottory:

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        channel = message.channel
        if message.author.id == 292953664492929025:
            await channel.send("Shut up {}".format(message.author.nick))

    @commands.group(invoke_without_command=True)
    async def tickets(self, ctx):
        """
        Show all tickets for current lottory
        """
        lottory = db.get_current_lottory()
        ticket_list = db.get_user_tickets(ctx.author.id,lottory)
        await ctx.send('{} has {} tickets in the curret drawing. {}'.format(ctx.author, len(ticket_list),ticket_list))

    @tickets.command()
    async def again(self,ctx):
        await ctx.send('Oh, it didn\'t hurt that time!')

    @commands.group(invoke_without_command=True)
    async def lottory(self,ctx):
        if ctx.author.id != 154415714411741185:
            await ctx.send("You're not my real dad!")
            return
        db.add_lottory(0)
        lid = db.get_current_lottory()
        await ctx.send("Lottory {} has begun, purchase tickets now!".format(lid))

    @lottory.command()
    async def draw(self,ctx):
        if ctx.author.id != 154415714411741185:
            await ctx.send("You're not my real dad bitch!")
            return
        lid = db.get_current_lottory()
        await ctx.send("Drawing for lottory {} starting!".format(lid))
        winning = quickpick()
        balls = ['First', 'Second', 'Third', 'MEGA']
        for n in range(4):
            await asyncio.sleep(2)
            await ctx.send("{} ball is {}".format(balls[n], winning.numbers[n]))
        await ctx.send("Winning numbers are {}".format(winning))
        ticket_list = db.get_lottory_tickets(lid)
        print(ticket_list)
        for ticket_user in ticket_list:
            ticket = Ticket(eval(ticket_user[0]))
            user = await self.bot.get_user_info(ticket_user[1])
            match, mega = parse_ticket(winning, ticket)
            payout = determine_payout(match, mega)
            if payout != 0:
                await ctx.send("Congradulations {} won {} with ticket {}!".format(user.name ,payout,ticket))

    @commands.group(invoke_without_command=True, aliases=['buy_tickets', 'bt'])
    async def buy_ticket(self, ctx, ticket_value: int):
        """
        Purchase a lottory ticket
        """
        if ticket_value < 1:
            await ctx.send('I\'m afraid I can\'t let you do that {}'.format(ctx.author.nick))
            return
        db.add_ticket_to_user()
        s = '' if number_of_tickets == 1 else 's'
        await ctx.send('{} bought {} ticket{}!'.format(ctx.author.nick, number_of_tickets, s))

    @buy_ticket.command(aliases=['quickpick'])
    async def qp(self, ctx):
        """
        Qiuck pick ticket
        """
        ticket = quickpick()
        lottory_id = db.get_current_lottory()
        db.add_ticket_to_user(ticket.numbers, lottory_id, ctx.author.id)
        await ctx.send('Quickpick ticket {} purchased by {}, good luck!'.format(ticket, ctx.author.nick))


def setup(bot):
    bot.add_cog(Lottory(bot))
