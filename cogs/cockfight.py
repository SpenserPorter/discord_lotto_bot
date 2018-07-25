import discord
import random
import lotto_dao as db
import asyncio
from discord.ext import commands

def get_cock_power(cock_status):
    return round((50 + cock_status) / 100.00,2)

def build_embed(input_dict):

    embed = discord.Embed(title=None,
                      description=None,
                      colour=input_dict['colour'])

    embed.set_author(name=input_dict['author_name'])

    for key, field in input_dict['fields'].items():
        embed.add_field(name=field['name'], value=field['value'])

    return embed

class CockFight:

    def __init__(self, bot):
        self.bot = bot
        self.cock_price = 100

    @commands.group(invoke_without_command=True, aliases=["cf", "cock", "dongfight", "df"])
    async def cockfight(self, ctx, amount:int):
        user_id = ctx.author.id
        balance = db.get_user_balance(user_id)
        cock_status = db.get_cock_status(user_id)

        if cock_status == -1:
            await ctx.send("Your cock is not ready for battle, prepare your lil cock with $prepare_cock first.")
            return
            
        if amount > balance:
            await ctx.send("That would cost {}, you only have {} you chode".format(amount, balance))
            return

        else:
            new_balance = db.modify_user_balance(user_id, -1 * amount)
            result = random.random()
            cock_power = get_cock_power(cock_status)

            if result < cock_power:
                amount_won = amount * 2
                new_cock_status = cock_status + 1
                new_balance = db.modify_user_balance(user_id, amount_won)
                db.set_cock_status(user_id, new_cock_status)
                result_msg = "Your lil cock made you {:,} richer".format(amount_won)
                hardness_msg= "Now at {}% hardness <:peen:456499857759404035>".format(get_cock_power(new_cock_status) * 100)
                embed_dict = {'colour':discord.Colour(0x00e553), 'author_name':ctx.author.name,
                            'fields': {1:{'name': result_msg, 'value': hardness_msg}}}

                await ctx.send(embed=build_embed(embed_dict))
            else:
                db.set_cock_status(user_id, -1)
                result_msg = "Your cock snapped in half <:sad:455866480454533120>"
                embed_dict = {'colour':discord.Colour(0xe10531), 'author_name':ctx.author.name,
                            'fields': {1:{'name': 'Ouch', 'value': result_msg}}}

                await ctx.send(embed=build_embed(embed_dict))


    @commands.group(invoke_without_command=True, aliases=["pc","gethard","buy"])
    async def prepare_cock(self, ctx):
        user_id = ctx.author.id
        balance = db.get_user_balance(user_id)
        cock_status = db.get_cock_status(user_id)
        cock_power = get_cock_power(cock_status)
        if cock_status != -1:
            await ctx.send("Your cock is already prepared for battle, currently at {}% hardness".format(cock_power * 100))
            return
        if balance < self.cock_price:
            await ctx.send("Your cock is too mangled and bruised to battle, please wait until you can afford 100 for a cock doctor before battling again.")
            return
        else:
            db.modify_user_balance(user_id, -1 * self.cock_price)
            db.set_cock_status(user_id, 0)
            await ctx.send("Your cock is ready for battle, you tip your fluffer {} for their service".format(self.cock_price))

def setup(bot):
    bot.add_cog(CockFight(bot))
