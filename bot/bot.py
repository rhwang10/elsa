import discord
import os
import asyncio
import logging

from discord.ext import commands

from bot.cogs.track import Music
from bot.cogs.latency import Latency
from bot.cogs.stocks import Stocks

from bot.redis.client import RedisClient
# from bot.cogs.message import Message
# from bot.cogs.sentiment import Sentiment
# from bot.cache.token_cache import TokenCache

# from bot.services.user_service import UserService
# from bot.services.message_service import MessageService
# from bot.services.track_service import TrackService
# from bot.services.sentiment_service import SentimentService

from bot.util.log import setup_logging_queue

setup_logging_queue()
LOG = logging.getLogger('simple')

async def setup(client, redisClient):
    # Music Cog inspired by https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
    await client.add_cog(Music(client))
    await client.add_cog(Latency(client, redisClient))
    await client.add_cog(Stocks(client))

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
client.remove_command('help')

# token_cache = TokenCache()

redisClient = RedisClient({
    'host': os.environ.get('REDIS_HOST') or 'localhost',
    'port': os.environ.get('REDIS_PORT') or 6379,
    'password': os.environ.get('REDIS_PASSWORD') or 'password'
})

# user_service = UserService(token_cache)
# message_service = MessageService(token_cache)
# track_service = TrackService(token_cache)
# sentiment_service = SentimentService(token_cache)


# RIP the most annoying feature of all time
# client.add_cog(Message(client, user_service, message_service, sentiment_service))


# client.add_cog(Sentiment(sentiment_service))

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    LOG.info("Ready to receive requests")

# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    LOG.info("Disconnected")

async def main():
    async with client:
        await setup(client, redisClient)
        await client.start(os.environ.get("BOT_TOKEN"))

@client.hybrid_command()
async def test(ctx):
    await ctx.send("This is a hybrid command!")


@client.hybrid_command()
async def register(ctx):
    await ctx.send("Would you like to give Elsa permission to collect your message data (Respond yes/y)?")

    def check_response(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    
    try:
        response = await client.wait_for('message', check=check_response)
    except asyncio.TimeoutError:
        await ctx.send("No response, timing out..")
        return

    if response.content.lower() not in ["yes", "y"]:
        await ctx.send("Ok, I won't collect your data")
        return
    
    await ctx.send(f"Ack, Elsa will collect and save {ctx.author.global_name}'s message history")

@client.command()
async def sync(ctx):
    print("sync command")
    await client.tree.sync()
    await ctx.send('Command tree synced.')

asyncio.run(main())