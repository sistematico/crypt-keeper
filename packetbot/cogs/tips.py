from discord.ext import commands
import discord
import random


class Tips(commands.Cog):
    """Commands for providing tips about using the bot."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[-1]]
        self.tips = [
            "Somente admins podem pular as músicas imediatamente. Todos os outros precisam votar!",
            f"Você pode achar meu código fonte em: {self.config['github_url']}"
        ]

    @commands.command()
    async def tip(self, ctx):
        """Get a random tip about using the bot."""
        index = random.randrange(len(self.tips))
        await ctx.send(f"**Dica #{index+1}:** {self.tips[index]}")
