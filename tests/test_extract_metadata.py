from extract_metadata import extract_metadata
from unittest.mock import patch
import pytest
import os

def test_extract_metadata_success():
    """正常提取一份 PDF 元信息"""
    pdf_path = "tests/resources/HEC.pdf"
    assert os.path.exists(pdf_path), "确保 sample PDF 存在"
    result = extract_metadata(pdf_path)

    assert isinstance(result, dict)
    assert "title" in result
    assert "author" in result
    assert "keywords" in result
    assert "abstract" in result

def test_extract_metadata_file_not_found():
    """文件路径不存在，应抛出 FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        extract_metadata("tests/resources/nonexistent.pdf")

def test_extract_metadata_keybert_fail():
    """模拟 KeyBERT 提取关键词失败"""
    pdf_path = "tests/resources/HEC.pdf"

    with patch('extract_metadata.extract_keywords_with_keybert', side_effect=Exception("模拟失败")):
        result = extract_metadata(pdf_path)
        assert isinstance(result, dict)
        assert "keywords" in result
        assert result["keywords"] == ""  # 应 fallback 成空串
