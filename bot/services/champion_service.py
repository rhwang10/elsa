import re
import collections

from .base.lookup_service import LookupService
from ..models.champions import Champion

from ..constants.champion_nicknames import (
    BRAUM,
    KHAZIX,
    LEESIN,
    MAOKAI,
    POPPY,
    SEJUANI
)

CHAMPIONS = [
    (champion, [champion.name.lower()]) for champion in Champion
]

CUSTOM_CHAMPIONS = {
    Champion.BRAUM: BRAUM,
    Champion.KHAZIX: KHAZIX,
    Champion.LEESIN: LEESIN,
    Champion.MAOKAI: MAOKAI,
    Champion.POPPY: POPPY,
    Champion.SEJUANI: SEJUANI
}

class ChampionService(LookupService):

    def __init__(self):
        super().__init__()
        # self.champion_regexes = [
        #     (l[0], "(" + "|".join(l[1]) + ")") for l in CHAMPIONS
        # ]
        self.champion_regexes = []

        for champion, nicknames in CHAMPIONS:

            if champion in CUSTOM_CHAMPIONS:
                self.champion_regexes.append((champion, "|".join(nicknames + CUSTOM_CHAMPIONS[champion])))
            else:
                self.champion_regexes.append((champion, "|".join(nicknames)))

        self.champion_base_url = f"https://na.op.gg/champion/"

    def lookup_champion(self, message):
        discord_message = message.content
        # clear the cache
        self.identified_counts.clear()
        self._obtain_champion_counts_from_msg(discord_message)
        sorted_champion_counts = sorted([(champion_model, frequency) for champion_model, frequency in self.identified_counts.items()], key = lambda x: x[1])
        try:
            return sorted_champion_counts[-1][0].name.lower()
        except IndexError:
            return "unknown"

    def _obtain_champion_counts_from_msg(self, msg):
        for champion, regex in self.champion_regexes:
            for keyword in regex.split("|"):
                if self._contains_word(msg, keyword):
                    self.identified_counts[champion] += 1

    def get_champion_analytics_profile(self, message):
        champion_name = self.lookup_champion(message)
        return self.champion_base_url + champion_name + "/statistics"

    def _contains_word(self, s, w):
        return f' {w} ' in f' {s} '
