# arxiv_search.py
import requests
import xml.etree.ElementTree as ET
from flask import Blueprint, request, jsonify

def search_arxiv(query, max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch data from arXiv API")

    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    results = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
        summary = entry.find('atom:summary', ns).text.strip()
        link = entry.find('atom:id', ns).text.strip()

        results.append({
            'title': title,
            'authors': authors,
            'summary': summary,
            'link': link
        })

    return results
search_bp = Blueprint('arxiv', __name__)
@search_bp.route('/api/arxiv/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        results = search_arxiv(query, max_results=10)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500