import discord
from random import randint
from secrets import randbelow
import lotto_dao as db
import asyncio
from discord.ext import commands


payout_table = {True:{0:8500, 1:3500, 2:14000, 3:262000},
                False:{0:0, 1:0, 2:0, 3:40500}}

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
            length = len(numlist)
            numbers.append(numlist.pop(randbelow(length)))
        megaball = randbelow(13) + 1
        numbers.append(megaball)
        qp_ticket_list.append(Ticket(numbers))
    return qp_ticket_list


def parse_ticket(winner, ticket):
    win_num = winner.numbers
    tick_num = ticket.numbers
    match = [x for x in tick_num[:3] if x in win_num[:3]]
    mega = win_num[3] == tick_num[3]
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


    @tickets.command()
    async def again(self,ctx):
        await ctx.send('Oh, it didn\'t hurt that time!')

    @commands.group(invoke_without_command=True,aliases=['lottery'])
    async def lottory(self,ctx):
        if ctx.author.id != 154415714411741185:
            await ctx.send("You're not my real dad!")
            return
        db.add_lottory(0)
        lid = db.get_current_lottory()
        await ctx.send("Lottory {} has begun, purchase tickets now!".format(lid))

    @lottory.command()
    async def status(self,ctx):
        lid = db.get_current_lottory()
        tickets = db.get_lottory_tickets(lid)
        num_tickets = len(tickets)
        progressive = db.get_lottory_jackpot_prog(lid)
        jackpot = payout_table[True][3] + progressive
        await ctx.send("Lottory {} is in progress, currently {:,} tickets sold, current jackpot is {:,}".format(lid,num_tickets,jackpot ))

    @lottory.command()
    async def draw(self,ctx):
        #if ctx.author.id != 154415714411741185:
        #    await ctx.send("You're not my real dad bitch!")
        #    return

        lid = db.get_current_lottory()
        progressive = db.get_lottory_jackpot_prog(lid)
        total_jackpot = progressive + payout_table[True][3]
        db.add_lottory() #increment lottory to next when drawing starts

        await ctx.send("Drawing for lottory {} starting! Jackpot is currently {:,}".format(lid,total_jackpot))

        winning_numbers = quickpick()[0] #Choose winning number_of_tickets

        balls = ['First', 'Second', 'Third', 'MEGA']
        async with ctx.typing():
            for n in range(4):
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

                    #if ticket_payout == payout_table[True][3]:
                        #jackpot_split.append([user_id, ticket_value])
                    #else:

                    balance_modifier += ticket_payout

                new_user_balance = db.modify_user_balance(user_id, balance_modifier)
                results.append([user_id, balance_modifier, new_user_balance, list_of_winning_tickets])
                total_payout += balance_modifier

            jackpot_results = []
            if len(jackpot_split) > 0:
                jackpot_payout = total_jackpot / len(jackpot_split)
                total_payout += total_jackpot

                for ticket_tuple in jackpot_split:

                    user_id = ticket_tuple[0]
                    ticket_value = ticket_tuple[1]
                    new_user_balance = db.modify_user_balance(user_id, jackpot_payout)
                    jackpot_results.append([user_id, jackpot_payout, new_user_balance, ticket_value])

                split_won = 'won' if len(jackpot_results) == 1 else 'split'
                await ctx.send("------------JACKPOT WINNAR!!!!!!-------------")
                for result in jackpot_results:
                    user_id = result[0]
                    jackpot_payout = result[1]
                    new_user_balance = result[2]
                    ticket_value = result[3]
                    user = await self.bot.get_user_info(user_id)
                    await ctx.send('{} {} the Jackpot of {:,} with ticket {}!!!!!!!'.format(user.name, split_won, round(jackpot_payout, 2), ticket_value))
                    await user.send('You {} the Jackpot for lottory {} with ticket {}! {:,} has been deposited into your account. Your new balance is {}.'.format(split_won, lid, ticket_value, round(jackpot_payout, 2), new_user_balance))

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
            progressive_add = len(ticket_list) * 443
            new_progressive = progressive + progressive_add
            lid = db.get_current_lottory()
            db.modify_lottory_jackpot_prog(lid, new_progressive)
            await ctx.send("No jackpot winner! Adding {:,} to next lottory! New jackpot is {:,}!".format(progressive_add, payout_table[True][3] + new_progressive))
        else:
            await ctx.send("Jackpot has been reseeded to {:,}".format(payout_table[True][3]))

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
            await ctx.send("Lottory {} stats: Total income: {} Total payout: {} Payout Ratio: {}%".format(lid_total, total_income, total_outflow, round(payout_ratio,2)))
        else:
            await ctx.send("There are not stats yet!")


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
    async def qp(self, ctx, number_of_tickets=1):
        """
        Quick pick ticket
        """
        ticket_list = quickpick(number_of_tickets)
        lottory_id = db.get_current_lottory()
        user_balance = db.get_user_balance(ctx.author.id)
        total_cost = 1000 * number_of_tickets
        if user_balance < total_cost:
            await ctx.send("That would cost {:,}, your balance is {:,}. Broke ass bitch".format(total_cost, user_balance))
            return
        else:
            new_balance = db.modify_user_balance(ctx.author.id, -1 * total_cost)
            for ticket in ticket_list:
                db.add_ticket_to_user(ticket.numbers, lottory_id, ctx.author.id)
                if len(ticket_list) <= 5:
                    await ctx.send('Quickpick ticket {} purchased by {}, good luck!'.format(ticket, ctx.author.nick))
            if number_of_tickets > 500:
                await ctx.author.send("You bought {} tickets. I'm not going to send you all of them.".format(number_of_tickets))
            else:
                for n in range(0, len(ticket_list), 100):
                    await ctx.author.send("Lottory {} Quickpick tickets {}".format(lottory_id, ticket_list[n:n+100]))
            await ctx.send("{} spent {:,} on {:,} tickets, new balance is {:,}. Use !tickets to see your ticket numbers!".format(ctx.author.name, total_cost, number_of_tickets, new_balance))

def setup(bot):
    bot.add_cog(Lottory(bot))
