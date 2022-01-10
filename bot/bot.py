import discord
import os
import asyncio
import logging

from discord.ext import commands

from bot.cogs.track import Music
from bot.cogs.latency import Latency

from bot.cache.token_cache import TokenCache

from bot.services.user_service import UserService
from bot.services.message_service import MessageService
from bot.services.track_service import TrackService

from bot.util.log import setup_logging_queue

setup_logging_queue()
LOG = logging.getLogger('simple')

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
client.remove_command('help')

token_cache = TokenCache()

user_service = UserService(token_cache)
message_service = MessageService(token_cache)
track_service = TrackService(token_cache)

# Music Cog inspired by https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
client.add_cog(Music(client, track_service))
client.add_cog(Latency(client))

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

# Called when a member updates their profile
# This is called when one or more of the following things change
# status, activity, nickname, roles, pending
@client.event
async def on_member_update(previous_member_state, current_member_state):
    pass

@client.event
async def on_message(message):

    await client.process_commands(message)

    if message.author == client.user or message.content.startswith("!"):
        return

    if "sing your favorite song" in message.content:
        ctx = await client.get_context(message)
        await ctx.send("🥰")
        return await ctx.invoke(client.get_command('play'), url="https://www.youtube.com/watch?v=l1uoTMkhUiE")

    target_user_id = await user_service.get_user_id(message.author.id)
    message_to_send = await message_service.get_message_for_user(target_user_id)

    if message_to_send:
        await _type(message.channel, message_to_send)

async def _type(channel, msg):
    await channel.trigger_typing()
    await asyncio.sleep(2)
    await channel.send(msg)

client.run(os.environ.get("BOT_TOKEN"))
