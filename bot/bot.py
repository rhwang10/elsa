import discord
import threading
import os
import asyncio
import random
import re
import sched
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from re import search
from flask import Flask, request, jsonify

# from .models.intent import Intent
# from .models.question_intent import QuestionIntent
# from .constants.game_players import LeaguePlayers
#
# from concurrent.futures import ThreadPoolExecutor
#
# from .services.intent_proposer import IntentProposer
# from .services.question_proposer import QuestionProposer
# from .services.player_service import PlayerService
# from .services.question_service import QuestionService
# from .services.champion_service import ChampionService
# from .services.sqs.client import SQSClient
# from .services.dynamo.client import DynamoClient

# MAX_WORKERS = 3
client = discord.Client(intents=discord.Intents.all())
scheduler = AsyncIOScheduler()

MEMBERS_WHO_CAN_STREAM=['Biiig Chiiiick', 'ScholarOfTheFirstMeme', 'Scrub', 'ItsMike', 'jook']
GAME = 'League of Legends'
STOP_MESSAGES = ["elsa shut up", "elsa stop", "elsa pause"]
RESUME_MESSAEGS = ["elsa resume", "elsa start"]

# player_service = PlayerService()
# champion_service = ChampionService()
# question_service = QuestionService()

# message_events_sqs_client = SQSClient("ELSA_EMOJI_MESSAGE_EVENTS_QUEUE_URL")

# FLIPPING_CHOICES = ["(╯°Д°)╯︵/(.□ . \)", "ヽ(ຈل͜ຈ)ﾉ︵ ┻━┻", "(☞ﾟヮﾟ)☞ ┻━┻", "┻━┻︵ \(°□°)/ ︵ ┻━┻", "(┛ಠ_ಠ)┛彡┻━┻", "(╯°□°)╯︵ ┻━┻", "(ノಠ益ಠ)ノ彡┻━┻", "┻━┻︵ \(°□°)/ ︵ ┻━┻", "ʕノ•ᴥ•ʔノ ︵ ┻━┻", "(┛❍ᴥ❍﻿)┛彡┻━┻", "(╯°□°)╯︵ ┻━┻ ︵ ╯(°□° ╯)", "(ﾉ＾◡＾)ﾉ︵ ┻━┻"]
# UNFLIPPING_CHOICES = ["┬─┬ノ( ◕◡◕ ノ)", "┳━┳ ヽ(ಠل͜ಠ)ﾉ", "┏━┓┏━┓┏━┓ ︵ /(^.^/)", "┬─┬ノ( ಠ_ಠノ)", "(ヘ･_･)ヘ ┳━┳", "┳━┳ノ( OωOノ )", "┬──┬  ¯\_(ツ)", "┣ﾍ(^▽^ﾍ)Ξ(ﾟ▽ﾟ*)ﾉ┳━┳", "┬───┬ ノ༼ຈ ل͜ຈノ༽", "┬──┬  ノ( ゜-゜ノ)", "┏━┓ ︵ /(^.^/)"]
async def check():
    print("Running check!")
    for channel in client.get_all_channels():

        if not isinstance(channel, discord.VoiceChannel):
            continue

        members = channel.members
        for member in members:
            if await should_ping(member, channel):
                general_text_channel = client.get_channel(316021605555896332)
                await _type(general_text_channel, f"{member.mention} <:strim:921622886010195988> pls (if u need this msg to stop because its broken, type 'elsa stop'. to restart it, type 'elsa resume')")

# Called when the client is done preparing the data received
# from Discord. Usually after login is successful and the
# Client.guilds and co. are filled up.
@client.event
async def on_ready():
    # start a thread to poll members that are currently gaming
    scheduler.add_job(check, "cron", second="*/30")
    scheduler.start()
    print("Scheduler started successfully")

# Called when the client has disconnected from Discord.
# This could happen either through the internet being disconnected,
# explicit calls to logout, or Discord terminating
# the connection one way or the other.
# This function can be called many times.
@client.event
async def on_disconnect():
    scheduler.shutdown()
    print("Scheduler shut down successfully")

async def should_ping(member, channel):

    if not isinstance(channel, discord.VoiceChannel):
        return

    members = channel.members
    members_streaming = [m for m in members if m.voice.self_stream]

    """
     2) This member is in the channel
     3) This member is eligible to stream
     4) This member is not streaming currently
     5) This member is currently playing a game
     6) This game is League
     7) The number of members in the channel is greater than one
     8) There is no one streaming currently in the channel
    """

    decision =  member in channel.members                                               and \
            member.name in MEMBERS_WHO_CAN_STREAM                                       and \
            not member.voice.self_stream                                                and \
            (member.activity and member.activity.type == discord.ActivityType.playing)  and \
            member.activity.name == GAME                                                and \
            len(members) > 1                                                            and \
            len(members_streaming) == 0

    return decision

# Called when a member updates their profile
# This is called when one or more of the following things change
# status, activity, nickname, roles, pending

@client.event
async def on_member_update(previous_member_state, current_member_state):

    # If a league game has not started, return
    if current_member_state.activity.type != discord.ActivityType.playing or \
           current_member_state.activity.name != GAME:
        return

    for channel in client.get_all_channels():
        if await should_ping(current_member_state, channel):
            await _type(GENERAL_TEXT_CHANNEL, f"{member.mention} <:strim:921622886010195988> pls")

