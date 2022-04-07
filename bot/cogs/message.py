import discord
import asyncio
import logging

from bot.services.user_service import UserService
from bot.services.message_service import MessageService
from bot.services.sentiment_service import SentimentService

from discord.ext import commands

from bot.util.log import setup_logging_queue

setup_logging_queue()
LOG = logging.getLogger('simple')

class Message(commands.Cog):

    def __init__(self,
                 bot: commands.Bot,
                 user_service: UserService,
                 message_service: MessageService,
                 sentiment_service: SentimentService):
        self.bot = bot
        self.user_service = user_service
        self.message_service = message_service
        self.sentiment_service = sentiment_service

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content.startswith("!"):
            return

        sentimentResp = await self.sentiment_service.get_sentiment(
            message.author.id,
            message.clean_content,
            shouldPersist=True
        )

        if sentimentResp:
            LOG.info(sentimentResp)

        if "sing your favorite song" in message.content:
            ctx = await client.get_context(message)
            await ctx.send("🥰")
            return await ctx.invoke(client.get_command('play'), url="https://www.youtube.com/watch?v=l1uoTMkhUiE")

        target_user_id = await self.user_service.get_user_id(message.author.id)
        message_to_send = await self.message_service.get_message_for_user(target_user_id)

        if message_to_send:
            await self._type(message.channel, message_to_send)


    @commands.command(name='tell')
    async def _tell(self, ctx: commands.Context, targetUser):
        try:
            discord_id = targetUser[3:len(targetUser) - 1]
            msg = ' '.join(ctx.message.content.split()[2:])
        except Exception as e:
            await ctx.send("Something went wrong, I can't understand :)")
            return

        author_user_id = await self.user_service.get_user_id(ctx.message.author.id)
        target_user_id = await self.user_service.get_user_id(discord_id)

        req = {
            "author_user_id": str(author_user_id),
            "target_user_id": str(target_user_id),
            "message": targetUser + " " + msg,
            "is_active": True,
            "rule": {
                "tokens": 1,
                "seconds": 2628000 # one month in seconds
            }
        }

        created_message = await self.message_service.create_message(req)

        await ctx.send("Got it")

    async def _type(self, channel, msg):
        await channel.trigger_typing()
        await asyncio.sleep(2)
        await channel.send(msg)
