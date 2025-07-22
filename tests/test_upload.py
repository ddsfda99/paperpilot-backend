import io
import os
from unittest.mock import patch
from werkzeug.datastructures import FileStorage


def load_hec_pdf():
    """加载测试用 HEC.pdf 为 BytesIO"""
    with open("tests/resources/HEC.pdf", "rb") as f:
        return io.BytesIO(f.read())


def test_upload_pdf_success(client, db):
    """测试上传 HEC.pdf 成功返回"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.async_build_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata') as mock_meta:

        mock_meta.return_value = {
            'title': 'HEC Test Paper',
            'author': 'John Doe',
            'keywords': 'AI, HEC',
            'abstract': 'This paper explores...'
        }

        res = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        json = res.get_json()
        assert json['msg'] in ['上传成功', '论文已存在，未重复上传']
        assert 'url' in json
        assert 'file_id' in json
        assert 'keyword' in json


def test_upload_duplicate(client, db):
    """第二次上传同一份 PDF，应提示已存在"""

    with patch('routes.upload.async_build_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata') as mock_meta:

        mock_meta.return_value = {
            'title': 'HEC Test Paper',
            'author': 'John Doe',
            'keywords': 'AI, HEC',
            'abstract': 'This paper explores...'
        }

        # 第一次上传（新打开文件）
        data1 = {'file': (load_hec_pdf(), 'HEC.pdf')}
        client.post('/api/upload', data=data1, content_type='multipart/form-data')

        # 第二次上传（重新打开文件）
        data2 = {'file': (load_hec_pdf(), 'HEC.pdf')}
        res = client.post('/api/upload', data=data2, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.get_json()['msg'] == '论文已存在，未重复上传'



def test_upload_invalid_file(client):
    """上传非 PDF 文件应返回 400"""
    fake = io.BytesIO(b"not a real pdf")
    data = {
        'file': (fake, 'not_pdf.txt')
    }
    res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 400
    assert '只支持 PDF 文件' in res.get_json()['error']


def test_metadata_failure_handled(client, db):
    """模拟 extract_metadata 抛异常，接口应正常返回默认元数据"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.async_build_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata', side_effect=Exception("Metadata failed")):

        res = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        json = res.get_json()
        assert json['keyword'] == ''
        assert json['abstract'] == ''
