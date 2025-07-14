from flask import Blueprint, jsonify, request
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

    # 删除PDF文件和封面图
    if paper.file_path and os.path.exists(paper.file_path):
        os.remove(paper.file_path)

    db.session.delete(paper)
    db.session.commit()
    return jsonify({'message': f'已删除文献 {paper.title}'})

