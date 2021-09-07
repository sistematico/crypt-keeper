import discord

class Reply:
    def __init__(self, discordClient):
        self.discordClient = discordClient

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')
        await discordClient.process_commands(message)