from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import jieba.analyse
import requests

app = Flask(__name__)
CORS(app)
API_KEY = ""
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
# 提取 PDF 文本
def extract_text_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 基于 TextRank 提取关键词
def extract_keywords(text, top_k=10):
    return jieba.analyse.textrank(text, topK=top_k)

# 构建简单的知识图谱数据结构
def build_knowledge_graph(keywords):
    nodes = [{"id": k, "label": k} for k in keywords]
    edges = []
    for i in range(len(keywords)):
        for j in range(i + 1, len(keywords)):
            edges.append({"from": keywords[i], "to": keywords[j], "label": ""})
    return {"nodes": nodes, "edges": edges}

@app.route('/api/graph', methods=['POST'])
def generate_graph():
    if 'file' not in request.files:
        print("没有接收到文件")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    print(f"收到文件: {file.filename}")

    try:
        text = extract_text_from_pdf(file)
        print(f"提取的文本前500字:\n{text[:500]}")

        keywords = extract_keywords(text)
        print(f"提取的关键词: {keywords}")

        graph = build_knowledge_graph(keywords)
        return jsonify(graph)

    except Exception as e:
        print(f"处理失败: {e}")
        return jsonify({"error": str(e)}), 500
    
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)
