import discord
import functools
import youtube_dl
import asyncio
import concurrent.futures
import logging

from cachetools import TTLCache
from discord.ext import commands

from bot.util.log import setup_logging_queue

LOG = logging.getLogger('simple')

class AsyncAudioSource(discord.PCMVolumeTransformer):

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
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    yt = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)

    def __init__(self,
                 source: discord.FFmpegPCMAudio,
                 data: dict,
                 volume: float = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data['title']
        self.description = data['description']
        self.is_downloaded = True

    @classmethod
    async def create(cls, url: str, cache: TTLCache):
        try:
            metadata = cache[url]
        except KeyError as e:
            LOG.info(f"Cache miss for URL: {url}, fetching from ytdl")
            loop = asyncio.get_event_loop()
            dl_future = functools.partial(cls.yt.extract_info, url, download=False, process=False)

            # Run in a custom thread pool
            # https://www.integralist.co.uk/posts/python-asyncio/#introduction
            metadata = await loop.run_in_executor(cls.executor, dl_future)
            cache[url] = metadata

        LOG.info(f"Fetched URL: {metadata['formats'][0]['url']}")

        return cls(discord.FFmpegPCMAudio(metadata['formats'][0]['url'], **cls.FFMPEG_OPTIONS), data=metadata)

class Track:

    def __init__(self, source: AsyncAudioSource):
        self.source = source
