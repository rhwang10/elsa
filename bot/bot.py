import discord
import os
import asyncio
import time
import requests
import psycopg2
import urllib.parse as urlparse
import json
import sseclient
import pprint

from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

from discord.ext import commands

from bot.cache.yt_cache import YTCache

CACHED_USER_ENDPOINT = os.environ['CACHED_USER_ENDPOINT']
USER_MSG_ENDPOINT = os.environ['USER_MSG_ENDPOINT']
TRACK_ENDPOINT = os.environ['TRACK_ENDPOINT']

COMMANDS = {"!play", "!kick", "!pause", "!resume"}

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')

yt_metadata = YTCache()

@client.command()
async def play(ctx, url):

    # If author is not part of a voice channel, do not allow them to start a song
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send(f"{ctx.author.name}, you're not in a voice channel...")
        return

    channel = ctx.author.voice.channel
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice == None:
        vc = await channel.connect()
    else:
        vc = voice

    hashed_url = YTCache.hash(url)

    if not vc.is_playing():
        info =get_metadata_from_cache(hashed_url)
        URL = info['formats'][0]['url']
        # vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        print(f"Playing {URL}")
        vc.is_playing()
    else:
        await ctx.send("I'm already playing a song!")
        return

@client.command()
async def kick(ctx):

    if not ctx.author.voice or not ctx.author.voice.channel:
        return

    await ctx.voice_client.disconnect()

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

@client.event
async def on_message(message):

    # Process commands first
    await client.process_commands(message)

    # Short circuit if bot is author, or message content contains a command
    if message.author == client.user or \
       any(message.content.find(cmd) for cmd in COMMANDS):
        return

    params = {
        'name': message.author.name,
        'id': message.author.discriminator
    }

    user_response = get(CACHED_USER_ENDPOINT, params=params)

    if not user_response or not user_response["id"]:
        print("Error occured, or no user found, exiting gracefully")
        return

    target_user_id = user_response["id"]
    message_response = get(USER_MSG_ENDPOINT + str(target_user_id))

    if message_response:
        await _type(message.channel, message_response['message'])

async def _type(channel, msg):
    await channel.trigger_typing()
    await asyncio.sleep(2)
    await channel.send(msg)

def get(req, params=None):
    try:
        resp = requests.get(req, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as err:
        print(err)
    return None

def get_metadata_from_cache(hashed_url):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = yt_metadata[hashed_url]
            print(f"Cache hit! Fetching {url} from cache")
        except KeyError as e:
            print(f"Cache miss..")
            info = ydl.extract_info(url, download=False)
            yt_metadata[hashed_url] = info
    return info

client.run(os.environ.get("BOT_TOKEN"))
