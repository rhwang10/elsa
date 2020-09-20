import discord
import threading
import os

from re import search

from bot.models.intent import Intent

from concurrent.futures import ThreadPoolExecutor

from .services.intent_proposer import IntentProposer
from .services.question_proposer import QuestionProposer
from .services.player_service import PlayerService
from .services.question_service import QuestionService

MAX_WORKERS = 3

client = discord.Client()
player_service = PlayerService()
question_service = QuestionService()

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    print("Logged in")


# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    print("Logged out")


@client.event
async def on_message(message):

    # Don't let bot respond to itself
    if message.author == client.user:
        return

    if not (search("elsa", message.content.lower())):
        return

    # proposrs are stateful, we need to make new ones on each run
    # todo: make proposers stateless
    intent_proposer = IntentProposer()
    question_proposer = QuestionProposer()

    # Determine intent
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        intent_future = executor.submit(intent_proposer.determine_intent, (message.content))
        question_intent_future = executor.submit(question_proposer.determine_intent, (message.content))

        intent = intent_future.result()[0]
        question_intent = question_intent_future.result()[0]

    if intent == Intent.PlayGameIntent:
        await message.channel.send("Ability to send messages to other players to play a game is not yet implemented")

    if intent == Intent.AskQuestionIntent:
        msg = question_service.lookup(message)
        await message.channel.send(msg)

    if intent == Intent.UpdateProfileIntent:
        await message.channel.send("Profiles are not yet implemented")

    if intent == Intent.IdentifyPlayerIntent:
        msg = player_service.lookup(message)
        await message.channel.send(msg)

    if intent == Intent.UnknownIntent:
        await message.channel.send(f"Hey there {message.author}, I don't know what you're trying to do")


client.run(os.environ.get("BOT_TOKEN"))
