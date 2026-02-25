from flask import Flask, request, Response, render_template_string
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

assistant_name = "RIKA"
owner_name = "Naveen"
memory_file = "memory.json"

GROQ_API_KEY = os.getenv("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")

# ================= MEMORY =================
def load_memory():
    if not os.path.exists(memory_file):
        return []
    with open(memory_file, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(memory_file, "w") as f:
        json.dump(data, f)

def update_memory(user, reply):
    memory = load_memory()
    memory.append({"user": user, "assistant": reply})
    memory = memory[-10:]
    save_memory(memory)

# ================= AI RESPONSE =================
def generate_response(user_input):

    memory = load_memory()

    messages = [{
        "role": "system",
        "content": f"You are {assistant_name}, a smart young female AI assistant. \
        Keep replies short (max 2 lines), witty and modern. \
        Built by {owner_name}."
    }]

    for m in memory:
        messages.append({"role": "user", "content": m["user"]})
        messages.append({"role": "assistant", "content": m["assistant"]})

    messages.append({"role": "user", "content": user_input})

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.6,
        "stream": True
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    full_reply = ""

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data:"):
                decoded = decoded.replace("data: ", "")
                if decoded == "[DONE]":
                    break
                chunk = json.loads(decoded)
                content = chunk["choices"][0]["delta"].get("content", "")
                full_reply += content
                yield content

    update_memory(user_input, full_reply)

# ================= WEB UI =================
@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>RIKA PUBLIC</title>
<style>
body { background:#111; color:white; text-align:center; padding-top:40px; font-family:Arial;}
input { width:60%; padding:10px;}
button { padding:10px;}
#response { width:60%; margin:auto; margin-top:20px; text-align:left;}
</style>
</head>
<body>

<h2>🌍 RIKA - Public AI</h2>

<input id="text" placeholder="Talk or type...">
<button onclick="send()">Send</button>

<div id="response"></div>

<script>

function send(){
    let text = document.getElementById("text").value;
    document.getElementById("response").innerHTML = "";

    fetch("/chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:text})
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        function read(){
            reader.read().then(({done, value})=>{
                if(done){
                    speak(fullText);
                    return;
                }
                let chunk = decoder.decode(value);
                fullText += chunk;
                document.getElementById("response").innerHTML += chunk;
                read();
            });
        }
        read();
    });
}

// 🎤 Browser Voice (Young Female)
function speak(text){
    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 1.05;
    speech.pitch = 1.3;
    speech.lang = "en-US";

    const voices = speechSynthesis.getVoices();
    const femaleVoice = voices.find(v => v.name.toLowerCase().includes("female") || v.name.toLowerCase().includes("zira"));
    if(femaleVoice){
        speech.voice = femaleVoice;
    }

    speechSynthesis.speak(speech);
}

</script>

</body>
</html>
""")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    return Response(generate_response(user_input), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)