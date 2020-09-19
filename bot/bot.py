import discord
import threading
import os

from concurrent.futures import ThreadPoolExecutor
from .services.proposer import Proposer

TOKEN = "NzU2Njc3MjY5NzMyNDU4NTQ2.X2VUnw.EyEIbrMW2CXcO0ETfjLFrrRY250"
MAX_WORKERS = 3


client = discord.Client()
proposer = Proposer()

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

    # Determine intent
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.submit(proposer.determine_intent, (message.content))


    # Respond to user
    await message.channel.send(f"hey {message.author}!")


client.run(os.environ.get("BOT_TOKEN"))
