# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
import datetime

################################  ALKUPASKA  ################################

with open('token.txt') as f:
    TOKEN = f.readline().strip()


bot = commands.Bot(command_prefix = "!", description="FULL BLAST!", case_insensitive = True)

status = ["Putin simulator 7000", "Åtter simulatår", "Paska peli", "My Summer Blyat",
          "Rocket League", "Minesweeper", "Perkele simulator", "Battle Royale Suomi",
          "GGA", "Mitä vittua oliivi", "Mitä vittua, olvi"]

class playerData():
    Channel = ""
    Playlist = []
    State = "404"
    CurrentSong = "404"
    Volume = "404"
    LastStatusUpdate = None

playerdata = playerData

async def printPlayerInfo(ctx):
    global playerdata
    playlistStr = ""
    for index, data in enumerate(playerdata.Playlist):
        if index != 0:
            playlistStr += str("{}. {}\n".format(index, data))
    if playerdata.LastStatusUpdate != None:
        try:
            await playerdata.LastStatusUpdate.delete()
        except:
            pass
    playerdata.LastStatusUpdate = await ctx.send("\n__**BlasterMaster's JukedBox**__\n**State:** {}\n**Volume:** {}%\n**Current song:** {}\n**Current playlist:**\n{}".format(playerdata.State, playerdata.Volume, playerdata.CurrentSong, playlistStr))

## Status
async def change_status():
    await bot.wait_until_ready()
    msgs = itertools.cycle(status)

    while not bot.is_closed():
        current_status = next(msgs)
        await bot.change_presence(activity=discord.Game(name=current_status))
        await asyncio.sleep(60*10)      ## Wait 10 mins

## Update TJ on Sotamonni-rank
async def update_tj():
    await bot.wait_until_ready()

    while not bot.is_closed():
        ## Get "sotamonni" -role by id
        role = discord.utils.get(bot.get_guild(175614327867310080).roles, id=731993022786437232)

        ## TJ
        today = datetime.date.today()
        kotiintumispaeva = datetime.date(2021, 6, 17)
        TJ = (kotiintumispaeva - today).days

        ## Edit role name
        if(role.name.endswith("TJ{}".format(TJ)) == False):
            ## Get ranks name without TJ
            names_name = role.name.split("-")[0]

            await role.edit(name="{}- TJ{}".format(names_name, TJ))

        ## Wait until tomorrow, 10 seconds past midnight
        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + datetime.timedelta(days=1)
        wait_time = (tomorrow - now + datetime.timedelta(seconds=10))
        #print(wait_time)
        #print(wait_time.total_seconds())
        await asyncio.sleep(wait_time.total_seconds())


@bot.event
async def on_ready():
    print("Logged in as {} at {}".format(bot.user, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


################################  FFMPEG + YTDL SETTINGS  ################################

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        ## Add name to player data -class
        playerdata.Playlist.append(data['title'])
        await printPlayerInfo(ctx)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        ## Used for preparing a stream, instead of downloading.
        ## Since Youtube Streaming links expire
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)

################################  BASIC COMMANDIT  ################################

class Basics(commands.Cog, name = "Basic shit"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "cyka")
    async def cyka_(self, ctx):
        await ctx.send("Blyat!")

    @commands.command(name = "nollaplusnolla", aliases = ["0+0"])
    async def nollaplusnolla_(self, ctx):
        await ctx.message.delete()
        await ctx.send("Nolla, plus nolla, on nolla! :anchor: :anchor:")

    @commands.command(name = "oltsu86", aliases = ["oltsu"])
    async def oltsu86_(self, ctx):
        await ctx.message.delete()
        await ctx.send("oltsu86 is a heavy anchor :anchor:")

    @commands.command(name = "kaljaa")
    async def kaljaa(self, ctx):
        await ctx.message.delete()
        await ctx.send(":regional_indicator_o::regional_indicator_i::regional_indicator_s::regional_indicator_p::regional_indicator_a:            :regional_indicator_k::regional_indicator_a::regional_indicator_l::regional_indicator_j::regional_indicator_a::regional_indicator_a:        :beer::beer: ")

    @commands.command(name = "moti")
    async def moti_(self, ctx):
        await ctx.send("```Error 404. 'Moti' not found```")

    @commands.command(name = "sotamonninaamut", aliases = ["tj"])
    async def sotamonninaamut(self, ctx):

        today = datetime.date.today()
        kotiintumispaeva = datetime.date(2021, 6, 17)
        TJ = (kotiintumispaeva - today)
        await ctx.send("Sotamonnilla on jäljellä {} aamua! (Aikamoinen kasa)".format(TJ.days))


        ## Get "sotamonni" -role by id
        #role = discord.utils.get(ctx.guild.roles, id=731993022786437232)
        #print(role)

        #await role.edit(name="Sotamonni #TJ")

    # @commands.command(name = "test", hidden=True)
    # async def test(self, ctx):
    #     print(ctx.message.guild.id)
    #
    #     print(Bot.get_guild(175614327867310080))
    #
    #     print(discord.utils.get(discord.Client.gui))
    #
    #     role = discord.utils.get(discord.Client().get_guild(175614327867310080).roles, id=731993022786437232)
    #     print(role)




################################  ADVANCED COMMANDIT  ################################

## SAY
@bot.command(hidden=True)
async def say(ctx, *args):
    await ctx.message.delete()
    output = ""
    for word in args:
        output = output + word
        output = output + " "
    await ctx.send(output)

## CLEAR
@bot.command(hidden=True)
async def clear(ctx, amount: int = 0):
    if amount <= 0:
        await ctx.send("Please specify amount of messages to be cleared.", delete_after=5)
    else:
        await ctx.channel.purge(limit = amount)

## TAG
@bot.command(hidden=True)
async def tag(ctx, name_):
    await ctx.message.delete()
    try:
        member = discord.utils.get(ctx.message.guild.members, name=name_)
        await ctx.send(member.mention)
    except:
        await ctx.send("Member '{}' not found".format(name_))

@bot.command(name = "kyskys", aliases = ["kys^2"], hidden=True)
async def kyskys(ctx):
    if playerdata.LastStatusUpdate != None:
        await playerdata.LastStatusUpdate.delete()
    await ctx.message.delete()
    await ctx.send("Lähden Kuopioon...")
    sys.exit(0)

################### VOICE MÄÄRITTELYT, NOT BY HENZZZZI  ########################

class MusicPlayer:

    __slots__ = ("bot", "_guild", "_channel", "_cog", "queue", "next", "current", "np", "volume")

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop(ctx))

        playerData.Volume = "50"

    async def player_loop(self, ctx):
        ## Player loop
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.next.clear()
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)
            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send("There was an error processing your song.\n")
                    continue
            source.volume = self.volume
            playerdata.Volume = self.volume * 100
            playerdata.CurrentSong = source.title
            playerdata.State = "Playing"
            await printPlayerInfo(ctx)

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.next.wait()
            del playerdata.Playlist[0]
            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            #self.current = None
            playerdata.CurrentSong = ""
            playerdata.State = "Not Playing"
            await printPlayerInfo(ctx)

    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))

