from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

API_KEY = "e849844fb96e4c0fa3a425960071a9d4.M2iGwvV3XMvV636i"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# ====================
# PDF 问答
# ====================
@app.route('/ask', methods=['POST'])
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

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        answer = response.json()['choices'][0]['message']['content']
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": response.text}), 500

# ====================
# 上传 PDF
# ====================
@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': '只支持 PDF 文件'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    print("✅ 上传成功：", file_path)
    return jsonify({'url': f'http://localhost:5000/static/uploads/{filename}'})

# ====================
# 解释选中英文内容
# ====================
@app.route('/api/explain', methods=['POST'])
def explain_text():
    data = request.get_json()
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

# ====================
# 文献管理：返回上传的 PDF 列表
# ====================
@app.route('/api/papers', methods=['GET'])
def list_uploaded_papers():
    pdf_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.pdf'):
            pdf_files.append({
                "id": filename,
                "title": filename.replace('.pdf', ''),
                "author": "未知",
                "tags": [],
                "cover": f"https://picsum.photos/seed/{filename}/200/120",
                "folder": "ai",
                "url": f"http://localhost:5000/static/uploads/{filename}"
            })
    return jsonify(pdf_files)

# ====================
# 启动服务
# ====================
if __name__ == '__main__':
    app.run(port=5000, debug=True)
