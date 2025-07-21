from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_context(file_id: str, question: str, top_k: int = 5, index_dir: str = "indices") -> list:
    print(f"📥 [retrieve_context] 正在处理 file_id={file_id}, question={question}")

    index_path = os.path.join(index_dir, f"{file_id}.index")
    text_path = os.path.join(index_dir, f"{file_id}.txt")

    # 检查路径是否存在
    if not os.path.exists(index_path):
        print(f"❌ 索引文件不存在: {index_path}")
        raise FileNotFoundError(f"索引文件不存在：{index_path}")
    if not os.path.exists(text_path):
        print(f"❌ 文本文件不存在: {text_path}")
        raise FileNotFoundError(f"文本文件不存在：{text_path}")

    # 加载数据
    index = faiss.read_index(index_path)
    with open(text_path, 'r', encoding='utf-8') as f:
        chunks = f.read().split("%%%\n")
    print(f"📄 段落数量: {len(chunks)}")

    # 生成查询向量
    try:
        q_vec = model.encode([question], convert_to_numpy=True)
    except Exception as e:
        print(f"❌ 问题 embedding 失败: {e}")
        raise

    # FAISS 搜索
    try:
        distances, indices = index.search(q_vec, top_k)
        print(f"🔍 FAISS 搜索完成，返回索引: {indices}")
    except Exception as e:
        print(f"❌ FAISS 查询失败: {e}")
        raise

    # 取出段落
    result = [chunks[i] for i in indices[0] if i < len(chunks)]
    print(f"✅ 返回段落数: {len(result)}")
    return result
