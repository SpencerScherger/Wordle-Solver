from flask import Flask, render_template, request, jsonify
from solver import Wordle_Solver
from util import load_word_lists
import time

app = Flask(__name__)

# Load word lists once
answers, all_words = load_word_lists()

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/solve", methods=["POST"])
def solve():
    target = request.json.get("target").strip().lower()
    if len(target) != 5:
        return jsonify({"error": "Word must be exactly 5 letters."}), 400
    if target not in all_words:
        return jsonify({"error": "Invalid word"}), 400

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

    return jsonify({
        "guesses": guesses,
        "num_guesses": len(guesses)
    })

def generate_feedback(guess, target):
    feedback = ["-"] * 5
    used = [False] * 5

    # First pass: greens
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = "g"
            used[i] = True

    # Second pass: yellows
    for i in range(5):
        if feedback[i] == "g":
            continue
        for j in range(5):
            if not used[j] and guess[i] == target[j]:
                feedback[i] = "y"
                used[j] = True
                break

    return "".join(feedback)

if __name__ == "__main__":
    app.run(debug=True)
