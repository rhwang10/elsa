import discord
import os
import asyncio
import time
import requests

from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

from discord.ext import commands

from bot.models.track import AsyncAudioSource
from bot.cogs.track import Music

CACHED_USER_ENDPOINT = os.environ['CACHED_USER_ENDPOINT']
USER_MSG_ENDPOINT = os.environ['USER_MSG_ENDPOINT']

from bot.util.log import setup_logging_queue

setup_logging_queue()

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')

# Music Cog inspired by https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
client.add_cog(Music(client))

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    print("Connected")

# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    print("Disconnected")

# Called when a member updates their profile
# This is called when one or more of the following things change
# status, activity, nickname, roles, pending
@client.event
async def on_member_update(previous_member_state, current_member_state):
    pass

# @client.event
# async def on_message(message):
#
#     if message.author == client.user:
#         return
#
#     params = {
#         'name': message.author.name,
#         'id': message.author.discriminator
#     }
#
#     user_response = get(CACHED_USER_ENDPOINT, params=params)
#
#     if not user_response:
#         print("No user found, exiting gracefully")
#         return
#
#     target_user_id = user_response["id"]
#     message_response = get(USER_MSG_ENDPOINT + str(target_user_id))
#
#     if message_response:
#         await _type(message.channel, message_response['message'])
#
#     await client.process_commands(message)
#
# async def _type(channel, msg):
#     await channel.trigger_typing()
#     await asyncio.sleep(2)
#     await channel.send(msg)
#
# def get(req, params=None):
#     try:
#         resp = requests.get(req, params=params)
#         resp.raise_for_status()
#         return resp.json()
#     except requests.exceptions.HTTPError as err:
#         print(err)
#         return None

client.run(os.environ.get("BOT_TOKEN"))
