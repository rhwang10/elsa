import random
import logging
import yfinance
import discord

from cachetools import TTLCache
from datetime import datetime, timedelta
from discord.ext import commands

from bot.util.color import RED, GREEN

LOG = logging.getLogger('simple')

class Stock:

    DOWNWARD = [
        "<:CEASE:1208948231590121502>",
        "<:s2jFEELS:844089871424684052>",
        "<:Sadge:805991489854898186>"
    ]

    UPWARD = [
        "<:POGGERS:805991381314306079>",
        "<:Smilers:1156459698187415552>",
        "<:peepoBlanket:1208948233020112947>"
    ]

    def __init__(self, info):
        self.info = info
        self.current_price = self.info["currentPrice"]
        self.previous_close = self.info["regularMarketPreviousClose"]
        self.percent_change = ((self.current_price - self.previous_close) / self.previous_close) * 100
    
    def _title(self):

        current_price = self.info["currentPrice"]
        previous_close = self.info["regularMarketPreviousClose"]
        percent_change = ((current_price - previous_close) / previous_close) * 100

        num_emoji = random.randint(5, 9)

        emoji_str = " ".join([random.choice(self.UPWARD) for _ in range(num_emoji)]) if percent_change > 0 else " ".join([random.choice(self.DOWNWARD) for _ in range(num_emoji)])

        if percent_change > 0:
            return f"{self.info['symbol']} IS VERY POG!!! {emoji_str}"

        return f"{self.info['symbol']} is sadge... {emoji_str} "
    
    def _color(self):
        return GREEN if self.percent_change > 0 else RED

    def embed(self):
        embed = discord.Embed(title=self._title(), color=self._color())
        embed.add_field(name="Current Price", value=self.info["currentPrice"], inline=False)
        embed.add_field(name="Previous Close", value=self.info["regularMarketPreviousClose"], inline=False)
        embed.add_field(name="Percent Change", value=f"{round(self.percent_change, 2)}%", inline=False)
        return embed
        
class Stocks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cache = TTLCache(500, timedelta(minutes=1), timer=datetime.now)

    @commands.command(name='stonks')
    async def _stonks(self, ctx: commands.Context, *, ticker: str):
        user = ctx.author.id
        stock_ticker = ticker.upper()


        if stock_ticker in self.cache:
            LOG.info(f"Fetched {stock_ticker} from cache")
            stock_info = self.cache[stock_ticker]
        else:
            stock = yfinance.Ticker(stock_ticker)
            stock_info = stock.info
            self.cache[stock_ticker] = stock_info
        try:
            stock_price = stock_info["currentPrice"]
        except Exception as e:
            LOG.error(f"Failed to fetch {stock_ticker} from yfinance: {e}")
            await ctx.send("Something went wrong, maybe this ticker does not exist. Try again later")

        await ctx.send(embed=Stock(stock_info).embed())
        
