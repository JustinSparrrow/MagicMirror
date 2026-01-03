# Magic Mirror Backend
这是一个基于 FastAPI 和 MediaPipe 构建的高性能 AI 图像处理引擎。它能够精准提取人脸关键部位（眼睛、眉毛、鼻子、嘴唇），并生成带透明通道的妆容素材，配合前端实现实时 AR 试妆效果。

## 🌟 核心工程特性
- 分层架构设计：采用类似 Java Spring Boot 的工程化结构（Controller-Service-Repository），实现逻辑高度解耦。
- 高性能并发控制：引入 ThreadPoolExecutor 隔离 CPU 密集型 AI 任务，确保异步 Web 服务不被图像识别算法阻塞。
- 内容寻址存储 (CAS)：基于 MD5 图像指纹 的缓存机制，避免同一图片重复计算，实现毫秒级二次响应。
- 准工业级安全性：使用 Bcrypt 盐值哈希存储密码，引入 JWT (JSON Web Token) 实现无状态身份鉴权。
- 生命周期管理：利用 FastAPI lifespan 实现 AI 模型的单例加载与资源释放。

## 🛠 技术栈
- 核心框架: FastAPI (Python 3.9+)
- AI 引擎: MediaPipe Tasks API (Face Landmarker)
- 数据库: SQLAlchemy + SQLite (可扩展支持 MySQL)
- 图像处理: OpenCV-Python
- 安全加密: Passlib + Bcrypt + Python-jose

## 🚀 环境搭建与快速启动
1. 克隆项目并进入目录
```bash
git clone <your-repo-url>
cd magic-mirror/backend
```

2. 创建虚拟环境 (推荐 Conda)
```bash
conda create -n magicmirror python=3.9
conda activate magicmirror
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 下载 AI 模型文件
由于模型文件较大，未包含在仓库中。请下载 face_landmarker.task 并放置在 backend/ 根目录下：
```bash
# 使用 curl 下载最新模型
curl -o face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

5. 配置环境变量
在 backend/ 目录下创建 .env 文件：
```lni
DATABASE_URL=sqlite:///./magic_mirror.db
JWT_SECRET_KEY=9a8b7c6d5e4f3g2h1i0j_magic_mirror_2026
ALGORITHM=HS256
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

6. 启动服务
```bash
python main.py
```

服务启动后，后端将运行在 http://127.0.0.1:8000。

## 📂 项目结构说明
```Text
backend/
├── app/
│   ├── api/          # 路由层 (Controller) - 处理请求分发
│   ├── crud/         # 数据持久层 (Repository) - 封装 DB 操作
│   ├── models/       # 实体类 (Entity) - 数据库表结构
│   ├── schemas/      # 数据传输对象 (DTO) - 输入输出校验
│   ├── services/     # 业务逻辑层 (Service) - AI 处理、JWT 逻辑
│   └── database.py   # 数据库连接池配置
├── static/           # 静态资源存放 (图片、缓存)
├── .env              # 环境变量配置
├── main.py           # 程序入口与生命周期管理
└── requirements.txt  # 依赖清单
```

## 📖 API 文档
启动后端后，访问以下路径查看完整的交互式 API 文档：

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 🧪 核心接口说明
|路径	|方法	|说明|
|------|-------|---|
|/api/v1/auth/register	|POST|	用户注册 (Bcrypt 加密)|
|/api/v1/auth/login	|POST|	用户登录 (换取 JWT Token)|
|/api/v1/makeup/extract	|POST	|核心接口：上传人脸并提取 6 部位妆容素材|
|/api/v1/makeup/my-styles/{user_id}	|GET	|获取用户保存的历史妆容列表|
|/api/v1/makeup/delete/{id}	|DELETE	|联动删除：物理删除磁盘图片并清理数据库|

## ⚠️ 开发者注意事项
1. CORS 配置：目前默认允许所有来源。在生产环境下，请在 main.py 中将 allow_origins 修改为前端真实域名。
2. 物理清理：本项目实现了引用计数清理逻辑。只有当数据库中没有任何记录引用某个 MD5 图片文件夹时，static/makeup_parts 下的物理文件才会被删除。

---
*Magic Mirror Project - 让美丽触手可及。*
