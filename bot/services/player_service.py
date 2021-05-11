import re
import random

from .base.lookup_service import LookupService

from ..models.players import Player

from ..constants.nicknames import (
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

PLAYERS = [
    (Player.SAINTS_INTO_THE_SEA, JAKE),
    (Player.BIG_CHICK, DAVID),
    (Player.MAKE_DEM_RAIN, SENIOR_DAVID),
    (Player.SILHOUETTE, SAYED),
    (Player.HIDDEN_KEY, KLAI),
    (Player.RESPECT_THE_PIPE, GEORGE),
    (Player.FREAKYWOODS, HENRY),
    (Player.YEN_SID, ROBERT),
    (Player.LA_CHURRO, MIKE),
    (Player.MORGORATH77, STEFAN)
]

class PlayerService(LookupService):

    def __init__(self):
        super().__init__()
        self.player_regexes = [
            (p[0], "(" + "|".join(p[1]) + ")") for p in PLAYERS
        ]
        self.base_url = "https://na.op.gg/summoner/userName="

    def lookup(self, message):
        discord_message = message.content
        self._obtain_counts_from_msg(discord_message)
        sorted_player_counts = sorted([(player_model, frequency) for player_model, frequency in self.identified_counts.items()], key = lambda x: x[1])
        return sorted_player_counts[-1][0].get_opgg_name()

    def lookup_random_player(self):
        return PLAYERS[random.randint(0, len(PLAYERS) - 1)][0].get_opgg_name()

    def _obtain_counts_from_msg(self, msg):
        for player, regex in self.player_regexes:
            self.identified_counts[player] = len(re.findall(regex, msg))

    def get_player_opgg_profile(self, message):
        profile_name = self.lookup(message)
        return self.base_url + profile_name
