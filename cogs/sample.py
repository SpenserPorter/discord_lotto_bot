import discord
from discord.ext import commands



class Lottory(object):

    def __init__(self, size):
        self.balance = size
        self.entries = 0
        self.entrants = {}




class Sample:

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        channel = message.channel
        if message.author.id == 292953664492929025:
            await channel.send("Shut up {}".format(message.author.nick))

    @commands.group(invoke_without_command=True)
    async def testicles(self, ctx):
        """
        A test command.
        """
        await ctx.send('Ouch my testicles!')

    @testicles.command()
    async def again(self,ctx):
        await ctx.send('Oh, it didn\'t hurt that time!')

    @commands.group(invoke_without_command=True, aliases=['buy_tickets'])
    async def buy_ticket(self, ctx, number_of_tickets: int):
        """
        Purchase a lottory ticket
        """
        if number_of_tickets < 1:
            await ctx.send('I\'m afraid I can\'t let you do that {}'.format(ctx.author.nick))
            return
        if number_of_tickets == 1:
            s = ''
        else:
            s = 's'

        await ctx.send('{} bought {} ticket{}!'.format(ctx.author.nick, number_of_tickets, s))

    @buy_ticket.command(aliases=['bonus'])
    async def mega(self, ctx, number_of_tickets: int):
        """
        Add mega bonus multiplier
        """
        if number_of_tickets == 1:
            s = ''
        else:
            s = 's'
        await ctx.send('{} bought {} MEGA BONUS ticket{}!'.format(ctx.author.nick, number_of_tickets, s))


def setup(bot):
    bot.add_cog(Sample(bot))
