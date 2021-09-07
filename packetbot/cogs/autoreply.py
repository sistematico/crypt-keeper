from discord.ext import commands
import discord

class AutoReply(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[-1]]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')
        await bot.process_commands(message)