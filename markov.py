import random
import json


class Speaker(object):

    def __init__(self, bigram_file, user):
        self.bigram_file = bigram_file
        self.user = user
        self.bigrams = {}
        self._load_bigrams()

    def probabilistic_sentence(self):
        s = []
        next_word = self._probabilistic_next_word('\n')
        while next_word != '\n':
            s.append(next_word)
            next_word = self._probabilistic_next_word(next_word)
        return ' '.join(s)

    def _probabilistic_next_word(self, word):
        options = self.bigrams[self.user][word]
        total = sum(options.values())
        n = random.randint(0, total)
        running_total = 0
        for word, odds in options.items():
            if n <= odds+running_total:
                return word
            else:
                running_total += odds
                pass

    def _load_bigrams(self):
        with open(self.bigram_file) as bigram_file:
            self.bigrams = json.load(bigram_file)
