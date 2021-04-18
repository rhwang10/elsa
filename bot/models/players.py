from enum import Enum

class Player(Enum):
    BIG_CHICK = "biiig+chiiiick"
    YEN_SID = "yensid"
    MAKE_DEM_RAIN = "makedemrain"
    FREAKYWOODS = "freakywoods"
    LA_CHURRO = "la+churro"
    SILHOUETTE = "silhouette"
    SAINTS_INTO_THE_SEA = "SaintsIntoTheSea"
    HIDDEN_KEY = "KLAI"
    RESPECT_THE_PIPE = "RespectThePipe"
    MORGORATH77 = "morgorath77"

    def get_opgg_name(self):
        return self.value
