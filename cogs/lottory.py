import discord
import random
import numpy as np
import lotto_dao as db
import asyncio
from multiprocessing import Pool
from itertools import combinations
from discord.ext import commands

ticket_cost = 10000

payout_table = {True:{0:0*ticket_cost, 1:4*ticket_cost, 2:15*ticket_cost, 3:200*ticket_cost, 4:15000*ticket_cost},
                False:{0:0*ticket_cost, 1:0*ticket_cost, 2:0*ticket_cost, 3:20*ticket_cost, 4:1500*ticket_cost}}


numbers = [x for x in range(1,24)]
all_the_combs = list(combinations(numbers, 4))

class Ticket(object):

    __slots__ = ('numbers')
    def __init__(self, numbers):
        self.numbers = numbers

    def __repr__(self):
        return "{}-{}-{}-{}-M{}".format(*[n for n in self.numbers])

def ticket_generator(number_of_tickets=1):
    '''Returns a number of QP tickets'''
    ticket_list = []
    numlist = [x for x in range(1,24)]
    for unused in range(number_of_tickets):
        np.random.shuffle(numlist)
        numbers = numlist[:4]
        megaball = np.random.randint(1,12)
        numbers.append(megaball)
        ticket_list.append(numbers)
    return ticket_list

def quickpick(number_of_tickets=1):
    results = []
    for result in mp_handler(number_of_tickets):
        results.extend(result)
    return results

def mp_handler(number_of_tickets):
    max_batch_size = 50000
    number_of_processes = 10 if number_of_tickets >= 100000 else 1
    pool = Pool(number_of_processes)
    batch_size = min(max_batch_size, int(number_of_tickets / number_of_processes))
    inputs = [batch_size for x in range(batch_size-1, number_of_tickets, batch_size)] + [number_of_tickets % batch_size]
    for result in pool.imap_unordered(ticket_generator, inputs):
        yield result
    pool.close()
    pool.join()


def quickpickmap(number_of_tickets=1):
    return list(map(lambda x: list(all_the_combs[x]).append(random.randint(1,12)), [random.randint(0,len(all_the_combs)-1) for i in range(number_of_tickets)]))


