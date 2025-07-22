from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer

db = SQLAlchemy()

# -------------------------- 数据模型 --------------------------

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Paper(db.Model):
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "tags": self.tags.split(',') if self.tags else [],
            "file_path": self.file_path
        }
        
class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, default='')
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

# -------------------------- 元数据提取（纯 Python 实现） --------------------------

# 1. 提取标题和作者（基于字体大小）
def extract_title_author_by_font(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]

    font_blocks = []
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                size = span["size"]
                if text:
                    font_blocks.append((size, text))

    # 按字体大小排序（降序），过滤过短文本
    font_blocks.sort(key=lambda x: -x[0])
    font_blocks = [fb for fb in font_blocks if len(fb[1]) > 5]

    title = font_blocks[0][1] if font_blocks else "Untitled"
    author = font_blocks[1][1] if len(font_blocks) > 1 else "Unknown Author"

    return title, author

# 2. 提取关键词（TF-IDF）
def extract_keywords(text, topk=5):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=topk)
    X = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out().tolist()

# 3. 综合封装接口
def extract_paper_metadata(pdf_path):
    title, author = extract_title_author_by_font(pdf_path)

    with fitz.open(pdf_path) as doc:
        full_text = ''
        for page in doc[:5]:  # 提取前5页内容用于关键词分析
            full_text += page.get_text()

    keywords = extract_keywords(full_text)

    return {
        'title': title,
        'author': author,
        'tags': ','.join(keywords),
    }
