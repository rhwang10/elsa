import re

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

from bot.services.base.lookup_service import LookupService
from bot.models.players import Player

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
        self.identified_counts = {}

    def lookup(self, message):

        discord_message = message.content
        self._obtain_counts_from_msg(discord_message)
        sorted_player_counts = sorted([(k,v) for k,v in self.identified_counts.items()], key = lambda x: x[1])
        op_gg_name = sorted_player_counts[-1][0].get_opgg_name()
        return self.base_url + op_gg_name

    def _obtain_counts_from_msg(self, msg):
        for player, regex in self.player_regexes:
            self.identified_counts[player] = len(re.findall(regex, msg))
