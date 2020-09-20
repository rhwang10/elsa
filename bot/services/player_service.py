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
    MIKE
)

from bot.models.players import Player

PLAYERS = [
    (Player.SAINTS_INTO_THE_SEA, JAKE),
    (Player.BIG_CHICK, DAVID),
    (Player.MAKE_DEM_RAIN, SENIOR_DAVID),
    (Player.SILHOUETTE, SAYED),
    (Player.HIDDEN_KEY, KLAI),
    (Player.RESPECT_THE_PIPE, GEORGE),
    (Player.FREAKWOODS, HENRY),
    (Player.YEN_SID, ROBERT),
    (Player.LA_CHURRO, MIKE)
]

class PlayerService:

    def __init__(self):
        self.base_url = "https://na.op.gg/summoner/userName="
        self.player_regexes = [
            (p[0], "(" + "|".join(p[1]) + ")") for p in PLAYERS
        ]
        self.identified_counts = {}

    def lookup_player(self, discord_message):

        self._obtain_counts_from_msg(discord_message)
        sorted_player_counts = sorted([(k,v) for k,v in self.identified_counts.items()], key = lambda x: x[1])
        op_gg_name = sorted_player_counts[-1][0].get_opgg_name()
        return self.base_url + op_gg_name

    def _obtain_counts_from_msg(self, msg):
        for player, regex in self.player_regexes:
            self.identified_counts[player] = len(re.findall(regex, msg))
