import re

from bot.models.question_intent import QuestionIntent
from bot.services.base.proposer import Proposer

IS_SKILL_QUESTION_INTENT = "(great|good|bad|best|worst|horrible|amazing|incredible|terrible|feeder|toxic|mid|top|laner|adc|bot|support|supp|jg|jungle|bottom|ad carry|ad|carry|htv|hidden tilt village)"
IS_ENOUGH_FOR_FIVES_INTENT = "(enough|fives|enough for fives|5s|fives|5|have|have enough|enough for 5s|do|we|have|cinco|enough feeders)"

class QuestionProposer(Proposer):

    def __init__(self):
        super()
        self.intents = [(QuestionIntent.UnknownQuestionIntent, 0.0001)]

    def determine_intent(self, input: str):
        words = self.clean(input)
        self.is_skill_question_intent(words)
        self.is_enough_for_fives_intent(words)
        return max(self.intents, key=lambda x: x[1])

    def is_skill_question_intent(self, words):
        self.intents.append(
            (QuestionIntent.SkillQuestionIntent, self.count_keywords(IS_SKILL_QUESTION_INTENT, words) / float(len(words)))
        )

    def is_enough_for_fives_intent(self, words):
        self.intents.append(
            (QuestionIntent.EnoughForFivesIntent, self.count_keywords(IS_ENOUGH_FOR_FIVES_INTENT, words) / float(len(words)))
        )
