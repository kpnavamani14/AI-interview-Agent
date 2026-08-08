import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai


load_dotenv()

app = Flask(__name__)

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)


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
        return jsonify({
            "question": "Interview completed!"
        })

    return jsonify({
        "question": questions[number]
    })


@app.route("/answer", methods=["POST"])
def answer():

    data = request.json

    user_answer = data.get("answer", "").strip()
    question_number = data.get("question_number", 0)

    if not user_answer:
        return jsonify({
            "result": "Please enter an answer."
        })

    try:

        question = questions[int(question_number)]

        prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Interview Question:
{question}

Candidate Answer:
{user_answer}

Evaluate the answer using these categories:

1. Technical Accuracy - score from 0 to 10
2. Relevance - score from 0 to 10
3. Communication - score from 0 to 10
4. Confidence - score from 0 to 10
5. Completeness - score from 0 to 10

Calculate an Overall Score from 0 to 10.

Return exactly this format:

Technical Accuracy: X/10
Relevance: X/10
Communication: X/10
Confidence: X/10
Completeness: X/10
Overall Score: X/10

Strengths:
- Strength 1
- Strength 2

Improvements:
- Improvement 1
- Improvement 2

Personalized Feedback:
Write short personalized feedback.
"""

        # Gemini AI request
        response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)
        result = response.text

        # Extract overall score
        overall_score = 0

        for line in result.splitlines():

            if "Overall Score:" in line:

                try:
                    score_text = line.split(":", 1)[1].strip()
                    score_text = score_text.replace("/10", "")
                    overall_score = float(score_text)

                except ValueError:
                    overall_score = 0

        scores.append(overall_score)

        return jsonify({
            "result": result
        })

    except Exception as e:

        print("Gemini Error:", repr(e))

        return jsonify({
            "result": (
                "AI evaluation failed.\n\n"
                "Please check the PowerShell terminal."
            )
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
