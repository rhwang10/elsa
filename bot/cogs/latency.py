import discord
import asyncio

from discord.ext import commands

class Latency(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='ping')
    async def _ping(self, ctx: commands.Context):
        await ctx.reply(f'Pong ~ took about {round(self.bot.latency * 1000)} ms')
