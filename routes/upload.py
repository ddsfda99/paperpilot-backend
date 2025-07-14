from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import fitz

from models import Paper, extract_paper_metadata, db
from context_cache import save_context

upload_bp = Blueprint('upload', __name__)

# 提取 PDF 文本全文（用于缓存上下文）
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

    # 提取全文文本，并缓存上下文
    full_text = extract_text_from_pdf(file_path)
    save_context(filename, full_text)  # ✅ 缓存时使用 filename 作为 key

    # 提取元数据
    metadata = extract_paper_metadata(file_path)
    title = metadata.get('title', 'Untitled')
    author = metadata.get('author', 'Unknown')
    tags = metadata.get('tags', '')

    # 检查是否已存在
    existing = Paper.query.filter_by(title=title, author=author).first()
    if existing:
        return jsonify({
            'msg': '论文已存在，未重复上传',
            'url': f'http://localhost:5000{existing.file_path}',
            'file_id': os.path.basename(existing.file_path)  # ✅ 返回 filename
        }), 200

    # 存入数据库
    paper = Paper(
        title=title,
        author=author,
        tags=tags,
        file_path='/static/uploads/' + filename,
    )
    db.session.add(paper)
    db.session.commit()

    return jsonify({
        'url': f'http://localhost:5000/static/uploads/{filename}',
        'file_id': filename  # ✅ 返回 filename
    }), 200
