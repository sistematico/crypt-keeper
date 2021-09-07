import discord
import sys
import traceback
import logging
from discord.ext import commands

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.bot.add_listener(self.on_command_error, "on_command_error")

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return  # Don't interfere with custom error handlers

        error = getattr(error, "original", error)  # get original error

        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(f"Este comando não existe. Por favor use `{self.bot.command_prefix}help` para uma lista de comandos.")

        if isinstance(error, commands.CommandError):
            return await ctx.send(f"Erro ao executar o comando `{ctx.command.name}`: {str(error)}")

        await ctx.send("Um erro inesperado aconteceu ao tentar executar este comando.")
        logging.warn("Ignorando a excessão no comando {}:".format(ctx.command))
        logging.warn("\n" + "".join(
            traceback.format_exception(
                type(error), error, error.__traceback__)))
