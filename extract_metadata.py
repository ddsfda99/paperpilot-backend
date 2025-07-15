import fitz  # PyMuPDF
from pathlib import Path


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

    return {
        "title": title,
        "author": author,
        "keywords": keywords,
        "abstract": abstract
    }


# CLI entry
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("❌ 用法：python extract_metadata.py <PDF路径>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    try:
        metadata = extract_metadata(pdf_file)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 提取失败: {e}")
