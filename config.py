import os
from dotenv import load_dotenv

load_dotenv()
# ChatGLM 接口配置
API_KEY = os.getenv("GLM_API_KEY", "")
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 数据库配置：SQLite 文件路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'papers.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 上传文件保存目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
