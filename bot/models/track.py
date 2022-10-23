import discord
import functools
import youtube_dl
import asyncio
import concurrent.futures
import logging

from cachetools import TTLCache
from discord.ext import commands
from datetime import datetime

from bot.util.log import setup_logging_queue

from bot.exceptions.exceptions import YTDLException

LOG = logging.getLogger('simple')

class AsyncAudioSource(discord.PCMVolumeTransformer):

    # Workaround for age-restricted videos
    # https://stackoverflow.com/questions/69901098/discord-py-ytdl-doesnt-play-age-restricted-videos
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'listformats': True,
        'cachedir': False,
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    yt = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)
    cache_l = asyncio.Lock()

    def __init__(self,
                 ctx : commands.Context,
                 source: discord.FFmpegPCMAudio,
                 data: dict,
                 cached: bool,
                 volume: float = 0.5):
        super().__init__(source, volume)
        self.channel = ctx.channel
        self.requested_by = ctx.author

        self.data = data
        self.cached = cached
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.webpage_url = data['webpage_url']
        self.duration = data['duration']
        self.thumbnail = data['thumbnails'][-1]['url']
        self.is_downloaded = True

    @classmethod
    async def create(cls, ctx: commands.Context, url: str, cache: TTLCache):
        async with cls.cache_l:
            try:
                metadata = cache[url]
                cached = True
            except KeyError as e:
                LOG.info(f"Cache miss for URL: {url}, fetching from ytdl")
                loop = asyncio.get_event_loop()
                dl_future = functools.partial(cls.yt.extract_info, url, download=False, process=False)

                # Run in a custom thread pool
                # https://www.integralist.co.uk/posts/python-asyncio/#introduction
                metadata = await loop.run_in_executor(cls.executor, dl_future)
                cache[url] = metadata
                cached = False

        if metadata is None or 'formats' not in metadata or not metadata['formats']:
            raise YTDLException(f"Nothing found for url: {url}")
        
        if 'quality' not in metadata['formats'][0]:
            LOG.info("No quality flag, using the first option")
            return cls(ctx, discord.FFmpegPCMAudio(metadata['formats'][0]['url'], **cls.FFMPEG_OPTIONS), data=metadata, cached=cached)

        # pick the best audio quality, I'm guessing this is the quality flag?
        sorted_formats = sorted(metadata['formats'], key=lambda x: x['quality'], reverse=True)
        LOG.info(f"Fetched URL: {sorted_formats[0]['url']}")

        return cls(ctx, discord.FFmpegPCMAudio(metadata['formats'][0]['url'], **cls.FFMPEG_OPTIONS), data=metadata, cached=cached)

class Track:

    def __init__(self, source: AsyncAudioSource):
        self.source = source

    def embed(self, title: str, color: discord.Color):
        embed = (discord.Embed(
                    title=title,
                    description='```css\n{0.source.title}\n```'.format(self), url=self.source.webpage_url,
                    color=color)
                .add_field(name='Requested by', value=self.source.requested_by)
                .add_field(name='Duration', value=self._convert_duration(self.source.duration))
                .set_thumbnail(url=self.source.thumbnail)
                .set_footer(text=f'Fetched from cache: {self.source.cached}'))

        return embed

    @staticmethod
    def topTracksEmbed(top_tracks: dict, color: discord.Color):

        embed = discord.Embed(
            title='Top Tracks!',
            color=color
        )

        for idx, (track_name, frequency) in enumerate(top_tracks.items()):
            embed.add_field(
                name=f'**{track_name}**',
                value=f'> Rank: {idx + 1}\n> Times played: {frequency}',
                inline=False
            )
        embed.set_footer(text=f'Data collected as of {datetime.now().isoformat()}')
        return embed

    def _convert_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        dur_str = []

        if days > 0:
            dur_str.append(f"{days} " + ("day" if days < 2 else "days"))
        if hours > 0:
            dur_str.append(f"{hours} " + ("hour" if hours < 2 else "hours"))
        if minutes > 0:
            dur_str.append(f"{minutes} " + ("minute" if minutes < 2 else "minutes"))
        if seconds > 0:
            dur_str.append(f"{seconds} " + ("second" if seconds < 2 else "seconds"))

        return ', '.join(dur_str)
