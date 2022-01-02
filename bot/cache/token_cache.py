import requests
import logging
from cachetools import TTLCache
from datetime import datetime, timedelta

from bot.util.auth import get_auth_config
from bot.util.log import setup_logging_queue

LOG = logging.getLogger('simple')

class TokenCache(TTLCache):

    def __init__(self):
        self.DEFAULT_MAX_SIZE = 2
        self.DEFAULT_TTL = timedelta(hours=22)
        self.HEADERS = {
            'content-type': 'application/json'
        }
        super().__init__(self.DEFAULT_MAX_SIZE, self.DEFAULT_TTL, timer=datetime.now)

        auth_config = get_auth_config()
        self.endpoint = auth_config["AUTH0_TOKEN_ENDPOINT"]
        self.data = {
            'client_id': auth_config["CLIENT_ID"],
            'client_secret': auth_config["CLIENT_SECRET"],
            'audience': auth_config["AUDIENCE"],
            'grant_type': auth_config["GRANT_TYPE"]
        }

    def __missing__(self, key):
        LOG.info("Refreshing Auth0 token")

        try:
            token_resp = requests.post(self.endpoint, headers=self.HEADERS, json=self.data)
            token_resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            LOG.error("Error refreshing Auth0 token")
            LOG.error(str(err))

        data = token_resp.json()
        self[key] = data['access_token']

        LOG.info("Successfully refreshed auth0 token!")
        return data['access_token']
