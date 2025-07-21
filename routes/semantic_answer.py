from flask import Blueprint, request, jsonify
import requests
from config import API_URL, API_KEY
from utils.retrieval import retrieve_context 

semantic_answer_bp = Blueprint('semantic_answer', __name__)

@semantic_answer_bp.route('/api/semantic_answer', methods=['POST'])
def semantic_answer():
    data = request.get_json()
    file_id = data.get("file_id")
    question = data.get("question")
    print("file_id:", file_id)
    print("question:", question)
    try:
        chunks = retrieve_context(file_id, question, top_k=5)
        print("召回段落：", chunks)
        if not chunks:
            return jsonify({"error": "未找到相关段落"}), 400
        context = "\n\n".join(chunks)
    except Exception as e:
        return jsonify({"error": f"无法从向量索引中检索上下文：{str(e)}"}), 500

    payload = {
        "model": "glm-4-flash-250414",
        "messages": [
            {"role": "system", "content": "你是一个论文分析助手，请根据提供的论文段落回答用户的问题。"},
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
        return jsonify({"error": f"大模型调用失败：{str(e)}"}), 500
