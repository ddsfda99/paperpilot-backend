## PaperPilot · 后端服务（Flask）
PaperPilot是一个集论文阅读、AI 解读、笔记管理、文献推荐等多功能于一体的智能阅读平台。本仓库为后端部分，使用 Flask 框架开发，提供完整的 API 支持与上下文处理、向量检索等功能。

前端地址：[paperpilot-frontend](https://github.com/ddsfda99/paperpilot-frontend)

## 项目演示视频

👉 [点击观看演示视频（bilibili）](https://www.bilibili.com/video/BV1KdgHzDEzs/?vd_source=de633d4318be770bdffc3275f1e20c2c)

[![Watch the video](![alt text](image.png))](https://www.bilibili.com/video/BV1KdgHzDEzs/?vd_source=de633d4318be770bdffc3275f1e20c2c)

## 核心功能
* PDF 上传与预览：支持目录跳转与文字高亮
* 论文解读：自动生成论文摘要，并且提供十个经典科研问题和相应的自动AI解答
* AI问答：结合上下文语义，支持自由提问
* 相似论文推荐：基于摘要关键词调用 OpenAlex 实时推荐
* 自动导出笔记&笔记管理：自动生成摘要与问答笔记，便于整理与复习
* 文献管理：保存已上传文献，并使用标题、作者等元数据标记
* 文献检索：根据关键词搜索文献
* 用户系统：支持登录注册、权限控制、身份管理

## 技术栈

| 技术组件                | 用途                        |
| ------------------- | ------------------------- |
| Flask               | 主体后端框架                    |
| SQLAlchemy          | ORM 数据库操作                 |
| SQLite              | 存储用户、论文、笔记等数据             |
| PyMuPDF (fitz)      | PDF 内容提取                  |
| FAISS               | 段落级向量检索                   |
| requests            | 调用 ChatGLM 与 OpenAlex API |
| pytest + coverage   | 自动化测试与覆盖率分析               |

## 目录结构

```
paperpilot-backend/
├── app.py                     # 应用入口，注册蓝图与启动服务
├── config.py                  # 配置文件（API_KEY、数据库等）
├── context_cache.py           # 管理 file_id 与上下文缓存映射
├── extract_metadata.py        # 提取标题、作者、关键词等元信息
├── models.py                  # SQLAlchemy 数据模型定义
├── papers.db                  # 默认 SQLite 数据库文件
├── requirements.txt           # Python 项目依赖
├── README.md                  # 项目说明文档
│
├── routes/                    # 路由模块（各类接口）
│   ├── __init__.py
│   ├── answer.py              # 主问答接口（上下文+问题）
│   ├── auth.py                # 用户登录注册
│   ├── explain.py             # AI 解释接口（备用/废弃）
│   ├── note.py                # 结构化笔记相关接口
│   ├── openalex_recommend.py  # 相似论文推荐（OpenAlex）
│   ├── openalex_search.py     # 文献检索（OpenAlex关键词搜索）
│   ├── paper.py               # 论文元数据获取等接口
│   ├── semantic_answer.py     # 支持向量召回的问答接口
│   └── upload.py              # 文件上传与 PDF 内容提取
│
├── static/                    # 静态资源（如上传文件）
│
├── tests/                     # 自动化测试文件夹
│   └── test_models.py         # 数据模型与功能测试
│
├── utils/                     # 工具模块
│   ├── build_index.py         # 构建段落向量索引（FAISS）
│   └── retrieval.py           # 从索引中召回相关段落
```

## 配置说明
请编辑 `config.py` 文件：

```python
# ChatGLM API 配置
API_KEY = "你的智谱API密钥"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 数据库配置（默认使用 SQLite，可改 PostgreSQL）
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'papers.db')

# 上传路径
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
```

## 启动方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动开发服务

```bash
python app.py
```

默认运行在 `http://localhost:5000`

## 接口测试（Pytest）
测试所有接口
```bash
pytest --cov=models tests/ -v
```