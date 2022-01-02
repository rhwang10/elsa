import requests
import functools
import asyncio

from bot.cache.token_cache import TokenCache
from bot.exceptions.exceptions import RequestException

from typing import Callable

RequestsCallable = Callable[[str], requests.models.Response]

class RequestService:

    def __init__(self, token_cache: TokenCache):
        self.token_cache = token_cache

    def _construct_awaitable(self,
                             func: RequestsCallable,
                             endpoint: str,
                             data: dict = None,
                             params: dict = None,
                             headers: dict = None):

        if headers is not None and 'Authorization' in headers:
            raise Exception("Can't construct an awaitable with existing bearer token")

        auth_header = {'Authorization': f'Bearer {self.token_cache["iduna-api"]}'}

        if headers is None:
            headers = auth_header
        else:
            headers.update(auth_header)

        return functools.partial(
            func, endpoint, data=data, params=params, headers=headers
        )

    async def _call(self, callable: Callable):
        loop = asyncio.get_event_loop()

        try:
            resp = await loop.run_in_executor(None, callable)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as err:
            raise RequestException(err)
        except Exception as err:
            raise RequestException(err)
