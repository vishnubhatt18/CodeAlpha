import json
from pathlib import Path

import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



nltk.download("punkt")
nltk.download("punkt_tab")



base_dir = Path(__file__).resolve().parent
faq_path = base_dir / "faq.json"

if not faq_path.exists():
    raise FileNotFoundError(f"FAQ file not found: {faq_path}")

with open(faq_path, "r", encoding="utf-8") as file:
    data = json.load(file)


questions = [item["question"] for item in data]
answers = [item["answer"] for item in data]



def preprocess_text(text):
    words = word_tokenize(text.lower())

    cleaned_words = []

    for word in words:
        if word.isalnum():
            cleaned_words.append(word)

    return " ".join(cleaned_words)



processed_questions = []

for question in questions:
    processed_questions.append(preprocess_text(question))



vectorizer = TfidfVectorizer(stop_words="english")
question_vectors = vectorizer.fit_transform(processed_questions)



def get_response(user_input):
    processed_input = preprocess_text(user_input)

    user_vector = vectorizer.transform([processed_input])

    similarity = cosine_similarity(
        user_vector,
        question_vectors
    )

    best_match = similarity.argmax()

    confidence = similarity[0][best_match]


    if confidence > 0.25:
        return answers[best_match]
    else:
        return "Sorry, I couldn't understand your question. Please ask something related to the college."



if __name__ == "__main__":
    print("\n🎓 College FAQ Chatbot")
    print("Type 'exit' to quit\n")

    while True:
        user_question = input("You: ")

        if user_question.lower() == "exit":
            print("Bot: Thank you for visiting. Goodbye!")
            break

        response = get_response(user_question)

        print("Bot:", response)