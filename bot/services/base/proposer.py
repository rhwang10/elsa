import nltk
import re

from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from typing import List

stop_words = set(stopwords.words('english'))

class Proposer:

    def __init__(self):
        self.intents = list()

    def determine_intent(self, input: str):
        raise NotImplementedError

    def clean(self, input: str) -> List:
        if not isinstance(input, str):
            raise Exception("Need a valid string in the proposer to tokenize")

        word_tokens = word_tokenize(input)
        return ' '.join([word.lower() for word in word_tokens if word not in stop_words])

    def count_keywords(self, regex, words) -> int:
        return len(re.findall(regex, words))
