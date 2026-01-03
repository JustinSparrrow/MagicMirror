import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

import uvicorn
from app.database import engine, Base
from app.api.v1 import auth, makeup
from app.services import ai_service

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 启动时 ---
    print("服务器正在启动...")
    # 1. 初始化数据库表
    Base.metadata.create_all(bind=engine)
    # 2. 初始化单例模型
    ai_service.init_detector()
    yield
    # --- 关闭时 ---
    print("服务器正在关闭...")

app = FastAPI(title="Magic Mirror Pro", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录详细日志
    print(f"全局拦截到异常: {exc}") 
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误，请稍后再试",
            "detail": str(exc) if True else "隐私信息已隐藏" # 生产环境建议隐藏 detail
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发阶段设为 *，上线后设为前端域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法 (GET, POST 等)
    allow_headers=["*"],  # 允许所有请求头
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(makeup.router, prefix="/api/v1")

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    uvicorn.run(app, host=host, port=port)

