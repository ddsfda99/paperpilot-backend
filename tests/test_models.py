import os
import pytest
from datetime import datetime
from models import User, Paper, Note, extract_keywords, extract_paper_metadata

# ✅ 测试 Paper 模型的 to_dict 方法
def test_paper_to_dict():
    paper = Paper(
        id=1,
        title="Test Paper",
        author="Tester",
        tags="AI,NLP",
        file_path="/path/to/file.pdf"
    )
    data = paper.to_dict()
    assert data["id"] == 1
    assert data["title"] == "Test Paper"
    assert data["author"] == "Tester"
    assert data["tags"] == ["AI", "NLP"]
    assert data["file_path"] == "/path/to/file.pdf"

# ✅ 测试 Note 模型的 to_dict 方法
def test_note_to_dict():
    note = Note(
        id=1,
        title="My Note",
        content="This is a test note",
        created_at=datetime(2024, 1, 1)
    )
    data = note.to_dict()
    assert data["id"] == 1
    assert data["title"] == "My Note"
    assert data["content"] == "This is a test note"
    assert data["created_at"].startswith("2024-01-01")

# ✅ 测试 User 模型的密码加密与验证
def test_user_password_check():
    user = User(username="tester")
    user.set_password("secure123")
    assert user.check_password("secure123") is True
    assert user.check_password("wrongpassword") is False

# ✅ 测试关键词提取函数
def test_extract_keywords():
    text = "Deep learning improves natural language processing and computer vision tasks."
    keywords = extract_keywords(text, topk=3)
    assert isinstance(keywords, list)
    assert len(keywords) == 3
    for word in keywords:
        assert isinstance(word, str)

# ✅ 测试元数据提取主函数（只验证是否报错、字段存在）
def test_extract_paper_metadata(tmp_path):
    import fitz 
    # 用 PyMuPDF 创建一个合法 PDF
    test_pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test Title\nTest Author")
    doc.save(str(test_pdf_path))
    doc.close()

    result = extract_paper_metadata(str(test_pdf_path))
    assert isinstance(result, dict)
    assert "title" in result
    assert "author" in result
    assert "tags" in result
