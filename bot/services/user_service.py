import os
import requests
import asyncio
import logging

from bot.services.request_service import RequestService
from bot.cache.token_cache import TokenCache
from bot.util.log import setup_logging_queue

from bot.exceptions.exceptions import RequestException, UserException


LOG = logging.getLogger('simple')

class UserService(RequestService):

    def __init__(self, token_cache: TokenCache):
        super().__init__(token_cache)
        self.CACHED_USER_ENDPOINT = os.environ['CACHED_USER_ENDPOINT']

    async def get_user_id(self, name: str, id: int):

        params = {
            'name': name,
            'id': id
        }

        user_request = self._construct_awaitable(requests.get,
                                                 self.CACHED_USER_ENDPOINT,
                                                 params=params)
        try:
            user_data = await self._call(user_request)
            return user_data['id']
        except RequestException as err:
            LOG.error(f"UserService error while fetching userID: {str(err)}")
            raise UserException
