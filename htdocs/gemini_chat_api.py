import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment.")

genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, concise health assistant. Provide friendly, short answers. "
    "Always suggest seeing a medical professional for serious issues."
)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME})

@app.route("/api/gemini-chat", methods=["POST"])
def gemini_chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    system_prompt = data.get("system", DEFAULT_SYSTEM_PROMPT)

    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "messages array required"}), 400

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        # Convert OpenAI-style messages to Gemini parts
        parts = []
        if system_prompt:
            parts.append({"role": "system", "content": system_prompt})
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append({"role": role, "content": content})

        resp = model.generate_content(parts)
        text = getattr(resp, "text", None) or (resp.candidates[0].content.parts[0].text if getattr(resp, "candidates", None) else "")

        return jsonify({
            "reply": text,
            "model": MODEL_NAME
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


