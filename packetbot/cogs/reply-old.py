#from discord.ext import commands
import discord
#import random

discordClient = discord.Client

class Reply(discordClient):
    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello World!')
        await discordClient.process_commands(message)

    # @commands.command()
    # async def tip(self, ctx):
    #     """Get a random tip about using the bot."""
    #     index = random.randrange(len(self.tips))
    #     await ctx.send(f"**Dica #{index+1}:** {self.tips[index]}")
