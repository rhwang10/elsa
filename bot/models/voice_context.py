import asyncio
import logging
import requests
import os
import json
import functools
from datetime import datetime
import discord

from async_timeout import timeout
from discord.ext import commands
from bot.models.queue import TrackQueue
from bot.util.color import ICE_BLUE
from bot.models.track import AsyncAudioSource
# from bot.services.track_service import TrackService

LOG = logging.getLogger('simple')
TRACK_EVENTS_ENDPOINT = os.environ.get("TRACK_EVENTS_ENDPOINT")

class VoiceContext:

    def __init__(self,
                 bot: commands.Bot,
                 ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx
        # self.track_service = track_service

        self.tracks = TrackQueue()
        self.next_track = asyncio.Event()
        self.current_track = None

        self._volume = 0.5
        self.voice = None

        self.player = bot.loop.create_task(self.play_audio())

    def __del__(self):
        self.player.cancel()

    @property
    def is_playing(self):
        return self.voice and self.current_track

    async def play_audio(self):
        LOG.info("Initializing audio loop")
        while True:
            self.next_track.clear()

            try:
                async with timeout(900): # If nothing new in 15 minutes, quit
                    self.current_track = await self.tracks.get()
            except asyncio.TimeoutError:
                LOG.info("Loop timed out, exiting")
                self.bot.loop.create_task(self.stop())
                return

            LOG.info(f"Pulled in new track! {self.current_track.source.title}")
            try:
                self.current_track.source.volume = self._volume
                # this is for local, assuming you installed ffmpeg and opus via brew
                if not discord.opus.is_loaded() and os.environ.get("ENV") != "prod":
                    LOG.info('loading opus')
                    discord.opus.load_opus('libopus.dylib')
                self.voice.play(self.current_track.source, after=self.play_next)
            except discord.ClientException as e:
                LOG.error("Discord Client exception")
                await self._ctx.send("Something went wrong, please try a different track!")
                self.play_next()
            except TypeError as e:
                LOG.error("Type Error")
                LOG.error(e)
                await self._ctx.send("Something went wrong, please try a different track!")
                self.play_next()
            except discord.opus.OpusNotLoaded as e:
                LOG.error("Opus not loaded")
                await self._ctx.send("Something went wrong, please try a different track!")
                self.play_next()
            except Exception as e:
                LOG.error('Unknown exception')
                await self._ctx.send("Something went wrong, please try a different track!")
                self.play_next()



            # play_event = self._construct_play_event(self.current_track.source)
            # await self.track_service.post_track_event(play_event)

            await self.current_track.source.channel.send(
                embed=self.current_track.embed(
                    title='Now Playing!',
                    color=ICE_BLUE
                )
            )

            await self.next_track.wait()

    def play_next(self, error=None):
        if error:
            LOG.error(f"Something went wrong in play next: {str(error)}")
            raise
        self.next_track.set()

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    def _construct_play_event(self, source: AsyncAudioSource):
        return {
            'id': source.id,
            'requested_by': source.requested_by.name + "#" + source.requested_by.discriminator,
            'event_type': 'PLAY',
            'title': source.title,
            'description': source.description,
            'webpage_url': source.webpage_url,
            'duration': source.duration,
            'timestamp': datetime.now().isoformat(),
            'guild_id': self._ctx.guild.id
        }

    async def stop(self):
        self.tracks.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