class Music(commands.Cog, name = "Music/Voice"):

    __slots__ = ("bot", "players")

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        ## A local check which applies to all commands in this cog
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        ## A local error handler for all errors arising from commands in this cog
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send("This command can not be used in Private Messages.")
            except discord.HTTPException:
                pass

        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        ## Get guilds audioplayer, if none, create one
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    ################################  VOICE COMMANDS  ################################

    @commands.command(name="join", help="Join to a voice channel")
    async def join_(self, ctx, *, channel: discord.VoiceChannel=None):
        try:
            await ctx.message.delete()
        except:
            pass
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("You are not connected to a voice channel.", delete_after=5)
        vc = ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.send("Blyaat", delete_after=5)
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                await ctx.send("Blyaat", delete_after=5)
        playerData.Channel = channel

    @commands.command(name = "joinname", aliases = ["jn"], help="Join to a voice channel.")
    async def joinname_(self, ctx, name_: str):
        await ctx.message.delete()
        try:
            ## Try searching a user with given name
            name_ = discord.utils.get(ctx.message.guild.members, name=name_)

            ## If user has connectec to a voice channel
            if name_.voice.channel != None:
                await name_.voice.channel.connect()
            else:
                await ctx.send("User '{}' is not connected to a voice channel.".format(name_), delete_after=5)

        ## If there's no user with given name
        except:
            await ctx.send("Invalid name.", delete_after=5)

    @commands.command(name="play", help="Plays/adds to queue song from provided url")
    async def play_(self, ctx, *, search: str):
        await ctx.trigger_typing()
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.join_)
        player = self.get_player(ctx)
        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=True)
        await player.queue.put(source)

    @commands.command(name="pause", help="Pauses music")
    async def pause_(self, ctx):
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send("I am not currently playing anything Blyat", delete_after=5)
        elif vc.is_paused():
            return await ctx.send("Player is already paused", delete_after=5)
        vc.pause()
        playerdata.State = "Paused"
        await printPlayerInfo(ctx)
        ##await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command(name="resume", aliases = ["r"])
    async def resume_(self, ctx):
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything Blyat", delete_after=5)
        elif not vc.is_paused():
            return
        vc.resume()
        playerdata.State = "Playing"
        await printPlayerInfo(ctx)

    @commands.command(name="skip", aliases = ["s"], help="Skips current song")
    async def skip_(self, ctx):
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything Blyat", delete_after=5)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        vc.stop()

    @commands.command(name="volume", aliases=["vol"], help="Sets volume (0-100%)")
    async def change_volume(self, ctx, *, vol: int = 0):
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently connected to voice!", delete_after=5)
        if not 0 < vol < 101:
            return await ctx.send("Error: Enter a value between 1 and 100", delete_after=5)
        player = self.get_player(ctx)
        if vc.source:
            vc.source.volume = vol / 100
        player.volume = vol / 100
        playerdata.Volume = vol
        await printPlayerInfo(ctx)

    @commands.command(name="kys", help="Leaves voice channel")
    async def stop_(self, ctx):
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently connected Blyat", delete_after=5)
        await self.cleanup(ctx.guild)

    @commands.command(name="tiikeri", aliases=["muna"], help="Näytä muna :D")
    async def tiikeri_(self, ctx):
        await ctx.trigger_typing()
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.join_)
        player = self.get_player(ctx)
        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        url = "https://www.youtube.com/watch?v=DJHwZpkLhL8"
        source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop, download=True)
        await player.queue.put(source)

    @commands.command(name="masterblaster", aliases=["mb", "fullblast"], help="Kuinka vanha olet")
    async def masterblaster_(self, ctx):
        await ctx.trigger_typing()
        await ctx.message.delete()
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.join_)
        player = self.get_player(ctx)
        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        url = "https://www.youtube.com/watch?v=kwU1_plW3L0"
        source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop, download=True)
        await player.queue.put(source)


################################  KEK  ################################

bot.add_cog(Basics(bot))
bot.add_cog(Music(bot))

bot.loop.create_task(change_status())
bot.loop.create_task(update_tj())
bot.run(TOKEN, bot=True, reconnect=True)
