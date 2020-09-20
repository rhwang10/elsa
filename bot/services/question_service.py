import re

from bot.services.base.lookup_service import LookupService

class QuestionService(LookupService):

    def __init__(self):
        super().__init__()

    def lookup(self, message):

        # determine question intent
        return message
