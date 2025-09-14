# time_tick_quiz.py

import requests
import html
import random
import threading
import time

CATEGORY_URL = "https://opentdb.com/api_category.php"
QUESTION_URL = "https://opentdb.com/api.php"
TIME_LIMIT = 15  # seconds per question

# ------------------ api functionss ------------------

def fetch_categories():
    """
    fetches trivia categories from the API.
    """
    res = requests.get(CATEGORY_URL)
    data = res.json()
    categories = data.get("trivia_categories", [])
    for c in categories:
        print(f"{c['id']}: {c['name']}")
    return categories

def fetch_questions(amount=10, category=None, difficulty=None, qtype=None):
    """
    fetches the questions based on given filters.
    """
    params = {
        "amount": amount,
        "category": category,
        "difficulty": difficulty,
        "type": qtype
    }
    res = requests.get(QUESTION_URL, params=params)
    data = res.json()
    return data.get("results", [])

# ------------------ user input selection ------------------

def select_category():
    """
    prompts user to select a category from the list.
    """
    cat = input("Enter Category ID: ")
    return cat

def select_difficulty():
    """
    prompts user to select question difficulty.
    """
    print("Select Difficulty:")
    print("1. Easy\n2. Medium\n3. Hard")
    diff_map = {"1": "easy", "2": "medium", "3": "hard"}
    choice = input("Enter choice (1/2/3): ")
    return diff_map.get(choice, "easy")

def select_question_type():
    """
    prompts the user to select type of questions (multiple/boolean).
    """
    print("Select Question Type:")
    print("1. Multiple Choice\n2. True / False")
    type_map = {"1": "multiple", "2": "boolean"}
    choice = input("Enter choice (1/2): ")
    return type_map.get(choice, "multiple")

# ------------------ quiz logicc ------------------

def ask_question(questions, typet):
    """
    presents a question to the user with a countdown timer.
    """
    score = 0

    for q in questions:
        end = threading.Event()

        print("\nQ:", html.unescape(q["question"]))

        options = q["incorrect_answers"] + [q["correct_answer"]]
        options = [html.unescape(opt) for opt in options]
        random.shuffle(options)
        print("Options:", options)

        def timer():
            if not end.wait(TIME_LIMIT):
                print("\n Time up!")
                print("Correct answer:", html.unescape(q["correct_answer"]))
                end.set()

        def user_input():
            ans = input("Your answer: ")
            if ans == q["correct_answer"]:
                print(" Correct")
                nonlocal score
                score += 1
            else:
                print(" Incorrect")
                print("Correct answer:", html.unescape(q["correct_answer"]))
            end.set()

        t = threading.Thread(target=user_input)
        o = threading.Thread(target=timer)
        t.start()
        o.start()
        t.join()
        o.join()

    print(f"\n Final Score: {score}/{len(questions)}")

def select_quiz_options(categories):
    """
    gathers all the quiz options and fetch questions accordingly.
    """
    cat = select_category()
    diff = select_difficulty()
    qtype = select_question_type()

    questions = fetch_questions(amount=5, category=cat, difficulty=diff, qtype=qtype)
    return questions, qtype

# ------------------ main fucntion ------------------

def main():
    """
    Entry point for the TimeTickQuiz game.
    """
    print("Welcome to TimeTickQuiz!")
    categories = fetch_categories()
    questions, qtype = select_quiz_options(categories)
    
    if questions:
        ask_question(questions, typet=qtype)
    else:
        print("No questions fetched. Exiting.")

if __name__ == "__main__":
    main()
