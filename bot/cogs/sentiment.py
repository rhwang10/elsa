import discord
import asyncio

from discord.ext import commands

from bot.models.sentiment import SentimentResponse

class Sentiment(commands.Cog):

    def __init__(self, sentiment_service):
        self.sentiment_service = sentiment_service

    @commands.command(name='analyze')
    async def _analyze(self, ctx: commands.Context):
        content = ctx.message.clean_content.replace("!analyze", "").strip()

        if not content:
            await ctx.send("Nothing to analyze!")

        sentimentResp = await self.sentiment_service.get_sentiment(
            ctx.message.author.id,
            content,
            shouldPersist=False
        )

        sentiment = SentimentResponse(sentimentResp, ctx.author)

        await ctx.send(embed=sentiment.embed())

        print(sentimentResp)
