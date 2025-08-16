from util import load_word_lists

answers, all_words = load_word_lists()

class Wordle_Solver:
    def __init__(self, all_words):
        self.all_words = all_words
        self.reset()
    
    def reset(self):
        self.candidates = self.all_words.copy()
        self.greens = [None] * 5
        self.yellows = [set() for _ in range(5)]
        self.grays = set()
    
    '''
    candidates : remaining valid words
    greens     : list of 5 letters or None for known correct positions
    yellows    : list of sets for letters that must appear but not at that index
    grays      : set of known incorrect letters (handle duplicate letters)
    '''
    def update_constraints(self, guess, feedback):
        for i in range(5):
            letter = guess[i]
            if feedback[i] == 'g':
                self.greens[i] == letter
            elif feedback[i] == 'y':
                self.yellows[i].add(letter)
            elif feedback[i] == '-':  # gray
                # Only add to grays if not in green or yellow positions
                if letter not in self.greens and all(letter not in y for y in self.yellows):
                    self.grays.add(letter)
        
    def filter_candidates(self):
        filtered = []
        for word in self.candidates:
            if not self.is_valid(word):
                continue
            filtered.append(word)
        self.candidates = filtered

    def is_valid(self, word):
        # Green check
        for i, g in enumerate(self.greens):
            if g is not None and word[i] != g:
                return False

        # Yellow check
        for i, ys in enumerate(self.yellows):
            for y in ys:
                if y not in word or word[i] == y:
                    return False

        # Gray check (naive version, refine later for repeated letters)
        for g in self.grays:
            if g in word:
                return False

        return True

    def score_words(self):
        from collections import Counter
        letter_counts = Counter("".join(self.candidates))

        def score(word):
            return sum(letter_counts[c] for c in set(word))

        return sorted(self.candidates, key=score, reverse=True)

    def next_guess(self):
        if not self.candidates:
            return None
        return self.score_words()[0]