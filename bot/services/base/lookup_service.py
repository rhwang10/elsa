import re
import collections

class LookupService:

    def __init__(self):
        self.identified_counts = collections.defaultdict(int)
