import discord
import os
import asyncio
import logging

from discord.ext import commands

from bot.cogs.track import Music
from bot.cogs.latency import Latency
from bot.cogs.message import Message
from bot.cogs.sentiment import Sentiment
from bot.cache.token_cache import TokenCache

from bot.services.user_service import UserService
from bot.services.message_service import MessageService
from bot.services.track_service import TrackService
from bot.services.sentiment_service import SentimentService

from bot.util.log import setup_logging_queue

setup_logging_queue()
LOG = logging.getLogger('simple')

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
client.remove_command('help')

token_cache = TokenCache()

user_service = UserService(token_cache)
message_service = MessageService(token_cache)
track_service = TrackService(token_cache)
sentiment_service = SentimentService(token_cache)

# Music Cog inspired by https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
client.add_cog(Music(client, track_service))
client.add_cog(Latency(client))
client.add_cog(Message(client, user_service, message_service, sentiment_service))
client.add_cog(Sentiment(sentiment_service))

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    LOG.info("Connected")

# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    LOG.info("Disconnected")

client.run(os.environ.get("BOT_TOKEN"))
