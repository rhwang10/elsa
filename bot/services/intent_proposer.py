# import nltk
# import re

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
    MIKE,
    STEFAN
)
from bot.services.base.proposer import Proposer

# from nltk.corpus import stopwords
# nltk.download('stopwords')
# nltk.download('punkt')
# from nltk.tokenize import word_tokenize
# from typing import List

IS_PLAY_GAME_INTENT = "(play|minecraft|league of legends|league|valorant|game|among|us|among us)"
IS_UPDATE_PROFILE_INTENT = "(update|change|email)"
IS_IDENTIFY_PLAYER_INTENT = "(opgg|op|gg|identify|get|find|who|profile" + \
    "|".join(JAKE + DAVID + SENIOR_DAVID + SAYED + KLAI + GEORGE + HENRY + ROBERT + MIKE + STEFAN) + \
")"
IS_FLIP_TABLE_INTENT = "(┻(─+|━+)┻)"
IS_UNFLIP_TABLE_INTENT = "(┳(─+|━+)┳|┏(─+|━+)┓)"

class IntentProposer(Proposer):

    def __init__(self):
        super()
        self.intents = [(Intent.UnknownIntent, 0.0001)]

    def determine_intent(self, input: str):
        words = self.clean(input)
        self.is_play_game_intent(words)
        self.is_update_profile_intent(words)
        self.is_identify_player_intent(words)
        self.is_flip_table_intent(words)
        self.is_unflip_table_intent(words)
        return max(self.intents, key=lambda x: x[1])

    def is_flip_table_intent(self, words):
        confidence = 0
        if self.count_keywords(IS_FLIP_TABLE_INTENT, words) > 0:
            confidence = float('inf')
        self.intents.append(
            (Intent.FlipTableIntent, confidence)
        )

    def is_unflip_table_intent(self, words):
        confidence = 0
        if self.count_keywords(IS_UNFLIP_TABLE_INTENT, words) > 0:
            confidence = float('inf')
        self.intents.append(
            (Intent.UnflipTableIntent, confidence)
        )

    def is_play_game_intent(self, words):
        self.intents.append(
            (Intent.PlayGameIntent, self.count_keywords(IS_PLAY_GAME_INTENT, words) / float(len(words)))
        )

    def is_update_profile_intent(self, words):
        self.intents.append(
            (Intent.UpdateProfileIntent, self.count_keywords(IS_UPDATE_PROFILE_INTENT, words) / float(len(words)))
        )

    def is_identify_player_intent(self, words):
        # Let's weight identify keywords higher than other keywords
        self.intents.append(
            (Intent.IdentifyPlayerIntent, self.count_keywords(IS_IDENTIFY_PLAYER_INTENT, words) * 2 / float(len(words)))
        )
