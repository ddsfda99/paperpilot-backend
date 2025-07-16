from flask import Blueprint, request, jsonify
import requests
import logging

recommend_bp = Blueprint('recommend', __name__)
logging.basicConfig(level=logging.INFO)
@recommend_bp.route('/api/openalex/recommend', methods=['POST'])
def recommend_papers():
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    text = data.get('text', '').strip()

    query = keyword or text
    if not query:
        return jsonify({'error': '缺少关键词或摘要'}), 400
    print("🔍 实际搜索关键词:", query)
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": 6
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        print("📥 OpenAlex 返回内容：", res.text) 
        json_data = res.json()
        if not json_data or "results" not in json_data:
            raise ValueError("OpenAlex 返回数据异常，无 results 字段")

        results = json_data.get("results", [])

        papers = []
        for r in results:
            title = r.get("title", "无标题")
            authors = [a.get("author", {}).get("display_name", "未知作者") for a in r.get("authorships", [])]

            # 抽取摘要
            abstract_obj = r.get("abstract_inverted_index")
            abstract_text = ""
            if abstract_obj:
                word_map = {}
                for word, positions in abstract_obj.items():
                    for pos in positions:
                        word_map[pos] = word
                abstract_text = ' '.join([word_map[i] for i in sorted(word_map)])

            primary_location = r.get("primary_location")
            paper_link = primary_location.get("landing_page_url") if primary_location else None
            papers.append({
                "title": title,
                "authors": authors,
                "abstract": abstract_text,
                "link": paper_link,
                "similarity": "N/A"
            })

        return jsonify(papers)

    except Exception as e:
        logging.error(f"❌ OpenAlex 接口请求失败: {e}")
        return jsonify([]), 500
