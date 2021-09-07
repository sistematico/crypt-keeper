import discord
import logging
import sys
from discord.ext import commands
from .cogs import music, error, meta, tips, autoreply
from . import config

cfg = config.load_config()
bot = commands.Bot(command_prefix=cfg["prefix"])

@bot.event
async def on_ready():
    logging.info(f"Bot logado como {bot.user.name}")

COGS = [music.Music, error.CommandErrorHandler, meta.Meta, tips.Tips, autoreply.AutoReply]

def add_cogs(bot):
    for cog in COGS:
        bot.add_cog(cog(bot, cfg))

def run():
    add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError("Nenhum token fornecido. Por favor verifique se o arquivo config.toml contem o token do bot.")
        sys.exit(1)
    bot.run(cfg["token"])