def parse_ticket(winner, ticket):
    match = [x for x in ticket[:4] if x in winner[:4]]
    mega = winner[4] == ticket[4]
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
        await ctx.send("4 White Balls 1-23, 1 MEGABALL 1-11 - Ticket cost {:,} \n Match 4+1 win {:,} + progressive jackpot \n Match 4    win {:,} \n Match 3+1 win {:,} \n Match 3    win {:,} \n Match 2+1 win {:,}\n Match 1+1 win {:,}".format(ticket_cost, payout_table[True][4], payout_table[False][4], payout_table[True][3], payout_table[False][3], payout_table[True][2], payout_table[True][1]))


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

    @commands.group(invoke_without_command=True)
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
                await asyncio.sleep(1)
                await ctx.send("{} ball is {}".format(balls[n], winning_numbers[n]))
            await ctx.send("Winning numbers are {}".format(Ticket(winning_numbers)))

        ticket_list = db.get_lottory_tickets(lid) #List of tuples (user_id, ticket_value)
        num_tickets = len(ticket_list)
        jackpot_split = []
        winner_dict = {}
        total_payout = 0

        async with ctx.typing():
            for ticket_tuple in ticket_list:
                ticket_value = eval(ticket_tuple[0])
                user_id = ticket_tuple[1]
                match, mega = parse_ticket(winning_numbers, ticket_value)
                ticket_payout = determine_payout(mega, match)

                if ticket_payout != 0:
                    winner_dict = add_ticket_to_winner_dict(winner_dict, user_id, ticket_value, ticket_payout)

        results = {}
        async with ctx.typing():

            for user_id, list_of_winning_tickets in winner_dict.items():
                balance_modifier = 0

                for ticket_tuple in list_of_winning_tickets:
                    ticket_value = Ticket(ticket_tuple[0])
                    ticket_payout = ticket_tuple[1]

                    if ticket_payout == payout_table[True][4]:
                        jackpot_split.append([user_id, ticket_value])
                    else:
                        balance_modifier += ticket_payout

                new_user_balance = db.modify_user_balance(user_id, balance_modifier)
                results[user_id] = [balance_modifier, new_user_balance, list_of_winning_tickets]
                total_payout += balance_modifier

            jackpot_results = {}
            if len(jackpot_split) > 0:
                jackpot_progressive_share = round(progressive / len(jackpot_split), 2)
                jackpot_payout = round(payout_table[True][4] + jackpot_progressive_share, 2)
                for ticket_tuple in jackpot_split:
                    user_id = ticket_tuple[0]
                    ticket_value = ticket_tuple[1]
                    total_payout += jackpot_payout
                    new_user_balance = db.modify_user_balance(user_id, jackpot_payout)
                    if user_id not in jackpot_results:
                        jackpot_results[user_id] = [jackpot_payout, new_user_balance, [ticket_value], jackpot_progressive_share]
                    else:
                        jackpot_results[user_id][0] += jackpot_payout
                        jackpot_results[user_id][1] = new_user_balance
                        jackpot_results[user_id][2].append(ticket_value)
                        jackpot_results[user_id][3] += jackpot_progressive_share

                split_won = 'won' if len(jackpot_results) == 1 else 'split'
                await ctx.send("------------JACKPOT WINNAR!!!!!!-------------")
                for user_id, result in jackpot_results.items():
                    jackpot_payout = result[0]
                    new_user_balance = result[1]
                    ticket_values = result[2] if len(result[2]) <= 10 else len(result[2])
                    progressive_split = result[3]
                    user = await self.bot.get_user_info(user_id)
                    await ctx.send('{} {} the Jackpot! Payout {:,}, your share of the progressive is {:,}! with {} tickets!!'.format(user.name, split_won, round(jackpot_payout,2), round(progressive_split,2), ticket_values))
                    await user.send('You {} the Jackpot for lottory {} with ticket {}! {:,} has been deposited into your account. Your new balance is {}.'.format(split_won, lid, ticket_value, round(jackpot_payout,2), new_user_balance))

            for user_id, result in results.items():
                jackpot_balance_modifier = jackpot_results[user_id][0] if user_id in jackpot_results else 0
                balance_modifier= result[0] + jackpot_balance_modifier
                new_user_balance=result[1]
                winning_tickets=result[2]
                user = await self.bot.get_user_info(user_id)
                await ctx.send("{} won a total of {:,} on {:,} winning tickers!".format(user.name, balance_modifier, len(winning_tickets)))
                await user.send("Lottory {} Results: You won {:,}. Your new balance is {:,}.".format(lid, balance_modifier, new_user_balance))
                if len(winning_tickets) < 100:
                    for n in range(0, len(winning_tickets), 50):
                        await user.send("Your winnings tickets for Lottory {}: Winning Numbers:{} Your winners: {}".format(lid, winning_numbers, winning_tickets[n:n+50]))

        income = ticket_cost * num_tickets
        payout_ratio = 100 * (total_payout - income) / income
        db.update_lottory_stats(lid, income, total_payout)
        await ctx.send("Lottory {} ended! {:,} tickets were sold for {:,}, {:,} was paid out for a payout ratio of {}%".format(lid, num_tickets, income, round(total_payout,2), round(payout_ratio, 2)))
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
    async def buy_ticket(self, ctx, *ticket_value):
        """
        Purchase a lottory ticket
        """


    @buy_ticket.command(aliases=['quickpick'])
    async def qp(self, ctx, number_of_tickets=1):
        """
        Quick pick ticket
        """
        lottory_id = db.get_current_lottory()
        user_balance = db.get_user_balance(ctx.author.id)
        total_cost = ticket_cost * number_of_tickets
        if user_balance < total_cost:
            await ctx.send("That would cost {:,}, your balance is {:,}. Broke ass bitch".format(total_cost, user_balance))
            return
        else:
            async with ctx.typing():
                progressive = db.get_lottory_jackpot_prog(lottory_id)
                ticket_list = quickpick(number_of_tickets)
                progressive_add = number_of_tickets * ticket_cost * .1
                new_progressive = progressive + progressive_add
                db.add_ticket_to_user(ticket_list, lottory_id, ctx.author.id)
                new_balance = db.modify_user_balance(ctx.author.id, -1 * total_cost)
                db.modify_lottory_jackpot_prog(lottory_id, progressive_add)
                if len(ticket_list) <= 5:
                    for ticket in ticket_list:
                        await ctx.send('Quickpick ticket {} purchased by {}, good luck!'.format(Ticket(ticket), ctx.author.name))
                if number_of_tickets > 500:
                    await ctx.author.send("You bought {} tickets. I'm not going to send you all of them.".format(number_of_tickets))
                else:
                    for n in range(0, len(ticket_list), 50):
                        await ctx.author.send("Lottory {} Quickpick tickets {}".format(lottory_id, ticket_list[n:n+50]))
                await ctx.send("{} spent {:,} on {:,} tickets, new balance is {:,}. The jackpot is now {:,}".format(ctx.author.name, total_cost, number_of_tickets, round(new_balance,2), payout_table[True][4]+new_progressive))

def setup(bot):
    bot.add_cog(Lottory(bot))
