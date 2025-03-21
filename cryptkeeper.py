import os
import asyncio
import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
from random import choice

TOKEN = os.environ.get('DISCORD_TOKEN')

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()

client = commands.Bot(command_prefix='!')

status = ['Counter-Strike: Source', 'Among Us', 'PlayerUnknown\'s Battlegrounds']
queue = []
loop = False

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='geral')
    await channel.send(f'Bem-vindo(a) {member.mention}! Quer ouvir uma música? Digite `!help` para maiores informações!')

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['***grumble*** Why did you wake me up?', 'Top of the morning to you lad!', 'Hello, how are you?', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name='die', help='This command returns a random last words')
async def die(ctx):
    responses = ['why have you brought my short life to an end', 'i could have done so much more', 'i have a family, kill them instead']
    await ctx.send(choice(responses))

@client.command(name='creditos', help='This command returns the credits')
async def credits(ctx):
    await ctx.send('Feito por `[PKL] Pé de Porco`')
    await ctx.send('Digite `?die` ou `?creditz`')

@client.command(name='creditz', help='This command returns the TRUE credits')
async def creditz(ctx):
    await ctx.send('**No one but me, lozer!**')

@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Você não está em um canal de voz.")
        return
    
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
    
@client.command(name='leave', help='This command stops the music and makes the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='loop', help='This command toggles loop mode')
async def loop_(ctx):
    global loop

    if loop:
        await ctx.send('Modo repetição está `DESATIVADO`!')
        loop = False
    
    else: 
        await ctx.send('Modo repetição está `ATIVADO`!')
        loop = True

@client.command(name='play', help='This command plays music')
async def play(ctx):
    global queue

    if not ctx.message.author.voice:
        await ctx.send("Você não está em um canal de voz.")
        return
    
    elif len(queue) == 0:
        await ctx.send('Nada na fila! Use `?fila` para adicionar uma música!')

    else:
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except: 
            pass

    server = ctx.message.guild
    voice_channel = server.voice_client
    while queue:
        try:
            while voice_channel.is_playing() or voice_channel.is_paused():
                await asyncio.sleep(2)
                pass

        except AttributeError:
            pass
        
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                
                if loop:
                    queue.append(queue[0])

                del(queue[0])
                
            await ctx.send('**Tocando agora:** {}'.format(player.title))

        except:
            break

@client.command(name='volume', help='This command changes the bots volume')
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")
    
    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Volume alterado para {volume}%")

@client.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

@client.command(name='resume', help='This command resumes the song!')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

@client.command(name='stop', help='This command stops the song!')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

@client.command(name='fila')
async def queue_(ctx, *, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` adicionada a fila!')

@client.command(name='remover')
async def remove(ctx, number):
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'Sua fila agora contem `{queue}!`')
    
    except:
        await ctx.send('Sua fila está **vazia** ou o índice está **fora de alcance**')

@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    await ctx.send(f'Sua fila `{queue}!`')

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run(TOKEN)