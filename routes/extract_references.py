import os
import re
import fitz
import logging

from flask import Blueprint, request, jsonify, current_app

# Blueprint 注册
extract_bp = Blueprint('extract', __name__)
logging.basicConfig(level=logging.DEBUG)


def extract_reference_texts(pdf_path):
    """
    从 PDF 中提取参考文献文本（纯文本数组，不请求 OpenAlex）
    """
    logging.info(f"📄 正在从 PDF 提取参考文献: {pdf_path}")
    doc = fitz.open(pdf_path)
    references_text = ""
    found = False

    for i, page in enumerate(doc):
        text = page.get_text()
        if "references" in text.lower() or "参考文献" in text.lower():
            logging.info(f"✅ 第 {i+1} 页检测到参考文献标题")
            found = True
        if found:
            references_text += "\n" + text

    if not references_text:
        logging.warning("⚠️ 未找到参考文献区域")
        return []

    # 清理与合并
    references_text = references_text.replace('\r', '').strip()
    lines = references_text.splitlines()
    full_text = " ".join(lines)

    # 分割为条目：如 [1]、1.、1） 等等
    refs = re.split(r'\[\d+\]|\n\d+\.\s+|\n\d+\s+|\n\s*\d+\)|\n\s*\d+\．', full_text)
    refs = [r.strip() for r in refs if len(r.strip()) > 20]

    logging.info(f"📌 共提取 {len(refs)} 条参考文献")
    return refs


@extract_bp.route('/api/extract/references', methods=['GET'])
def extract_references():
    file_id = request.args.get('file_id')
    logging.info(f"📥 接收到参考文献提取请求: file_id = {file_id}")
    
    if not file_id:
        logging.error("❌ file_id 参数缺失")
        return jsonify({'error': '缺少 file_id 参数'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, file_id)

    if not os.path.exists(file_path):
        logging.error(f"❌ 文件不存在: {file_path}")
        return jsonify({'error': '文件不存在'}), 404

    try:
        references = extract_reference_texts(file_path)
        logging.info(f"✅ 成功提取 {len(references)} 条参考文献")
        return jsonify({'references': references})
    except Exception as e:
        logging.exception("🔥 提取参考文献出错:")
        return jsonify({'error': str(e)}), 500
