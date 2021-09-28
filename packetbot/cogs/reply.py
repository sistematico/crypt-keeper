from discord.ext import commands
import random

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
        if len(message.attachments) > 0 or message.content.startswith('!') or message.content.startswith('@') or message.author == self.bot.user:
            return

        if any(x in message.content.lower() for x in ['frase do dia']) or message.content.startswith('@frase'):
            frase = random.choice(list(open('txt/frases.txt','r')))
            #await message.channel.send(message.author.id)
            #await message.channel.send(message.author.name)
            await message.channel.send("<@" + message.author.id + "> " + frase)
            return

        if any(x in message.content.lower() for x in ['oie', 'olá','e aí']):
            saudacao = random.choice(['Olá!', 'Oi, tudo bom?', 'E aí! Blza?'])
            await message.channel.send(saudacao)
            return

        # use self.bot instead of self.client
        await self.bot.process_commands(message)