import os
import requests
import asyncio
import logging
import json

from bot.services.request_service import RequestService
from bot.cache.token_cache import TokenCache
from bot.util.log import setup_logging_queue
from bot.exceptions.exceptions import SentimentCreateException

LOG = logging.getLogger('simple')

class SentimentService(RequestService):

    def __init__(self, token_cache: TokenCache):
        super().__init__(token_cache)
        self.SENTIMENT_CREATE_ENDPOINT = os.environ.get("SENTIMENT_CREATE_ENDPOINT")

    async def get_sentiment(self, discord_id: int, content: str, shouldPersist=False):

        create_sentiment_callable = self._construct_awaitable(
            requests.post,
            self.SENTIMENT_CREATE_ENDPOINT,
            data=json.dumps({"discord_id": discord_id, "content": content}),
            params={"persist": shouldPersist}
        )

        try:
            sentiment = await self._call(create_sentiment_callable)
            return sentiment
        except Exception as err:
            LOG.error(f"Error creating message sentiment record: {str(err)}")
            raise SentimentCreateException(err)
        finally:
            LOG.info(f"Successful sentiment analyzed for discordId: {discord_id}")
