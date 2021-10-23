import os
from discord.ext import commands
import discord
import asyncio
import youtube_dl
import logging
import math
from urllib import request
from ..video import Video

# TODO: abstract FFMPEG options into their own file?
FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
"""
Command line options to pass to `ffmpeg` before the `-i`.

See https://stackoverflow.com/questions/43218292/youtubedl-read-error-with-discord-py/44490434#44490434 for more information.
Also, https://ffmpeg.org/ffmpeg-protocols.html for command line option reference.
"""

async def not_playing(ctx):
    """Checks that audio is not currently playing before continuing."""
    client = ctx.guild.voice_client
    if not client:
        return True
    else:
        raise commands.CommandError("O bot está tocando uma música.")

async def audio_playing(ctx):
    """Checks that audio is currently playing before continuing."""
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise commands.CommandError("O bot não está tocando nenhum audio.")


async def in_voice_channel(ctx):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise commands.CommandError("Você precisa estar em um canal de voz para isso.")


async def is_audio_requester(ctx):
    """Checks that the command sender is the song requester."""
    music = ctx.bot.get_cog("Music")
    state = music.get_state(ctx.guild)
    permissions = ctx.channel.permissions_for(ctx.author)
    if permissions.administrator or state.is_requester(ctx.author):
        return True
    else:
        raise commands.CommandError("Você precisa ser a pessoa que pediu a música para fazer isto.")


