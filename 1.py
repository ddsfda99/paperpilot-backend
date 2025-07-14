# clear_papers.py

from models import db, Paper
from app import create_app  # 确保 app 正确引入（你的 Flask 实例）
app = create_app()
with app.app_context():
    print("🗑️ 正在删除所有论文记录...")
    num_deleted = Paper.query.delete()
    db.session.commit()
    print(f"✅ 已删除 {num_deleted} 条论文记录")
