# import discord.py's command extension module
# see the documentation: https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#
from discord.ext import commands
import random

# with open('quotes.txt', encoding='utf8') as f:
#     for line in f:
#         print(line.strip())

# made Reply subclass commands.Cog
class Reply(commands.Cog):
    # Cogs must take the Bot and a config dict as arguments,
    # based on the way I have set things up in bot.py
    def __init__(self, bot, config):
        # keep a reference to the Bot object
        self.bot = bot
        # register the on_message function as a listener for the
        # `on_message` event.
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('!'):
            return

        if any(x in message.content.lower() for x in ['frase do dia', 'frases do dia']):
            await message.channel.send(random.choice(list(open('txt/confucio.txt','r'))))
            return

        if any(x in message.content.lower() for x in ['oie', 'olá','e aí']):
            await message.channel.send(random.choice([
                '{0.author} Olá!', 
                '{0.name} Oi, tudo bom?', 
                '{0.author} E aí! Blza?'
            ]).format(message))
            return

        # if 'olá' in message.content.lower():
        # if message.content.startswith('hello'):

        # use self.bot instead of self.client
        await self.bot.process_commands(message)