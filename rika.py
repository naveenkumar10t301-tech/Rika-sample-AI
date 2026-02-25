from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

assistant_name = "RIKA"
user_name = "Naveen"

# Use environment variable for security
client = Groq(api_key=os.environ.get("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"))

conversation_memory = []

SYSTEM_PROMPT = f"""
You are {assistant_name}, a smart young female AI assistant.
You respond in short, clear, fast replies.
Be confident, slightly playful, and modern.
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
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_memory
            ]
        )

        reply = completion.choices[0].message.content

        conversation_memory.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": "Hmm... my brain lagged 😅 Try again."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
