
class LookupService:

    def __init__(self):
        self.base_url = "https://na.op.gg/summoner/userName="

    def lookup(self, message):
        raise NotImplementedError
