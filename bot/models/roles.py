from enum import Enum

from players import Player

class Role(Enum):
    TOP = [Player.BIG_CHICK, Player.MAKE_DEM_RAIN, Player.LA_CHURRO, Player.HIDDEN_KEY]
    JUNGLE = [Player.YEN_SID, Player.SAINTS_INTO_THE_SEA, Player.RESPECT_THE_PIPE]
    MID = [Player.HIDDEN_KEY, Player.STEFAN, Player.FREAKYWOODS]
    AD = [Player.YEN_SID, Player.FREAKYWOODS, Player.HIDDEN_KEY, Player.RESPECT_THE_PIPE, Player.LA_CHURRO]
    SUPPORT = [Player.LA_CHURRO, Player.YEN_SID, Player.RESPECT_THE_PIPE]
