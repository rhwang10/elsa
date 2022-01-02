import os
import requests
import asyncio
import logging
import json

from bot.services.request_service import RequestService
from bot.cache.token_cache import TokenCache
from bot.util.log import setup_logging_queue

from bot.exceptions.exceptions import RequestException, CreateTrackEventException

LOG = logging.getLogger('simple')

class TrackService(RequestService):

    def __init__(self, token_cache: TokenCache):
        super().__init__(token_cache)
        self.TRACK_EVENTS_ENDPOINT = os.environ.get("TRACK_EVENTS_ENDPOINT")
        self.TOP_TRACKS_ENDPOINT = os.environ.get("TOP_TRACKS_ENDPOINT")

    async def get_top_tracks(self, guild_id: int, limit: int):
        top_tracks_request = self._construct_awaitable(
            requests.get,
            self.TOP_TRACKS_ENDPOINT + str(guild_id),
            params={'limit': limit})

        try:
            top_tracks_response = await self._call(top_tracks_request)
            return top_tracks_response
        except RequestException as err:
            LOG.error(f"Error while fetching top tracks: {str(err)}")
            raise TopTracksException(err)

    async def post_track_event(self, track_event: dict):

        create_track_event_callable = self._construct_awaitable(
            requests.post,
            self.TRACK_EVENTS_ENDPOINT,
            data=json.dumps(track_event))
        try:
            await self._call(create_track_event_callable)
        except RequestException as err:
            LOG.error(f"Error creating track event: {str(err)}")
            raise CreateTrackEventException(err)
        finally:
            LOG.info(f"Successful track event post to Iduna for track ID {track_event['id']}")
