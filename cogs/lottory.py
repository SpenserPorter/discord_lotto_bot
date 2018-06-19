import discord
import random
import numpy as np
import lotto_dao as db
import asyncio
import multiprocessing
import itertools
from discord.ext import commands


payout_table = {True:{0:0, 1:2000, 2:12000, 3:250000, 4:50000000},
                False:{0:0, 1:0, 2:0, 3:25000, 4:2000000}}

class Ticket(object):

    __slots__ = ('numbers')
    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return "{}-{}-{}-{}-M{}".format(*[n for n in self.numbers])

def quickpick(number_of_tickets=1):
    '''Returns a number of QP tickets'''
    qp_ticket_list = []
    numlist = [x for x in range(1,24)]
    for unused in range(number_of_tickets):
        np.random.shuffle(numlist)
        numbers = numlist[:4]
        megaball = np.random.randint(1,12)
        numbers.append(megaball)
        qp_ticket_list.append(Ticket(numbers))
    return qp_ticket_list

def quickpick2(number_of_tickets=1):
    '''Returns a number of QP tickets'''
    qp_ticket_list = []
    for unused in range(number_of_tickets):
        numbers = []
        numlist=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        for unused in range(4):
            length = len(numlist)
            numbers.append(numlist.pop(np.random.randint(0,length)))
        megaball = np.random.randint(1,12)
        numbers.append(megaball)
        qp_ticket_list.append(numbers)
    return qp_ticket_list

def quickpick3(number_of_tickets=1):
    numbers = range(1,24)
    return [random.sample(numbers, 4) for i in range(number_of_tickets)]


def quickpick_multi(number_of_tickets):
    return mp_handler(number_of_tickets)

numbers = [x for x in range(1,24)]
all_the_combs = list(itertools.combinations(numbers, 4))

def mp_handler(number_of_tickets):
    number_of_processes = 10
    avg_per = int(number_of_tickets / number_of_processes)
    remainder = number_of_tickets % number_of_processes
    inputs = [avg_per] * number_of_processes
    inputs[0] += remainder

    pool = multiprocessing.Pool(number_of_processes)
    pool.map(quickpickmap, inputs)

def quickpickmap(number_of_tickets=1):
    return list(map(lambda x: list(all_the_combs[x]).append(random.randint(1,12)), [random.randint(0,len(all_the_combs)-1) for i in range(number_of_tickets)]))


def parse_ticket(winner, ticket):
    win_num = winner.numbers
    tick_num = ticket.numbers
    match = [x for x in tick_num[:4] if x in win_num[:4]]
    mega = win_num[4] == tick_num[4]
    return len(match), mega

def add_ticket_to_winner_dict(winner_dict, user_id, ticket_value, payout):
    if user_id not in winner_dict:
        winner_dict[user_id] = [[ticket_value, payout]]
    else:
        winner_dict[user_id].append([ticket_value, payout])
    return winner_dict

def determine_payout(mega, match):
    return payout_table[mega][match]

