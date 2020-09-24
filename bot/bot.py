import discord
import threading
import os

from re import search

from bot.models.intent import Intent
from bot.models.question_intent import QuestionIntent
from bot.constants.game_players import LeaguePlayers

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
    is_question = False

    # Determine intent
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        intent_future = executor.submit(intent_proposer.determine_intent, (message.content))
        question_intent_future = executor.submit(question_proposer.determine_intent, (message.content))

        intent, intent_confidence = intent_future.result()[0], intent_future.result()[1]
        question_intent, question_confidence = question_intent_future.result()[0], question_intent_future.result()[1]

        print(question_confidence)
        print(intent_confidence)
        is_question = True if (question_confidence >= intent_confidence) else False

    # def is_question(message):
    #     return search("\?", message.content)

    if is_question:
        await route_question_intent(message, question_intent)
    else:
        await route_intent(message, intent)


async def route_question_intent(message, intent):

    if intent == QuestionIntent.EnoughForFivesIntent:

        def filter_offline(member):
            return member.status != discord.Status.offline and not member.bot

        online_members = list(map(lambda x: x.name, filter(filter_offline, message.guild.members)))
        league = list(filter(lambda x: x in LeaguePlayers, online_members))

        if len(league) > 5:
            await message.channel.send("Looks like it, online members that play league:\n" + ',\n'.join(league))
        else:
            await message.channel.send(f"Nope, looks like we need {5 - len(league)} more. Current online members that play league:\n" + ',\n'.join(league))

    if intent == QuestionIntent.SkillQuestionIntent:
        await message.channel.send("SkillQuestionIntent, not yet implemented")

    if intent == QuestionIntent.UnknownQuestionIntent:
        await message.channel.send(f"Hey there {message.author}, I don't know what you're trying to ask me")

async def route_intent(message, intent):

    if intent == Intent.PlayGameIntent:
        await message.channel.send("Ability to send messages to other players to play a game is not yet implemented")

    if intent == Intent.UpdateProfileIntent:
        await message.channel.send("Profiles are not yet implemented")

    if intent == Intent.IdentifyPlayerIntent:
        msg = player_service.lookup(message)
        await message.channel.send(msg)

    if intent == Intent.UnknownIntent:
        await message.channel.send("eat my ass bitch")


client.run(os.environ.get("BOT_TOKEN"))
