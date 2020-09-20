import re

from bot.models.question_intent import QuestionIntent
from bot.services.base.proposer import Proposer

class QuestionProposer(Proposer):

    def __init__(self):
        super()
        self.intents = [(QuestionIntent.UnknownQuestionIntent, 0.0001)]

    def determine_intent(self, input: str):
        words = self.clean(input)
        return self.intents[0]
