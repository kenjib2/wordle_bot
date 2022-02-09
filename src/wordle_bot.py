import math


# ------------------- Weights -------------------
WT_LETTER_COUNT_PER_POSITION = 0.60
WT_LETTER_COUNT_TOTAL = 0.20
WT_FIRST_WORD_LETTER_REPEAT = 0.50
WT_WORD_COMMONALITY = 0.50
WORD_COMMONALITY_MAX_SET = 20
WORD_COMMONALITY_MAX_SCORE = 1226734006

# -----------------------------------------------

ALPHA = "abcdefghijklmnopqrstuvwxyz"


def init_letter_freq_dict(file_path):
    with open(file_path) as file:
        lines = file.readlines()

    letter_freqs = {}
    for next_letter in ALPHA:
        pos = [0, 0, 0, 0, 0]
        for i in range(0, 4):
            letter_freqs[next_letter] = pos

    for next_line in lines:
        for idx, next_letter in enumerate(next_line.strip().lower()):
            letter_freqs[next_letter][idx] += 1

    return letter_freqs


def init_word_commonality_dict(file_path, word_set):
    word_commonality = {}
    with open(file_path) as file:
        for next_line in file:
            (key, val) = next_line.split()
            if key in word_set:
                word_commonality[key] = int(val)

    return word_commonality


def compute_word_score(word, letter_freqs, word_commonality, word_number, words_remaining):
    score = 0
    used_letters = set()
    for idx, next_letter in enumerate(word):
        letter_score = letter_freqs[next_letter][idx] * WT_LETTER_COUNT_PER_POSITION\
                       + sum(letter_freqs[next_letter]) * WT_LETTER_COUNT_TOTAL
        if next_letter in used_letters and word_number == 1:
            letter_score *= WT_FIRST_WORD_LETTER_REPEAT
        score += letter_score
        used_letters.add(next_letter)

    if words_remaining < WORD_COMMONALITY_MAX_SET and word in word_commonality.keys():
        word_commonality_scaled = math.log(word_commonality[word]) / math.log(WORD_COMMONALITY_MAX_SCORE)
        commonality = (word_commonality_scaled * (WORD_COMMONALITY_MAX_SET - words_remaining) * WT_WORD_COMMONALITY) + 1
        score = score * commonality

    return score


def init_word_set(file_path):
    with open(file_path) as file:
        word_set = file.readlines()
    cleaned_word_set = [x.strip().lower() for x in word_set]
    return [word for word in cleaned_word_set if len(word) == 5]


def find_highest_scoring_word(letter_freqs, word_set, word_commonality, word_number, words_remaining):
    highest_score = 0
    highest_word = ""
    for next_word in word_set:
        score = compute_word_score(next_word, letter_freqs, word_commonality, word_number, words_remaining)
        if score > highest_score:
            highest_score = score
            highest_word = next_word
    return highest_word


# Number of times the letter appears in yellow and green clues combined
def num_clue_letters(letter, green_letters, yellow_letters):
    num_letters = 0
    for next_green_letter in green_letters:
        if next_green_letter[0] == letter:
            num_letters += 1
    for next_yellow_letter in yellow_letters:
        if next_yellow_letter[0] == letter:
            num_letters += 1
    return num_letters


# Number of times the letter appears in the word
def num_word_letters(word, letter):
    num_letters = 0
    for next_letter in word:
        if next_letter == letter:
            num_letters += 1
    return num_letters


def is_valid_word(word, green_letters, yellow_letters, gray_letters):
    for next_letter in word:
        word_letters = num_word_letters(word, next_letter)
        clue_letters = num_clue_letters(next_letter, green_letters, yellow_letters)
        if word_letters < clue_letters:
            return False

    for next_gray_letter in gray_letters:
        word_letters = num_word_letters(word, next_gray_letter[0])
        clue_letters = num_clue_letters(next_gray_letter[0], green_letters, yellow_letters)
        if word_letters > clue_letters:
            return False
        if word_letters < clue_letters:
            return False
        if next_gray_letter[0] == word[next_gray_letter[1]]:
            return False

    green_positions = []
    for next_green_letter in green_letters:
        green_positions.append(next_green_letter[1])
        if word[next_green_letter[1]] != next_green_letter[0]:
            return False

    # track which positions have already been "claimed" by a yellow
    yellow_positions = []
    for next_yellow_letter in yellow_letters:
        # Can't be in the same positions or it would be green
        if word[next_yellow_letter[1]] == next_yellow_letter[0]:
            return False

        letter_found = False
        for idx, next_letter in enumerate(word):
            if next_letter == next_yellow_letter[0] and idx not in yellow_positions and idx not in green_positions and not letter_found:
                yellow_positions.append(idx)
                letter_found = True

        if not letter_found:
            return False
    return True


def build_clue_sets(green_letters, yellow_letters, gray_letters, guessed_word, result):
    # We can clear green and yellow clues because we are paring down the word set every iteration. That means all
    # words we are checking already meet the criteria for previous clues, thus we don't need to worry about them
    # anymore. This only works because we are always guessing only valid words that match all clues (aka hard mode).
    # Do not clear grays, since those clues are still valid
    green_letters.clear()
    yellow_letters.clear()

    for idx, next_letter in enumerate(result):
        new_clue = (guessed_word[idx], idx)
        if next_letter == 'G':
            green_letters.add(new_clue)
        elif next_letter == 'g':
            gray_letters.add(new_clue)
        if next_letter == 'y':
            yellow_letters.add(new_clue)


def pare_word_set(word_set, green_letters, yellow_letters, gray_letters):
    pared_word_set = set()
    for next_word in word_set:
        if is_valid_word(next_word, green_letters, yellow_letters, gray_letters):
            pared_word_set.add(next_word)
    return pared_word_set


def main():
    green_letters = set()
    yellow_letters = set()
    gray_letters = set()

    word_set = init_word_set("Collins Scrabble Words (2019).txt")
    word_commonality = init_word_commonality_dict('count_1w.txt', word_set)
    letter_freqs = init_letter_freq_dict("Wordles.txt")

    num_guesses = 0

    best_word = find_highest_scoring_word(letter_freqs, word_set, word_commonality, num_guesses + 1, len(word_set))

    print("Best word choice: " + best_word)
    finished = False
    while not finished:
        result = input("Results of last guess: ")
        num_guesses += 1
        if len(result) != 5 or not set(result).issubset("Ggy"):
            print("Results must be five digits in the format Ggygg where g=gray, G=green, and y=yellow")
        elif result == "GGGGG":
            print("Winner is you!")
            finished = True
        elif num_guesses == 6:
            print("You have been defeated!")
            finished = True
        else:
            build_clue_sets(green_letters, yellow_letters, gray_letters, best_word, result)
            word_set = pare_word_set(word_set, green_letters, yellow_letters, gray_letters)
            best_word = find_highest_scoring_word(letter_freqs, word_set, word_commonality, num_guesses + 1, len(word_set))
            print("Number of possible words: " + str(len(word_set)))
            print("Best word choice: " + best_word)


if __name__ == "__main__":
    main()
