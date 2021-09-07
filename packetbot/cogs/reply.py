from discord.ext import commands
import discord
import random

cli = discord.Client()

class Reply():
    def __init__(self, bot, config, cli):
        self.cli = cli
        self.bot = bot
        self.config = config[__name__.split(".")[-1]]
        self.saudacoes = ["Olá", "Oi"]

    @cli.event
    async def on_message(message):
        if message.author == cli.user:
            return
        
        if message.content == 'oi':
            await message.send("Oiii")
            #await message.channel.send(' aaaaa ')
        await cli.process_commands(message)

    @commands.command()
    async def tip(self, ctx):
        """Get a random tip about using the bot."""
        index = random.randrange(len(self.tips))
        await ctx.send(f"**Dica #{index+1}:** {self.tips[index]}")