@client.event
async def on_message(message):
    # if message.author == client.user:
    #     return
    #
    # mentions = message.mentions
    # if len(mentions) == 0:
    #     await message.reply("Remember to give someone to get status!")
    # else:
    #     activ = mentions[0].activity
    #     if activ == None:
    #         await message.reply("None")
    #     else:
    #         await message.reply(activ.name)

    if message.author == client.user:
        return

    if message.content == "<:strim:921622886010195988>":
        await _type(message.channel, "<:strim:921622886010195988>")

    if any(x in message.content for x in STOP_MESSAGES):
        scheduler.pause()

    if any(x in message.content for x in RESUME_MESSAEGS):
        scheduler.resume()

# @client.event
# async def on_voice_state_update(member, before, after):
#     print("yes")

# @client.event
# async def on_message(message):
#
#     # Don't let bot respond to itself
#     if message.author == client.user:
#         return
#
#     if message.author.name != "Rythm":
#         persist_emojis(message)
#
#     # proposrs are stateful, we need to make new ones on each run
#     # todo: make proposers stateless
#     intent_proposer = IntentProposer()
#     question_proposer = QuestionProposer()
#     is_question = False
#
#     # Determine intent
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         intent_future = executor.submit(intent_proposer.determine_intent, (message.content))
#         question_intent_future = executor.submit(question_proposer.determine_intent, (message.content))
#
#         intent, intent_confidence = intent_future.result()[0], intent_future.result()[1]
#         question_intent, question_confidence = question_intent_future.result()[0], question_intent_future.result()[1]
#
#         print(f"Intent: {intent}, Confidence: {str(intent_confidence)}")
#         print(f"Question Intent: {question_intent}, Confidence: {str(question_confidence)}")
#
#         is_question = True if (question_confidence >= intent_confidence) else False
#
#     if is_question:
#         await route_question_intent(message, question_intent)
#     else:
#         await route_intent(message, intent)
#
#
# async def route_question_intent(message, intent):
#
#     channel = message.channel
#
#     if intent == QuestionIntent.EnoughForFivesIntent:
#
#         def filter_offline(member):
#             return member.status != discord.Status.offline and not member.bot
#
#         online_members = list(map(lambda x: x.name, filter(filter_offline, message.guild.members)))
#         league = list(filter(lambda x: x in LeaguePlayers, online_members))
#
#         if len(league) > 4:
#             await _type(channel, "Looks like it, online members that play league:\n" + ',\n'.join(league))
#         else:
#             await _type(channel, f"Nope, looks like we need {5 - len(league)} more. Current online members that play league:\n" + ',\n'.join(league))
#
#     if intent == QuestionIntent.SkillQuestionIntent:
#         msg = question_service.choose_random_name()
#         await _type(channel, msg)
#
#     if intent == QuestionIntent.WordFrequencyIntent:
#         await _type(channel, "Word frequencies disabled until I can migrate message consumer onto this app")
#         # last_word = message.content.split(" ")[-1]
#         # count = message_events_dynamo_client.get_word_frequency(message.author.id, last_word)
#         # await _type(channel, f"You have said the word {last_word} in this Discord server at least {count} time(s)")
#
#     if intent == QuestionIntent.UnknownQuestionIntent:
#         print("Unknown question intent")
#         # await _type(channel, "Unknown question")
#
# async def route_intent(message, intent):
#
#     channel = message.channel
#
#     if intent == Intent.PlayGameIntent:
#         print("Play game intent")
#         # await _type(channel, "Ability to send messages to other players to play a game is not yet implemented")
#
#     if intent == Intent.UpdateProfileIntent:
#         print("Update profile intent")
#         # await _type(channel, "Profiles are not yet implemented")
#
#     if intent == Intent.IdentifyPlayerIntent:
#         msg = player_service.get_player_opgg_profile(message)
#         await _type(channel, msg)
#
#     if intent == Intent.FlipTableIntent:
#         await _type(channel, random.choice(UNFLIPPING_CHOICES))
#
#     if intent == Intent.UnflipTableIntent:
#         await _type(channel, random.choice(FLIPPING_CHOICES))
#
#     if intent == Intent.ChampionInformationIntent:
#         msg = champion_service.get_champion_analytics_profile(message)
#         await _type(channel, msg)
#
#     if intent == Intent.UnknownIntent:
#         print("Unknown Intent")
#         # await _type(channel, "Unknown intent")
#
# def persist_emojis(msg):
#
#     pattern = re.compile("(?<=\<)(.*?)(?=\>)")
#     matched = pattern.findall(msg.content)
#
#     # If no emojis, return
#     if not matched:
#         return
#
#     # emoji is formatted like :peepoNotes:841521842316771358
#     for e in matched:
#
#         if e.startswith(":"):
#             emoji_name, emoji_id = e[1:].split(":")
#
#             sqs_msg = {
#                 "authorId": msg.author.id,
#                 "authorName": msg.author.name,
#                 "emojiId": emoji_id,
#                 "emojiName": emoji_name,
#                 "timestamp": msg.created_at.isoformat(),
#                 "channel": msg.channel.name,
#                 "voiceChannel": msg.author.voice.channel.name if msg.author.voice else ""
#             }
#
#             # Sends message to emoji message events queue
#             # Consumer will persist the message to DynamoDB elsa-emoji-events table
#             print("Writing message to SQS")
#             message_events_sqs_client.send_message(sqs_msg)


async def _type(channel, msg):
    await channel.trigger_typing()
    await asyncio.sleep(2)
    await channel.send(msg)

client.run(os.environ.get("BOT_TOKEN"))
