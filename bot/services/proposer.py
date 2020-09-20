import nltk
import re

from bot.models.intent import Intent
from bot.constants.nicknames import (
    JAKE,
    DAVID,
    SENIOR_DAVID,
    SAYED,
    KLAI,
    GEORGE,
    HENRY,
    ROBERT,
    MIKE
)

from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize

from typing import List

IS_PLAY_GAME_INTENT = "(play|minecraft|league of legends|league|valorant|game|among|us|among us)"
IS_UPDATE_PROFILE_INTENT = "(update|change|email)"
IS_ASK_QUESTION_INTENT = "(\?)"
IS_IDENTIFY_PLAYER_INTENT = "(opgg|op|gg|identify|get|find|who|profile" + \
    "|".join(JAKE + DAVID + SENIOR_DAVID + SAYED + KLAI + GEORGE + HENRY + ROBERT + MIKE) + \
")"

class Proposer:

    def __init__(self):
        self.intents = [(Intent.UnknownIntent, 0.0001)]

    def determine_intent(self, input: str):
        self.validate(input)
        stripped_words = self.strip_stopwords(input)
        words = ' '.join(stripped_words)

        self.isPlayGameIntent(words)
        self.isUpdateProfileIntent(words)
        self.isAskQuestionIntent(words)
        self.isIdentifyPlayerIntent(words)

        return max(self.intents, key=lambda x: x[1])

    def isPlayGameIntent(self, words):
        self.intents.append(
            (Intent.PlayGameIntent, self.count_keywords(IS_PLAY_GAME_INTENT, words) / float(len(words)))
        )

    def isUpdateProfileIntent(self, words):
        self.intents.append(
            (Intent.UpdateProfileIntent, self.count_keywords(IS_UPDATE_PROFILE_INTENT, words) / float(len(words)))
        )

    def isAskQuestionIntent(self, words):
        self.intents.append(
            (Intent.AskQuestionIntent, self.count_keywords(IS_ASK_QUESTION_INTENT, words) / float(len(words)))
        )

    def isIdentifyPlayerIntent(self, words):
        self.intents.append(
            (Intent.IdentifyPlayerIntent, self.count_keywords(IS_IDENTIFY_PLAYER_INTENT, words) / float(len(words)))
        )

    def count_keywords(self, regex, words):
        return len(re.findall(regex, words))


    def validate(self, input: str):
        if not isinstance(input, str):
            raise Exception("Need a valid string in the proposer to tokenize")

    def strip_stopwords(self, input: str) -> List:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(input)

        return [word for word in word_tokens if word not in stop_words]
