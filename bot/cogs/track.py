import discord
import asyncio
import logging
import functools
import requests

from discord.ext import commands
from cachetools import TTLCache
from datetime import datetime, timedelta

from bot.models.track import AsyncAudioSource, Track
from bot.models.voice_context import VoiceContext
from bot.services.track_service import TrackService
from bot.exceptions.exceptions import YTDLException
from bot.util.log import setup_logging_queue
from bot.util.color import ICE_BLUE

LOG = logging.getLogger('simple')

class Music(commands.Cog):

    def __init__(self, bot: commands.Bot, track_service: TrackService):
        self.bot = bot
        self.track_service = track_service
        self.voice_contexts = {}
        self.metadata_cache = TTLCache(100, timedelta(hours=12), timer=datetime.now)

    def get_voice_context(self, ctx: commands.Context):
        voice_context = self.voice_contexts.get(ctx.guild.id)
        if not voice_context:
            voice_context = VoiceContext(self.bot, ctx, self.track_service)
            self.voice_contexts[ctx.guild.id] = voice_context

        return voice_context

    def cog_unload(self):
        for state in self.voice_contexts.values():
            self.bot.loop.create_task(state.stop())

    def _is_queue_state_invalid(self, ctx: commands.Context):
        return (not ctx.voice_context or
                not ctx.voice_context.is_playing or
                len(ctx.voice_context.tracks) == 0)

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_context = self.get_voice_context(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(str(error))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        dest = ctx.author.voice.channel

        if ctx.voice_context.voice:
            await ctx.voice_context.voice.move_to(dest)
            return

        ctx.voice_context.voice = await dest.connect()

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, url: str):

        # This might happen if play is invoked from another coroutine
        if not hasattr(ctx, "voice_context"):
            ctx.voice_context = self.get_voice_context(ctx)

        if not ctx.voice_context.voice:
            await ctx.invoke(self._join)

        try:
            source = await AsyncAudioSource.create(ctx, url, self.metadata_cache)
        except YTDLException as e:
            await ctx.send(f"Nothing found for url {url}...")
        except Exception as e:
            LOG.error(f"Error creating audio source: {e}")
        else:
            track = Track(source)

            # If queue contains items, send queued msg
            if ctx.voice_context.is_playing or len(ctx.voice_context.tracks) > 0:
                await ctx.send(f"Queued up {track.source.title} !")

            await ctx.voice_context.tracks.put(track)

    @commands.command(name='leave')
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_context.voice:
            return await ctx.send("Not connected to any channel")

        await ctx.voice_context.stop()
        del self.voice_contexts[ctx.guild.id]

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_context.is_playing and ctx.voice_context.voice.is_playing():
            ctx.voice_context.voice.pause()
            return await ctx.send("Paused!")

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_context.is_playing and ctx.voice_context.voice.is_paused():
            ctx.voice_context.voice.resume()
            return await ctx.send("Resumed!!")

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):

        if not ctx.voice_context.is_playing:
            return await ctx.send("But there's no song playing!")

        ctx.voice_context.skip()

    @commands.command(name='stop', aliases=['clear', 'quit'])
    async def _stop(self, ctx: commands.Context):
        ctx.voice_context.tracks.clear()

        if ctx.voice_context.is_playing:
            ctx.voice_context.voice.stop()

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context):
        if not ctx.voice_context:
            return await ctx.send("I'm not currently active, why not change that with !play")
        tracks = ctx.voice_context.tracks
        return await ctx.send(f"{len(tracks)} tracks are queued")

    @commands.command(name='peek', aliases=['next'])
    async def _peek(self, ctx: commands.Context, num: int = None):

        if self._is_queue_state_invalid(ctx):
            return await ctx.send("No songs are queued!")

        if num is None:
            nxt = ctx.voice_context.tracks[0]
            return await ctx.send(embed=nxt.embed(title='Next up ~', color=ICE_BLUE))

        # Pull in the min(len(queue), num) and send each embed
        for idx in range(min(len(ctx.voice_context.tracks), num)):
            track = ctx.voice_context.tracks[idx]
            title = "Next up ~" if idx == 0 else f"Playing after {idx + 1} tracks"
            await ctx.send(embed=track.embed(
                                title=title,
                                color=ICE_BLUE))

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        if self._is_queue_state_invalid(ctx):
            return await ctx.send("No songs are queued to shuffle!")

        ctx.voice_context.tracks.shuffle()
        await ctx.send("Shuffled tracks in queue! Take a look with !peek {number}")

    @commands.command(name='top')
    async def _top(self, ctx:commands.Context, n: int = 1):
        top_tracks = await self.track_service.get_top_tracks(ctx.guild.id, n)
        await ctx.send(embed=Track.topTracksEmbed(top_tracks, ICE_BLUE))

    @commands.command(name='help')
    async def _help(self, ctx: commands.Context):
        embed = (discord.Embed(
            title='Command list',
            color=ICE_BLUE)
        .add_field(
            name='**!play {url}**',
            value='Queues up a track from YouTube. Must be in a voice channel to use',
            inline=False
        )
        .add_field(
            name='**!skip**',
            value='Skips the track currently playing',
            inline=False
        )
        .add_field(
            name='**!join**',
            value='Moves Elsa into the voice channel the user is currently in',
            inline=False
        )
        .add_field(
            name='**!leave**',
            value='Removes Elsa from the voice channel the user is currently in',
            inline=False
        )
        .add_field(
            name='**!pause**',
            value='Pauses the current track that is playing',
            inline=False
        )
        .add_field(
            name='**!resume**',
            value='Resumes a track that has been paused',
            inline=False
        )
        .add_field(
            name='**!stop**',
            value='Quits the current track, and clears the queue',
            inline=False
        )
        .add_field(
            name='**!queue**',
            value='Gives the number of tracks currently queued',
            inline=False
        )
        .add_field(
            name='**!peek {n}**',
            value='Shows the next n tracks that are in the queue',
            inline=False
        )
        .add_field(
            name='**!shuffle**',
            value='Shuffles tracks in the existing queue',
            inline=False
        )
        .add_field(
            name='**!top**',
            value='Displays a leaderboard of most freqently played tracks',
            inline=False
        ))
        await ctx.send(embed=embed)

    @_join.before_invoke
    @_play.before_invoke
    async def validate_voice_context(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You aren't connected to a voice channel")

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("I'm already in a voice channel")
