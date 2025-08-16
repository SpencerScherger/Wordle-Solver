# simulation.py
import random
from solver import Wordle_Solver
from util import load_word_lists
from collections import Counter
import csv

# Configuration
NUM_TRIALS = 1000
MAX_ATTEMPTS = 6
OUTPUT_PATH = "results/simulation_stats.csv"

# Load word lists
answers, all_words = load_word_lists()

# Statistics tracker
guess_distribution = Counter()  # keys: 1-6 or 'fail'

# Ensure results/ folder exists
import os
os.makedirs("results", exist_ok=True)

# Simulation loop
for trial in range(1, NUM_TRIALS + 1):
    target = random.choice(answers)
    solver = Wordle_Solver(all_words)
    solved = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        guess = solver.next_guess()
        if guess is None:
            break

        # Generate feedback like Wordle
        feedback = ["-"] * 5
        used = [False] * 5

        # First pass: greens
        for i in range(5):
            if guess[i] == target[i]:
                feedback[i] = "g"
                used[i] = True

        # Second pass: yellows
        for i in range(5):
            if feedback[i] == 'g':
                continue
            for j in range(5):
                if not used[j] and guess[i] == target[j]:
                    feedback[i] = 'y'
                    used[j] = True
                    break

        if feedback == ['g'] * 5:
            guess_distribution[attempt] += 1
            solved = True
            break

        solver.update_constraints(guess, "".join(feedback))
        solver.filter_candidates()

    if not solved:
        guess_distribution['fail'] += 1

# Print summary
print("Simulation complete.")
print("\nGuess distribution:")
for i in range(1, 7):
    print(f"{i} guess{'es' if i > 1 else ''}: {guess_distribution[i]}")
print(f"Failed: {guess_distribution['fail']}")

# Export CSV
with open(OUTPUT_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Guesses", "Count"])
    for i in range(1, 7):
        writer.writerow([i, guess_distribution[i]])
    writer.writerow(["fail", guess_distribution['fail']])

print(f"\nResults saved to {OUTPUT_PATH}")
