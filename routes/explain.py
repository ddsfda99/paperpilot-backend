from flask import Blueprint, request, jsonify
import requests
from config import API_KEY, API_URL

explain_bp = Blueprint('explain', __name__)

@explain_bp.route('/api/explain', methods=['POST'])
def explain_text():
    data = request.get_json()
    print("🧪 收到 explain 请求:", data)
    user_text = data.get('text', '')

    if not user_text.strip():
        return jsonify({'error': 'No text provided'}), 400

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4-flash-250414",
        "messages": [
            {"role": "system", "content": "你是一个PDF论文知识点解释助手，请用中文简洁解释选中的英文内容"},
            {"role": "user", "content": f"请使用简洁易懂的中文解释以下英文内容，不要有多余内容：{user_text}"}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content']
        return jsonify({"explanation": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
