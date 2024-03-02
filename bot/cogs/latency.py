import discord
import asyncio

from discord.ext import commands
from bot.redis.client import RedisClient

LATENCY_SORTED_SET = 'latency_sorted_set'

class Latency(commands.Cog):

    def __init__(self, bot: commands.Bot, redisClient: RedisClient):
        self.bot = bot
        self.redis = redisClient

    @commands.command(name='ping')
    async def _ping(self, ctx: commands.Context):
        user = ctx.author.id

        new_count = self.redis.increment_sorted_set(LATENCY_SORTED_SET, user, 1)

        await ctx.reply(f'Pong ~ took about {round(self.bot.latency * 1000)} ms. {ctx.author.global_name} has pinged {new_count} times!')

    @commands.command(name='pong')
    async def _pong(self, ctx: commands.Context):
        await ctx.reply("Wait, I'm supposed to do that...")
    
    @commands.command(name='pingthese')
    async def _pong(self, ctx: commands.Context):
        await ctx.reply(f"{ctx.author.global_name} is a massive bitch")