class Lottory:

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        channel = message.channel
        if message.author.id == 292953664492929025:
            await channel.send("Shut up {}".format(message.author.nick))

    @commands.group(invoke_without_command=True)
    async def money_please(self, ctx, amount: int):
        '''adds amount to all users balance'''
        if ctx.author.id != 154415714411741185:
            await ctx.send("You're not my real dad bitch!")
            return
        user_id_list = db.get_user()
        for user_id in user_id_list:
            user = await self.bot.get_user_info(user_id[0])
            if not user.bot:
                new_balance = db.modify_user_balance(user_id[0], amount)
                await ctx.send('Added {} to {}\'s balance. New balance is {}'.format(amount, user.name, new_balance))

    @commands.group(invoke_without_command=True)
    async def tickets(self, ctx):
        """
        Show all tickets for current lottory
        """
        lottory = db.get_current_lottory()
        ticket_list = db.get_user_tickets(ctx.author.id,lottory)
        await ctx.send('{} has {} tickets in the curret drawing.'.format(ctx.author, len(ticket_list)))
        for n in range(0, len(ticket_list), 100):
            await ctx.author.send('{}'.format(ticket_list[n:n+100]))

    @commands.group(invoke_without_command=True,aliases=['lottery'])
    async def lottory(self,ctx):
        if ctx.author.id != 154415714411741185:
            await ctx.send("You're not my real dad!")
            return
        db.add_lottory(0)
        lid = db.get_current_lottory()
        await ctx.send("Lottory {} has begun, purchase tickets now!".format(lid))

    @commands.group(invoke_without_command=True, aliases=['what'])
    async def info(self, ctx):
        await ctx.send("4 White Balls 1-23, 1 MEGABALL 1-11 - Ticket cost 1000 \n Match 4+1 win {:,} + progressive jackpot \n Match 4    win {:,} \n Match 3+1 win {:,} \n Match 3    win {:,} \n Match 2+1 win {:,}\n Match 1+1 win {:,}".format(payout_table[True][4], payout_table[False][4], payout_table[True][3], payout_table[False][3], payout_table[True][2], payout_table[True][1]))


    @lottory.command()
    async def status(self,ctx):
        lid = db.get_current_lottory()
        tickets = db.get_lottory_tickets(lid)
        num_tickets = len(tickets)
        progressive = db.get_lottory_jackpot_prog(lid)
        jackpot = payout_table[True][4] + progressive
        await ctx.send("Lottory {} is in progress, currently {:,} tickets sold, current jackpot is {:,}".format(lid,num_tickets,jackpot))

    @commands.group(invoke_without_command=True)
    async def balance(self,ctx):
        balance = db.get_user_balance(ctx.author.id)
        lid = db.get_current_lottory()
        ticket_list = db.get_user_tickets(ctx.author.id,lid)
        await ctx.send("{} balance is {:,}. You have {} tickets in the next drawing".format(ctx.author.name, round(balance,2), len(ticket_list)))

    @lottory.command()
    async def draw(self,ctx):
        #if ctx.author.id != 154415714411741185:
        #    await ctx.send("You're not my real dad bitch!")
        #    return

        lid = db.get_current_lottory()
        progressive = db.get_lottory_jackpot_prog(lid)
        total_jackpot = progressive + payout_table[True][4]
        db.add_lottory() #increment lottory to next when drawing starts

        await ctx.send("Drawing for lottory {} starting! Jackpot is currently {:,}".format(lid,total_jackpot))

        winning_numbers = quickpick()[0] #Choose winning number_of_tickets

        balls = ['First', 'Second', 'Third', 'Fourth', 'MEGA']
        async with ctx.typing():
            for n in range(5):
                await asyncio.sleep(2)
                await ctx.send("{} ball is {}".format(balls[n], winning_numbers.numbers[n]))
            await ctx.send("Winning numbers are {}".format(winning_numbers))

        ticket_list = db.get_lottory_tickets(lid) #List of tuples (user_id, ticket_value)
        num_tickets = len(ticket_list)
        jackpot_split = []
        winner_dict = {}
        total_payout = 0

        async with ctx.typing():
            for ticket_tuple in ticket_list:
                ticket_value = Ticket(eval(ticket_tuple[0]))
                user_id = ticket_tuple[1]
                match, mega = parse_ticket(winning_numbers, ticket_value)
                ticket_payout = determine_payout(mega, match)

                if ticket_payout != 0:
                    winner_dict = add_ticket_to_winner_dict(winner_dict, user_id, ticket_value, ticket_payout)

        results = []
        async with ctx.typing():

            for user_id, list_of_winning_tickets in winner_dict.items():
                balance_modifier = 0

                for ticket_tuple in list_of_winning_tickets:
                    ticket_value = ticket_tuple[0]
                    ticket_payout = ticket_tuple[1]

                    if ticket_payout == payout_table[True][4]:
                        jackpot_split.append([user_id, ticket_value])
                    else:
                        balance_modifier += ticket_payout

                new_user_balance = db.modify_user_balance(user_id, balance_modifier)
                results.append([user_id, balance_modifier, new_user_balance, list_of_winning_tickets])
                total_payout += balance_modifier

            jackpot_results = []
            if len(jackpot_split) > 0:
                jackpot_progressive_share = round(progressive / len(jackpot_split), 2)
                jackpot_payout = round(payout_table[True][4] + jackpot_progressive_share, 2)
                total_payout += progressive + payout_table[True][4]

                for ticket_tuple in jackpot_split:
                    user_id = ticket_tuple[0]
                    ticket_value = ticket_tuple[1]
                    new_user_balance = db.modify_user_balance(user_id, jackpot_payout)
                    jackpot_results.append([user_id, jackpot_payout, new_user_balance, ticket_value, jackpot_progressive_share])

                split_won = 'won' if len(jackpot_results) == 1 else 'split'
                await ctx.send("------------JACKPOT WINNAR!!!!!!-------------")
                for result in jackpot_results:
                    user_id = result[0]
                    jackpot_payout = result[1]
                    new_user_balance = result[2]
                    ticket_value = result[3]
                    progressive_split = result[4]
                    user = await self.bot.get_user_info(user_id)
                    await ctx.send('{} {} the Jackpot! Payout {:,}, your share of the progressive is {:,}! with ticket {}!!!!!!!'.format(user.name, split_won, jackpot_payout, progressive_split, ticket_value))
                    await user.send('You {} the Jackpot for lottory {} with ticket {}! {:,} has been deposited into your account. Your new balance is {}.'.format(split_won, lid, ticket_value, round(jackpot_payout,2), new_user_balance))

            for result in results:
                user_id = result[0]
                balance_modifier=result[1]
                new_user_balance=result[2]
                winning_tickets=result[3]
                user = await self.bot.get_user_info(user_id)
                await ctx.send("{} won a total of {:,} on {:,} winning tickers!".format(user.name, balance_modifier, len(winning_tickets)))
                await user.send("Lottory {} Results: You won {:,}. Your new balance is {:,}.".format(lid, balance_modifier, new_user_balance))
                if len(winning_tickets) < 100:
                    for n in range(0, len(winning_tickets), 50):
                        await user.send("Your winnings tickets for Lottory {}: Winning Numbers:{} Your winners: {}".format(lid, winning_numbers, winning_tickets[n:n+50]))

        income = 1000 * num_tickets
        payout_ratio = 100 * (total_payout - income) / income
        db.update_lottory_stats(lid, income, total_payout)
        await ctx.send("Lottory {} ended! {:,} tickets were sold for {:,}, {:,} was paid out for a payout ratio of {}%".format(lid, num_tickets, num_tickets * 1000, total_payout, round(payout_ratio, 2)))
        if len(jackpot_split) == 0:
            await ctx.send("No jackpot winner!")
            lid = db.get_current_lottory()
            db.modify_lottory_jackpot_prog(lid, progressive)
        else:
            await ctx.send("Jackpot has been reseeded to {:,}".format(payout_table[True][4]))

    @lottory.command(invoke_without_command=True)
    async def stats(self, ctx, lid=None):
        '''Returns lifetime lottory statistics, or stats of specific lottory_id if given'''
        stats_list = db.get_lottory_stats(lid)
        total_income = 0
        total_outflow = 0
        lid_total = '{}'.format(lid) if lid is not None else 'lifetime'
        for stats_tuple in stats_list:
            income = stats_tuple[0]
            outflow = stats_tuple[1]
            total_income += income
            total_outflow += outflow
        if total_income > 0:
            payout_ratio = 100 * (total_outflow - total_income) / total_income
            await ctx.send("Lottory {} stats: Total income: {:,} Total payout: {:,} Payout Ratio: {}%".format(lid_total, total_income, total_outflow, round(payout_ratio,2)))
        else:
            await ctx.send("There are not stats yet!")


    @commands.group(invoke_without_command=True, aliases=['buy_tickets', 'bt'])
    async def buy_ticket(self, ctx, ticket_value,):
        """
        Purchase a lottory ticket
        """

    @buy_ticket.command(aliases=['quickpick'])
    async def qp(self, ctx, number_of_tickets=1):
        """
        Quick pick ticket
        """
        ticket_list = quickpick(number_of_tickets)
        lottory_id = db.get_current_lottory()
        user_balance = db.get_user_balance(ctx.author.id)
        progressive = db.get_lottory_jackpot_prog(lottory_id)
        total_cost = 1000 * number_of_tickets
        if user_balance < total_cost:
            await ctx.send("That would cost {:,}, your balance is {:,}. Broke ass bitch".format(total_cost, user_balance))
            return
        else:
            progressive_add = number_of_tickets * 100
            new_progressive = progressive + progressive_add
            new_balance = db.modify_user_balance(ctx.author.id, -1 * total_cost)
            db.add_ticket_to_user(ticket_list, lottory_id, ctx.author.id)
            db.modify_lottory_jackpot_prog(lottory_id, progressive_add)
            if len(ticket_list) <= 5:
                for ticket in ticket_list:
                    await ctx.send('Quickpick ticket {} purchased by {}, good luck!'.format(ticket, ctx.author.name))
        if number_of_tickets > 500:
            await ctx.author.send("You bought {} tickets. I'm not going to send you all of them.".format(number_of_tickets))
        else:
            for n in range(0, len(ticket_list), 100):
                await ctx.author.send("Lottory {} Quickpick tickets {}".format(lottory_id, ticket_list[n:n+100]))
        await ctx.send("{} spent {:,} on {:,} tickets, new balance is {:,}. The jackpot is now {:,}".format(ctx.author.name, total_cost, number_of_tickets, new_balance, payout_table[True][4]+new_progressive))

def setup(bot):
    bot.add_cog(Lottory(bot))
