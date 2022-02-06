import discord
import asyncio

from bot.services.user_service import UserService
from bot.services.message_service import MessageService

from discord.ext import commands

class Message(commands.Cog):

    def __init__(self, bot: commands.Bot, user_service: UserService, message_service: MessageService):
        self.bot = bot
        self.user_service = user_service
        self.message_service = message_service

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
