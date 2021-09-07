from discord.ext import commands
import discord

class AutoReply(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot:
            return

        if message.content.startswith('oi'):
            await message.channel.send('Aloha!')
        #await self.bot.process_commands(message)