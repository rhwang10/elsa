import re

from .base.lookup_service import LookupService

class PlayerService(LookupService):

    def __init__(self):
        super().__init__()

    def get_player_opgg_profile(self, message):
        profile_name = self.lookup(message)
        return self.base_url + profile_name
