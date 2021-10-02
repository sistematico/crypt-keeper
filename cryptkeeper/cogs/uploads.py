from discord.ext import commands

class Upload(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if len(message.attachments) > 0:
            filename = message.attachments[0].filename.replace('/(?:\.(?![^.]+$)|[^\w.])+/g', '-').lower()
            if filename.endswith('.mp3'):
                await message.attachments[0].save('uploads/audio/' + filename)
                await message.channel.send('Arquivo: `' + filename + '` enviado com sucesso.')
        return

        #await self.bot.process_commands(message)