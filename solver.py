from util import load_word_lists
import math
from collections import defaultdict, Counter

answers, all_words = load_word_lists()

class Wordle_Solver:
    def __init__(self, all_words):
        self.all_words = all_words
        self.reset()

    def reset(self):
        # in reset()
        self.candidates = self.all_words.copy()
        self.greens = [None] * 5                      # fixed letters
        self.yellows = [set() for _ in range(5)]      # banned letters per position
        self.min_counts = {}                          # letter -> minimum count required
        self.max_counts = {}                          # letter -> maximum count allowed (when known)

        '''
        self.candidates = self.all_words.copy()
        self.greens = [None] * 5
        self.yellows = [set() for _ in range(5)]
        self.grays = set()
        '''

    def update_constraints(self, guess, feedback):
        # Per-letter greens+yellows in this guess
        gy_count = Counter()
        for i, (gch, fb) in enumerate(zip(guess, feedback)):
            if fb == 'g':
                self.greens[i] = gch
                gy_count[gch] += 1
            elif fb == 'y':
                self.yellows[i].add(gch)
                gy_count[gch] += 1
            # '-' handled below after we know gy_count

        # Raise per-letter minimums based on this guess
        for ch, c in gy_count.items():
            if c > self.min_counts.get(ch, 0):
                self.min_counts[ch] = c

        # Now handle '-' cells to set per-letter maximums correctly.
        # If a letter got '-' somewhere but also had G/Y elsewhere in THIS guess,
        # that means "no more than the gy_count occurrences".
        # If it only got '-' (no G/Y for that letter in this guess),
        # its max is 0 (absent).
        seen_in_this_guess = set(gy_count.keys())
        for i, (gch, fb) in enumerate(zip(guess, feedback)):
            if fb == '-':
                if gch in seen_in_this_guess:
                    # cap max to the gy_count we already saw
                    current_cap = self.max_counts.get(gch, 5)
                    self.max_counts[gch] = min(current_cap, gy_count[gch])
                else:
                    self.max_counts[gch] = 0
        '''
        for i in range(5):
            letter = guess[i]
            if feedback[i] == 'g':
                self.greens[i] = letter
            elif feedback[i] == 'y':
                self.yellows[i].add(letter)
            elif feedback[i] == '-':
                if letter not in self.greens and all(letter not in y for y in self.yellows):
                    self.grays.add(letter)
        #print(f"[DEBUG] Guess: {guess}, Feedback: {feedback}") #Debug
        '''


    def filter_candidates(self):
        filtered = []
        for word in self.candidates:
            if self.is_valid(word):
                filtered.append(word)
        self.candidates = filtered


    def is_valid(self, word):
        # greens
        for i, g in enumerate(self.greens):
            if g is not None and word[i] != g:
                return False

        # yellows (must not be here)
        for i, banned in enumerate(self.yellows):
            if word[i] in banned:
                return False

        # per-letter counts
        wc = Counter(word)
        # minimums
        for ch, m in self.min_counts.items():
            if wc[ch] < m:
                return False
        # maximums
        for ch, M in self.max_counts.items():
            if wc[ch] > M:
                return False

        return True
        '''
        # Check green constraints
        for i, g in enumerate(self.greens):
            if g is not None and word[i] != g:
                return False

        # Check yellow constraints
        for i, ys in enumerate(self.yellows):
            for y in ys:
                if y not in word or word[i] == y:
                    return False

        # Gray logic fix: only eliminate if letter not in green or yellow anywhere
        known_letters = set(filter(None, self.greens))
        for ys in self.yellows:
            known_letters.update(ys)

        for g in self.grays:
            if g in word and g not in known_letters:
                return False

        return True
        '''


    def generate_feedback(self, guess, target):
        feedback = ['-'] * 5
        used = [False] * 5

        for i in range(5):
            if guess[i] == target[i]:
                feedback[i] = 'g'
                used[i] = True

        for i in range(5):
            if feedback[i] == 'g':
                continue
            for j in range(5):
                if not used[j] and guess[i] == target[j]:
                    feedback[i] = 'y'
                    used[j] = True
                    break

        return ''.join(feedback)

    def next_guess(self):
        if not self.candidates:
            return None

        if len(self.candidates) == 1:
            return self.candidates[0]
        
        if len(self.candidates) == len(self.all_words):
            return "soare"

        best_word = None
        best_score = -1
        total = len(self.candidates)

        for guess in self.candidates:
            feedback_counts = defaultdict(int)
            for target in self.candidates:
                feedback = self.generate_feedback(guess, target)
                feedback_counts[feedback] += 1

            score = -sum(
                (count / total) * math.log2(count / total)
                for count in feedback_counts.values()
            )

            if (score > best_score) and (guess in self.candidates):
                best_score = score
                best_word = guess
            
        print(f"[DEBUG] Next guess: {best_word}, Candidates left: {len(self.candidates)}")
        return best_word
