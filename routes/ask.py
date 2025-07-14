# ask.py
from flask import Blueprint, request, jsonify
import requests
from config import API_KEY, API_URL

ask_bp = Blueprint('ask', __name__)

@ask_bp.route('/ask', methods=['POST'])
def ask_ai():
    data = request.json
    user_question = data.get('question')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4-flash-250414",
        "messages": [
            {"role": "system", "content": "你是一个PDF论文问答助手，请用简洁明了的中文回答用户问题"},
            {"role": "user", "content": user_question}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        answer = response.json()['choices'][0]['message']['content']
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
