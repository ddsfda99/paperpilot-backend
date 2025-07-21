import fitz  # PyMuPDF
import faiss
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_paragraphs(pdf_path: str) -> list:
    doc = fitz.open(pdf_path)
    paragraphs = []
    for page in doc:
        blocks = page.get_text().split('\n')
        for line in blocks:
            line = line.strip()
            if len(line) > 20:  # 过滤短句
                paragraphs.append(line)
    return paragraphs

def build_faiss_index(file_id: str, pdf_path: str, index_dir='indices'):
    os.makedirs(index_dir, exist_ok=True)
    paras = extract_paragraphs(pdf_path)
    vectors = model.encode(paras, convert_to_numpy=True)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, os.path.join(index_dir, f"{file_id}.index"))

    with open(os.path.join(index_dir, f"{file_id}.txt"), 'w', encoding='utf-8') as f:
        for p in paras:
            f.write(p + '\n%%%\n')

    print(f"✅ 构建完成，共 {len(paras)} 段")
