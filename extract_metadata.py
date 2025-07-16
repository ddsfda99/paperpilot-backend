import fitz  # PyMuPDF
from pathlib import Path
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
kw_model = KeyBERT(SentenceTransformer('all-MiniLM-L6-v2'))

def extract_keywords_with_keybert(text: str, top_k=5) -> str:
    """使用 KeyBERT 从文本中提取关键词（轻量语义模型）"""
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        top_n=top_k
    )
    return ", ".join([kw[0] for kw in keywords])


def extract_metadata(pdf_path: str) -> dict:
    """Extract title, author, keywords, and abstract from a PDF file."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} not found.")

    doc = fitz.open(pdf_path)
    meta = doc.metadata or {}

    title = meta.get("title", "").strip()
    author = meta.get("author", "").strip()
    keywords = meta.get("keywords", "").strip()

    # Fallback from text spans: title and author
    spans = []
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                spans.append({
                    "text": span["text"].strip(),
                    "size": span["size"],
                    "bbox": span["bbox"]
                })
    spans = [s for s in spans if len(s["text"]) > 5]
    sorted_spans = sorted(spans, key=lambda x: -x["size"])

    if not title and sorted_spans:
        title = sorted_spans[0]["text"]
    if not author and len(sorted_spans) > 1:
        author = sorted_spans[1]["text"]

    # Try to extract abstract
    abstract = ""
    for page in doc:
        text = page.get_text("text")
        if "abstract" in text.lower():
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if "abstract" in line.lower():
                    abstract = "\n".join(lines[i:i + 6])
                    break
            if abstract:
                break

    # 如果 keywords 缺失，则用 KeyBERT 从 abstract 中提取
    if not keywords:
        try:
            keywords = extract_keywords_with_keybert(abstract)
        except Exception as e:
            print(f"⚠️ KeyBERT 提取关键词失败: {e}")
            keywords = ""
    print("keywords:", keywords)
    return {
        "title": title,
        "author": author,
        "keywords": keywords,
        "abstract": abstract
    }
