from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import fitz
import logging

from models import Paper, db
from context_cache import save_context
from extract_metadata import extract_metadata  # ✅ 使用 PyMuPDF 提取器
from routes.extract_references import extract_reference_texts  # ✅ 自动提取参考文献

upload_bp = Blueprint('upload', __name__)
logging.basicConfig(level=logging.DEBUG)


# 提取 PDF 文本全文（用于缓存和元数据分析）
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text


@upload_bp.route('/api/upload', methods=['POST'])
def upload_pdf():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': '只支持 PDF 文件'}), 400

    # 保存 PDF 文件
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # 提取全文文本（用于上下文缓存）
    full_text = extract_text_from_pdf(file_path)
    save_context(filename, full_text)

    # ✅ 提取元数据
    metadata = extract_metadata(file_path)
    title = metadata.get('title', 'Untitled')
    author = metadata.get('author', 'Unknown')
    tags = metadata.get('keywords', '')
    logging.info(f"🧠 提取到关键词 tags: {tags}")

    abstract = metadata.get('abstract', '')

    # ✅ 提取参考文献
    try:
        references = extract_reference_texts(file_path)
        logging.info(f"📚 成功提取 {len(references)} 条参考文献")
    except Exception as e:
        logging.warning(f"❌ 提取参考文献失败: {e}")
        references = []

    # 检查是否已存在
    existing = Paper.query.filter_by(title=title, author=author).first()
    if existing:
        return jsonify({
            'msg': '论文已存在，未重复上传',
            'url': f'http://localhost:5000{existing.file_path}',
            'file_id': os.path.basename(existing.file_path),
            'references': references,
            'keyword': tags,
            'abstract': abstract
        }), 200
    # 存入数据库
    paper = Paper(
        title=title,
        author=author,
        tags=tags,
        file_path='/static/uploads/' + filename,
        # abstract=abstract,  # 可添加字段
    )
    db.session.add(paper)
    db.session.commit()

    return jsonify({
        'msg': '上传成功',
        'url': f'http://localhost:5000/static/uploads/{filename}',
        'file_id': filename,
        'references': references, 
        'keyword': tags,          
        'abstract': abstract      
    }), 200
