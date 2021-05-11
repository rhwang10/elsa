from enum import Enum

class Intent(Enum):
    UnknownIntent = 1
    PlayGameIntent = 2
    AskQuestionIntent = 3
    UpdateProfileIntent = 4
    IdentifyPlayerIntent = 5
    FlipTableIntent = 6
    UnflipTableIntent = 7
    ChampionInformationIntent = 8
