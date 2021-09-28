from discord.ext import commands


class Upload(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.bot.add_listener(self.on_message, "on_message")

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if len(message.attachments) > 0:
            #filename = ''.join(e for e in ctx.message.attachments[0].filename if e.isalnum())
            filename = message.attachments[0].filename.replace('/(?:\.(?![^.]+$)|[^\w.])+/g', '-').lower()

            if filename.endswith('.jpg'): # Checks if it is a .csv file
                await message.attachments[0].save('uploads/' + filename)
                await message.channel.send(filename)
            else:
                await message.channel.send('Formato inválido.')

            #await message.channel.send(filename)
            # await clear_soundboard()
        return

        await self.bot.process_commands(message)