import discord
import lotto_dao as db
import asyncio
import re
from discord.ext import commands

def get_cock_power(cock_status):
    return (50 + cock_status) / 100

def build_embed(embed_input_dict):

    embed = discord.Embed(title=None,
                      description=None,
                      colour=embed_input_dict['colour'])

    embed.set_author(name=embed_input_dict['author_name'])

    for key, field in embed_input_dict['fields'].items():
        embed.add_field(name=field['name'], value=field['value'])
    return embed

class GeneralCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        '''Accepts deposits from Unbeleivaboat'''
        channel = message.channel
        if message.author.id == 292953664492929025: #Unbeleivaboat user.id
            try:
                sender_url = message.embeds[0].author.icon_url
                description = message.embeds[0].description
                receiver_id = int(re.findall(r'<@!(\d+)>', description)[0])
                amount = int(re.findall(r'your .(\d{1,3}(,\d{3})*(\.\d+)?)', description)[0][0].replace(',', ''))
                sender_id = int(re.findall(r'tars/(\d+)/', sender_url)[0])
            except:
                return
            if receiver_id == 456460945074421781: #Lotto-bot user.id
                new_balance = db.modify_user_balance(sender_id, amount)
                sender = await self.bot.fetch_user(sender_id)
                await channel.send("{:,} received from {}. Your balance is now {:,}".format(amount, sender.name, new_balance))

    @commands.group(invoke_without_command=True, aliases=["lb"])
    async def leaderboard(self,ctx):
        '''Displays user balance, cock status and number of tickets in current drawing'''

        user_list = db.get_user()
        balances = []

        for user_id in user_list:
            user = await self.bot.fetch_user(user_id[0])

            if not user.bot:
                balance = db.get_user_balance(user.id)
                cock_status = db.get_cock_status(user.id)
                balances.append((user.name, cock_status, balance))

        sorted_balances = sorted(balances, key=lambda balances: balances[2], reverse=True)
        rank = 1
        output = []

        for user_name, cock_status, user_balance in sorted_balances:
            cock_power = "{:.1f}% <:peen:456499857759404035>".format((get_cock_power(cock_status) * 100)) if cock_status is not -1 else "<:sad:455866480454533120>"
            output.append("{}: **{}** - {:,} - {}".format(rank, user_name, round(user_balance), cock_power))
            rank += 1

        embed_dict = {'colour':discord.Colour(0x034cc1), 'author_name':"Lotto-Bot",
                    'fields': {1:{'name': "Leaderboard", 'value': "\n".join(output)}}}

        await ctx.send(embed = build_embed(embed_dict))

    @commands.group(invoke_without_command=True, hidden=True)
    async def money_please(self, ctx, amount: int):
        '''Adds amount to all non bot users balances'''

        if ctx.author.id != 154415714411741185: #My user.id
            await ctx.send("You're not my real dad bitch!")
            return

        user_id_list = db.get_user() #Returns a list of all users

        for user_id in user_id_list:
            user = await self.bot.fetch_user(user_id[0])
            if not user.bot:
                new_balance = db.modify_user_balance(user_id[0], amount)
                await ctx.send('Added {} to {}\'s balance. New balance is {}'.format(amount, user.name, new_balance))

    @commands.group(invoke_without_command=True, aliases=["bal","cash","money"])
    async def balance(self,ctx):
        '''Shows your balance and number of tickets in current drawing'''

        balance = db.get_user_balance(ctx.author.id)
        lottory_id = db.get_current_lottory()
        ticket_list = db.get_user_tickets(ctx.author.id,lottory_id)
        await ctx.send("{} balance is {:,}. You have {} tickets in the next drawing".format(ctx.author.name, round(balance,2), len(ticket_list)))

def setup(bot):
    bot.add_cog(GeneralCommands(bot))
