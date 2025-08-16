def load_word_lists(answer_path="data/wordle-answers-alphabetical.txt", guess_path="data/wordle-allowed-guesses.txt"):
    with open(answer_path) as f:
        answers = f.read().splitlines()
    with open(guess_path) as f:
        guesses = f.read().splitlines()
    
    # Combine both lists to get all valid guesses
    all_words = sorted(set(guesses + answers))

    return answers, all_words