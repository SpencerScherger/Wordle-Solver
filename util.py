def load_word_lists(answer_path="data/wordle-answers-alphabetical.txt", guess_path="data/wordle-allowed-guesses.txt"):
    '''
    Loads word lists from files

    :param answer_path: Path to the file containing the list of valid answers
    :param guess_path: Path to the file containing the list of valid guesses

    :return: A tuple containing the list of valid answers and the list of valid guesses
    '''
    with open(answer_path) as f:
        answers = f.read().splitlines()
    with open(guess_path) as f:
        guesses = f.read().splitlines()
    
    # Combine both lists to get all valid guesses
    all_words = sorted(set(guesses + answers))

    return answers, all_words