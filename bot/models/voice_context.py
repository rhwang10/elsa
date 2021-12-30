import asyncio

from async_timeout import timeout

from discord.ext import commands

from bot.models.queue import TrackQueue

class VoiceContext:

    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

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
        while True:
            self.next_track.clear()

            try:
                async with timeout(900): # If nothing new in 15 minutes, quit
                    self.current_track = await self.tracks.get()
            except asyncio.TimeoutError:
                self.bot.loop.create_task(self.stop())
                return

            self.current_track.source.volume = self._volume
            self.voice.play(self.current_track.source, after=self.play_next)
            await self.next_track.wait()

    def play_next(self, error=None):
        if error:
            print("Something went wrong in play next")
            raise Exception(str(error))
        self.next_track.set()

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.tracks.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
