# app.py
from flask import Flask, render_template, request, jsonify
from solver import Wordle_Solver
from util import load_word_lists
import random
import secrets
from collections import Counter

app = Flask(__name__)

# Load word lists once
answers, all_words = load_word_lists()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def solve():
    target = request.json.get("target", "").strip().lower()

    if len(target) != 5:
        return jsonify({"error": "Word must be exactly 5 letters."}), 400
    if target not in all_words:
        return jsonify({"error": "Invalid word (not in dictionary)."}), 400

    solver = Wordle_Solver(all_words)
    guesses = []
    max_attempts = 6

    for attempt in range(max_attempts):
        guess = solver.next_guess()
        if guess is None:
            break

        feedback = generate_feedback(guess, target)
        guesses.append({"word": guess, "feedback": feedback})

        if feedback == "ggggg":
            break

        solver.update_constraints(guess, feedback)
        solver.filter_candidates()

    solved = (guesses[-1]["feedback"] == "ggggg") if guesses else False

    return jsonify({
        "guesses": guesses,
        "num_guesses": len(guesses),
        "solved": solved
    })

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.json
    num_trials = int(data.get("trials", 1000))
    max_attempts = 6
    guess_distribution = Counter()

    # Different RNG per request
    rng = random.Random(secrets.randbits(64))

    for _ in range(num_trials):
        target = rng.choice(answers)

        if _ < 3:  # print a few
            print("[simulate] sample target:", target)
            
        solver = Wordle_Solver(all_words)
        solved = False

        for attempt in range(1, max_attempts + 1):
            guess = solver.next_guess()
            if guess is None:
                break

            feedback = generate_feedback_list(guess, target)
            if feedback == ['g'] * 5:
                guess_distribution[str(attempt)] += 1
                solved = True
                break

            solver.update_constraints(guess, "".join(feedback))
            solver.filter_candidates()

        if not solved:
            guess_distribution["fail"] += 1

    return jsonify(guess_distribution)

def generate_feedback(guess, target):
    feedback = ["-"] * 5
    used = [False] * 5
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = "g"
            used[i] = True
    for i in range(5):
        if feedback[i] == "g":
            continue
        for j in range(5):
            if not used[j] and guess[i] == target[j]:
                feedback[i] = "y"
                used[j] = True
                break
    return "".join(feedback)

def generate_feedback_list(guess, target):
    feedback = ["-"] * 5
    used = [False] * 5
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = "g"
            used[i] = True
    for i in range(5):
        if feedback[i] == "g":
            continue
        for j in range(5):
            if not used[j] and guess[i] == target[j]:
                feedback[i] = "y"
                used[j] = True
                break
    return feedback

if __name__ == "__main__":
    app.run(debug=True)
