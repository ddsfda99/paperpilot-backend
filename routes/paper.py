from flask import Blueprint, jsonify, request, send_file
from models import Paper, db
import os

paper_bp = Blueprint('paper', __name__)


# 获取所有文献列表
@paper_bp.route('/api/papers', methods=['GET'])
def get_all_papers():
    papers = Paper.query.order_by(Paper.created_at.desc()).all()
    return jsonify([p.to_dict() for p in papers])


# 删除指定文献
@paper_bp.route('/api/papers/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    # 删除PDF文件
    if paper.file_path and os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    db.session.delete(paper)
    db.session.commit()
    return jsonify({'message': f'已删除文献 {paper.title}'})

# 下载 PDF 文件
@paper_bp.route('/api/papers/<int:paper_id>/download', methods=['GET'])
def download_paper(paper_id):
    paper = Paper.query.get_or_404(paper_id)

    # 拼接绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 当前目录
    file_path = os.path.join(base_dir, '..', paper.file_path.lstrip('/'))  # 注意移除开头斜杠

    file_path = os.path.abspath(file_path)  # 处理完是绝对路径

    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )