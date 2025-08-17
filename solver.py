from util import load_word_lists
import math
from collections import defaultdict, Counter

answers, all_words = load_word_lists()

class Wordle_Solver:
    #
    def __init__(self, all_words):
        '''
        Initialize the solver with all possible words (answers + full guess list)
        Reset constraints for a new solve

        :param all_words: List of all possible words

        :return: None
        '''        

        self.all_words = all_words
        self.reset()

    def reset(self):
        '''
        Reset constraints for a new solve
        The candidates are the current list of possible words after applying constraints

        :return: None
        '''

        self.candidates = self.all_words.copy()
        self.greens = [None] * 5                      
        self.yellows = [set() for _ in range(5)]      # banned letters per position

        # Per-letter constraints for handling duplicates
        self.min_counts = {}
        self.max_counts = {}

    def update_constraints(self, guess, feedback):
        '''
        Update constraints based on a guess and feedback
        Follows the rules of Wordle (hard mode)

        :param guess: The guessed word
        :param feedback: The feedback for the guess in a 5 character string using 'g', 'y' and '-'

        :return: None
        '''

        # Per-letter greens+yellows in this guess
        gy_count = Counter()
        for i, (gch, fb) in enumerate(zip(guess, feedback)):
            if fb == 'g':
                self.greens[i] = gch
                gy_count[gch] += 1
            elif fb == 'y':
                self.yellows[i].add(gch)
                gy_count[gch] += 1

        # Raise per-letter minimums based on this guess
        for ch, c in gy_count.items():
            if c > self.min_counts.get(ch, 0):
                self.min_counts[ch] = c

        # Lower per-letter maximums based on this guess
        seen_in_this_guess = set(gy_count.keys())
        for i, (gch, fb) in enumerate(zip(guess, feedback)):
            if fb == '-':
                if gch in seen_in_this_guess:
                    current_cap = self.max_counts.get(gch, 5)
                    self.max_counts[gch] = min(current_cap, gy_count[gch])
                else:
                    self.max_counts[gch] = 0

    def filter_candidates(self):
        '''
        Filter the candidates based on the current constraints
        O(nk) with n being the number of current candidates and k being the number of checks
        '''
        filtered = []
        for word in self.candidates:
            if self.is_valid(word):
                filtered.append(word)
        self.candidates = filtered

    def is_valid(self, word):
        '''
        Check if a word is valid based on the current constraints
        Handles cases where duplicates are involved through min/max system

        :param word: The word to check

        :return: True if the word is valid, False otherwise
        '''

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

    def generate_feedback(self, guess, target):
        '''
        Generate feedback for a guess based on the target word

        :param guess: The guessed word
        :param target: The target word

        :return: The feedback in a 5 character string using 'g', 'y' and '-'
        '''
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
        '''
        Generates the next guess based on the current constraints
        Uses entropy (expected information gain) to choose the best word:
            For all candidates, compute expected information gain for each possible feedback (target word)
            Pick the word with the highest expected information gain
        
        O(G*S) with G = # of guesses and S = # of candidates
        Technically O()

        S := the current number of candidates (hypothesis size)
        count := the number of words with the same feedback

        :return: The next guess
        '''
        if not self.candidates:
            return None

        if len(self.candidates) == 1:
            return self.candidates[0]
        
        # Start with "soare" on first guess to reduce entropy computation costs
        if len(self.candidates) == len(self.all_words):
            return "soare"

        best_word = None
        best_score = -1
        S = len(self.candidates)

        for guess in self.candidates:
            feedback_counts = defaultdict(int)
            for target in self.candidates:
                feedback = self.generate_feedback(guess, target)
                feedback_counts[feedback] += 1

            score = -sum(
                (count / S) * math.log2(count / S)
                for count in feedback_counts.values()
            )

            if (score > best_score) and (guess in self.candidates):
                best_score = score
                best_word = guess
            
        # print(f"[DEBUG] Next guess: {best_word}, Candidates left: {len(self.candidates)}")
        return best_word