class Music(commands.Cog):
    """Bot commands to help play music."""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config[__name__.split(".")[
            -1]]  # retrieve module name, find config entry
        self.states = {}
        self.bot.add_listener(self.on_reaction_add, "on_reaction_add")

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(aliases=["stop"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        """Leaves the voice channel, if currently in one."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            state.playlist = []
            state.now_playing = None
        else:
            raise commands.CommandError("Não está em um canal de voz.")

    @commands.command(aliases=["resume"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        client = ctx.guild.voice_client
        self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @commands.command(aliases=["vol", "v"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def volume(self, ctx, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        state = self.get_state(ctx.guild)

        # make sure volume is nonnegative
        if volume < 0:
            volume = 0

        max_vol = self.config["max_volume"]
        if max_vol > -1:  # check if max volume is set
            # clamp volume to [0, max_vol]
            if volume > max_vol:
                volume = max_vol

        client = ctx.guild.voice_client

        state.volume = float(volume) / 100.0
        client.source.volume = state.volume  # update the AudioSource's volume to match

    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        if ctx.channel.permissions_for(
                ctx.author).administrator or state.is_requester(ctx.author):
            # immediately skip if requester or admin
            client.stop()
        elif self.config["vote_skip"]:
            # vote to skip song
            channel = client.channel
            self._vote_skip(channel, ctx.author)
            # announce vote
            users_in_channel = len([
                member for member in channel.members if not member.bot
            ])  # don't count bots
            required_votes = math.ceil(
                self.config["vote_skip_ratio"] * users_in_channel)
            await ctx.send(
                f"{ctx.author.mention} votaram para pular a música com ({len(state.skip_votes)}/{required_votes} votos)"
            )
        else:
            raise commands.CommandError("Desculpe, a opção de pular a música está desabilitada.")

    def _vote_skip(self, channel, member):
        """Register a vote for `member` to skip the song playing."""
        logging.info(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([
            member for member in channel.members if not member.bot
        ])  # don't count bots
        if (float(len(state.skip_votes)) /
                users_in_channel) >= self.config["vote_skip_ratio"]:
            # enough members have voted to skip, so skip the song
            logging.info(f"Votos suficientes, pulando...")
            channel.guild.voice_client.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        state = self.get_state(ctx.guild)
        message = await ctx.send("", embed=state.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @commands.command(aliases=["q", "playlist"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, ctx):
        """Display the current play queue."""
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        """Returns a block of text describing a given song queue."""
        if len(queue) > 0:
            message = [f"{len(queue)} músicas na fila:"]
            message += [
                f"  {index+1}. **{song.title}** (Música pedida por **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "A fila está vazia."

    @commands.command(aliases=["cq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.has_permissions(administrator=True)
    async def clearqueue(self, ctx):
        """Clears the play queue without leaving the channel."""
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.command(aliases=["jq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.has_permissions(administrator=True)
    async def jumpqueue(self, ctx, song: int, new_index: int):
        """Moves song at an index to `new_index` in queue."""
        state = self.get_state(ctx.guild)  # get state for this guild
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song - 1)  # take song at index...
            state.playlist.insert(new_index - 1, song)  # and insert it.

            await ctx.send(self._queue_text(state.playlist))
        else:
            raise commands.CommandError("You must use a valid index.")

    @commands.command(brief="Plays audio from <url>.", aliases=["yt", "youtube", "tocar", "toca"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""

        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)  # get the guild's state

        if client and client.channel:
            try:
                video = Video(url, ctx.author)
            except youtube_dl.DownloadError as e:
                logging.warn(f"Erro ao baixar o vídeo: {e}")
                await ctx.send("Houve um erro ao baixar seu vídeo, desculpe.")
                return
            state.playlist.append(video)
            message = await ctx.send("Adicionada a fila.", embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except youtube_dl.DownloadError as e:
                    await ctx.send("Houve um erro ao baixar seu vídeo, desculpe.")
                    return
                client = await channel.connect()
                self._play_song(client, state, video)
                message = await ctx.send("", embed=video.get_embed())
                await self._add_reaction_controls(message)
                logging.info(f"Tocando agora '{video.title}'")
            else:
                raise commands.CommandError("Você precisa estar em um canal de voz para isso.")

    async def on_reaction_add(self, reaction, user):
        """Respods to reactions added to the bot's messages, allowing reactions to control playback."""
        message = reaction.message
        if user != self.bot.user and message.author == self.bot.user:
            await message.remove_reaction(reaction, user)
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                permissions = message.channel.permissions_for(user)
                guild = message.guild
                state = self.get_state(guild)
                if permissions.administrator or (
                        user_in_channel and state.is_requester(user)):
                    client = message.guild.voice_client
                    if reaction.emoji == "⏯":
                        # pause audio
                        self._pause_audio(client)
                    elif reaction.emoji == "⏭":
                        # skip audio
                        client.stop()
                    elif reaction.emoji == "⏮":
                        state.playlist.insert(
                            0, state.now_playing
                        )  # insert current song at beginning of playlist
                        client.stop()  # skip ahead
                elif reaction.emoji == "⏭" and self.config["vote_skip"] and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                    # ensure that skip was pressed, that vote skipping is
                    # enabled, the user is in the channel, and that the bot is
                    # in a voice channel
                    voice_channel = message.guild.voice_client.channel
                    self._vote_skip(voice_channel, user)
                    # announce vote
                    channel = message.channel
                    users_in_channel = len([
                        member for member in voice_channel.members
                        if not member.bot
                    ])  # don't count bots
                    required_votes = math.ceil(
                        self.config["vote_skip_ratio"] * users_in_channel)
                    await channel.send(
                        f"{user.mention} votaram para pular a música com ({len(state.skip_votes)}/{required_votes} votos)"
                    )

    async def _add_reaction_controls(self, message):
        """Adds a 'control-panel' of reactions to a message that can be used to control the bot."""
        CONTROLS = ["⏮", "⏯", "⏭"]
        for control in CONTROLS:
            await message.add_reaction(control)

    @commands.command(aliases=["p"])
    @commands.check(not_playing)
    async def local_play(self, client, *, song):

        def after_playing(err):
            client.disconnect()

        if client.author.voice is not None and client.author.voice.channel is not None:
            channel = client.author.voice.channel
            client = await channel.connect()

        try:
            source = discord.FFmpegPCMAudio('uploads/audio/' + str(song) + '.mp3')
            #source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('uploads/audio/' + str(song) + '.mp3', before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)
            client.play(source, after=after_playing)
            # client.play(source)
            while client.is_playing():
                sleep(.1)
        except IOError:
            await client.send(str(client.author.name) + f" o arquivo {song} é inválido.")
        finally:
            await client.message.delete()
            logging.info(f"Tocando agora '{video.title}'")


    # async def local_play(self, ctx, *, arquivo):
        # Gets voice channel of message author
        # voice_channel = ctx.author.channel
        # channel = None
        # if voice_channel != None:
        #     channel = voice_channel.name
        #     vc = await voice_channel.connect()
        #     vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="C:<path_to_file>"))
        #     # Sleep while audio is playing.
        #     while vc.is_playing():
        #         sleep(.1)
        #     await vc.disconnect()
        # else:
        #     await ctx.send(str(ctx.author.name) + "is not in a channel.")
        # # Delete command after the audio is done playing.
        # await ctx.message.delete()



        # def _play_song(self, client, state, song):
        # state.now_playing = song
        # state.skip_votes = set()  # clear skip votes
        # source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)
        
        # source = discord.FFmpegPCMAudio(('uploads/audio/' + str(song) + '.mp3', before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)
        # source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('uploads/audio/' + str(song) + '.mp3', before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)
        # client.play(source, after=after_playing)











        # client = ctx.guild.voice_client
        # state = self.get_state(ctx.guild)  # get the guild's state

        # if ctx.author.voice is not None and ctx.author.voice.channel is not None:
        #     channel = ctx.author.voice.channel
        #     client = await channel.connect()

        #     try:
        #         source = discord.FFmpegPCMAudio('uploads/audio/' + str(arquivo) + '.mp3')
        #         client.play(source)
        #         while client.is_playing():
        #             sleep(.1)
        #         await client.disconnect()
        #     except IOError:
        #         await ctx.send(str(ctx.author.name) + f" o arquivo {arquivo} é inválido.")
        #     finally:
        #         await ctx.message.delete()
        #     # logging.info(f"Tocando agora '{video.title}'")
        # else:
        #     raise commands.CommandError("Você precisa estar em um canal de voz para isso.")

    @commands.command(aliases=["la", "ls", "lista", "listar", "listagem"])
    async def list(self, ctx):
        await ctx.message.delete()

        try:
            #files_no_ext = [".".join(f.split(".")[:-1]) for f in os.listdir('uploads/audio/') if os.path.isfile(f)]
            files = [os.path.splitext(filename)[0] for filename in os.listdir('uploads/audio/') if os.path.isfile(filename) and filename != '.gitignore']
            #s = ""
            #for f in files:
            #    s = s + f"- {f}\n"


            print(files)
            arquivos = '\n'.join(files)

            print(arquivos)
            #print(s)
            #print (files)
            await ctx.send(str(ctx.author.name) + f": Listagem de arquivos:\n```\n{arquivos}\n```")
        except:
            await ctx.send(str(ctx.author.name) + f" Houve um erro ao exibir a listagem de arquivos.")
        #finally:
        #    await ctx.message.delete()

class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user
