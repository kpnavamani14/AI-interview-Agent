from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

questions = [
    "Tell me about yourself.",
    "What are your technical skills?",
    "Tell me about a project you have worked on.",
    "What was a difficult problem you faced in your project?",
    "Why should we hire you?"
]

scores = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/question/<int:number>")
def get_question(number):

    if number < 0 or number >= len(questions):
        return jsonify({"question": "Interview completed!"})

    return jsonify({
        "question": questions[number]
    })


@app.route("/answer", methods=["POST"])
def answer():

    data = request.json
    user_answer = data.get("answer", "").strip()

    if not user_answer:
        return jsonify({
            "result": "Please enter an answer."
        })

    word_count = len(user_answer.split())
    answer_lower = user_answer.lower()

    # Calculate score
    if word_count >= 50:
        score = 9
        feedback = "Excellent answer. It is detailed and well explained."
    elif word_count >= 30:
        score = 8
        feedback = "Good answer. Add a little more detail to make it stronger."
    elif word_count >= 15:
        score = 6
        feedback = "Your answer is okay, but try to explain your experience in more detail."
    else:
        score = 4
        feedback = "Your answer is too short. Give more details and examples."

    # Check technical keywords
    keywords = [
        "python",
        "java",
        "sql",
        "machine learning",
        "project",
        "team",
        "communication",
        "developer",
        "student"
    ]

    found = []

    for keyword in keywords:
        if keyword in answer_lower:
            found.append(keyword)

    if found:
        feedback += "\nRelevant topics: " + ", ".join(found)

    # Store score
    scores.append(score)

    result = f"""
Score: {score}/10

Feedback:
{feedback}
"""

    return jsonify({
        "result": result
    })


@app.route("/final-score")
def final_score():

    if not scores:
        return jsonify({
            "score": 0,
            "message": "No answers submitted."
        })

    average = sum(scores) / len(scores)

    return jsonify({
        "score": round(average, 1),
        "answered": len(scores),
        "total": len(questions)
    })


if __name__ == "__main__":
    app.run(debug=True)