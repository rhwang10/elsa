import re

from services.base.lookup_service import LookupService

class QuestionService(LookupService):

    def __init__(self):
        super().__init__()

    def choose_random_name(self):
        profile_name = self.lookup_random_player()
        return self.base_url + profile_name
