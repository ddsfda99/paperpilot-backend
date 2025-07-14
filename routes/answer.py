from flask import Blueprint, request, jsonify
import requests
from config import API_URL, API_KEY
from context_cache import get_context

answer_bp = Blueprint('answer', __name__)

@answer_bp.route('/api/answer', methods=['POST'])
def answer_question():
    data = request.get_json()
    file_id = data.get("file_id")
    question = data.get("question")

    context = get_context(file_id)
    if not context:
        return jsonify({"error": "上下文不存在，请先上传文档"}), 400

    payload = {
        "model": "glm-4-flash-250414",
        "messages": [
            {"role": "system", "content": "你是一个论文分析助手，请根据提供的论文上下文回答用户的问题。"},
            {"role": "user", "content": f"上下文内容：{context}\n\n请回答问题：{question}"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload)
        res.raise_for_status()
        reply = res.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
