from bot.models.intent import Intent
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from typing import List

class Proposer:

    @staticmethod
    def determine_intent(input: str):

        if not validate(input):
            print("Proposer validation failed")

        lst = strip_stopwords(input)
        print(lst)


def validate(input: str) -> bool:
    return isinstance(input, str)

def strip_stopwords(input: str) -> List:
    stop_words = set(stopwords.words('english'))
    tok = word_tokenize(input)

    return [w for w in tok if w not in stop_words]
