import os
import requests
import asyncio
import logging

from bot.services.request_service import RequestService
from bot.cache.token_cache import TokenCache
from bot.util.log import setup_logging_queue

from bot.exceptions.exceptions import RequestException, MessageSelectionException

LOG = logging.getLogger('simple')

class MessageService(RequestService):

    def __init__(self, token_cache: TokenCache):
        super().__init__(token_cache)
        self.USER_MSG_ENDPOINT = os.environ['USER_MSG_ENDPOINT']

    async def get_message_for_user(self, user_id: int):

        message_request = self._construct_awaitable(requests.get,
                                                    self.USER_MSG_ENDPOINT + str(user_id))
        try:
            message_data = await self._call(message_request)
            return message_data['message']
        except RequestException as err:
            LOG.error(f"MessageServie error while fetching message for user: {str(err)}")
            raise MessageSelectionException
        except KeyError as err:
            LOG.warn(f"Not message selected for user ID: {user_id}")
            return None
