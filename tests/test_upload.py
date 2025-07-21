import io
from unittest.mock import patch

def load_hec_pdf():
    """加载 HEC.pdf 作为测试用 PDF"""
    with open("tests/resources/HEC.pdf", "rb") as f:
        return io.BytesIO(f.read())

def test_upload_hec_pdf_success(client, db):
    """测试上传 HEC.pdf 成功返回并存入数据库"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.build_faiss_index') as mock_index, \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata') as mock_meta, \
         patch('routes.upload.extract_reference_texts') as mock_refs:

        mock_index.return_value = None
        mock_meta.return_value = {
            'title': 'HEC 2024 Paper',
            'author': 'Jane Doe',
            'keywords': 'HEC, AI',
            'abstract': 'A test paper from HEC conference.'
        }
        mock_refs.return_value = ['[1] Reference One', '[2] Reference Two']

        response = client.post('/api/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert response.json['msg'] in ['上传成功', '论文已存在，未重复上传']
        assert response.json['keyword'] == 'HEC, AI'
        assert isinstance(response.json['references'], list)
        assert 'abstract' in response.json

def test_upload_invalid_file_type(client):
    """上传一个非 PDF 文件应报错"""
    fake_file = io.BytesIO(b'This is not a pdf.')
    data = {
        'file': (fake_file, 'fake.txt')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert '只支持 PDF 文件' in response.json['error']

def test_upload_duplicate_pdf(client, db):
    """第二次上传同一份 PDF，应提示已存在"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.build_faiss_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata') as mock_meta, \
         patch('routes.upload.extract_reference_texts'):

        mock_meta.return_value = {
            'title': 'HEC 2024 Paper',
            'author': 'Jane Doe',
            'keywords': 'HEC, AI',
        }

        # 第一次上传
        client.post('/api/upload', data=data, content_type='multipart/form-data')

        # 第二次上传，应该走“已存在”逻辑
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.json['msg'] == '论文已存在，未重复上传'

def test_upload_metadata_error_handling(client, db):
    """模拟 extract_metadata 抛出异常，仍应成功返回"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.build_faiss_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata', side_effect=Exception("模拟失败")), \
         patch('routes.upload.extract_reference_texts', return_value=[]):

        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert 'msg' in response.json

def test_upload_reference_extraction_failure(client, db):
    """模拟 extract_reference_texts 抛异常"""
    data = {
        'file': (load_hec_pdf(), 'HEC.pdf')
    }

    with patch('routes.upload.build_faiss_index'), \
         patch('routes.upload.save_context'), \
         patch('routes.upload.extract_metadata', return_value={
             'title': 'Another Paper',
             'author': 'John Doe',
             'keywords': '',
         }), \
         patch('routes.upload.extract_reference_texts', side_effect=Exception("模拟失败")):

        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert 'references' in response.json
        assert response.json['references'] == []  # 应该返回空列表
