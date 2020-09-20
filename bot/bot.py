import discord
import threading
import os

from re import search

from bot.models.intent import Intent

from concurrent.futures import ThreadPoolExecutor
from .services.proposer import Proposer
from .services.player_service import PlayerService

MAX_WORKERS = 3

client = discord.Client()
player_service = PlayerService()

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    print("We have logged in")


# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    print("We have logged out")


@client.event
async def on_message(message):

    # Don't let bot respond to itself
    if message.author == client.user:
        return

    if not (search("elsa", message.content.lower())):
        return

    proposer = Proposer()

    # Determine intent
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future = executor.submit(proposer.determine_intent, (message.content))
        intent = future.result()[0]

    if intent == Intent.PlayGameIntent:
        await message.channel.send("PlayGameIntent")

    if intent == Intent.AskQuestionIntent:
        await message.channel.send("AskQuestionIntent")

    if intent == Intent.UpdateProfileIntent:
        await message.channel.send("UpdateProfileIntent")

    if intent == Intent.IdentifyPlayerIntent:
        msg = player_service.lookup_player(message.content)
        await message.channel.send(msg)

    if intent == Intent.UnknownIntent:
        await message.channel.send(f"Hey there {message.author}, I don't know what you're trying to do")


client.run(os.environ.get("BOT_TOKEN"))
