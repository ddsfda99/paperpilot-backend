import requests
from flask import Blueprint, request, jsonify
def search_openalex(keyword, page=1, per_page=10):
    url = "https://api.openalex.org/works"
    params = {
        "search": keyword,
        "page": page,
        "per-page": per_page,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("results", []):
        title = item.get("title", "")
        authors = [a["author"]["display_name"] for a in item.get("authorships", [])]
        abstract_raw = item.get("abstract_inverted_index", None)
        abstract = ""
        if abstract_raw:
            # 拼接摘要
            word_map = sorted([(v, k) for k, positions in abstract_raw.items() for v in positions])
            abstract = " ".join([w[1] for w in word_map])

        results.append({
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "link": item.get("id", "")
        })

    return results
openalex_bp = Blueprint('openalex', __name__)

@openalex_bp.route('/api/openalex/search', methods=['GET'])
def openalex_search():
    keyword = request.args.get("q")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    if not keyword:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        results = search_openalex(keyword, page=page, per_page=per_page)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
