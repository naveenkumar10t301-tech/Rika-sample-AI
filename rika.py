from flask import Flask, render_template, request, jsonify
import datetime
import ollama

app = Flask(__name__)

assistant_name = "RIKA"
user_name = "Naveen"

# Memory storage
conversation_memory = []

SYSTEM_PROMPT = f"""
You are {assistant_name}, a smart young female AI assistant.
You respond in short, clear, quick replies.
You are slightly playful and confident.
You speak naturally and modern.
Keep answers under 3 sentences.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    conversation_memory.append({"role": "user", "content": user_message})

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_memory
            ]
        )

        reply = response["message"]["content"]

        conversation_memory.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except:
        return jsonify({"reply": "Oops. Brain glitch. Try again 😅"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)