"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.chat import router as chat_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print(f"🚀 智能运维助手启动中...")
    print(f"📊 LangSmith 追踪: {settings.LANGCHAIN_PROJECT}")
    print(f"🤖 模型: {settings.ANTHROPIC_MODEL}")
    print(f"🔗 API: {settings.ANTHROPIC_BASE_URL}")
    yield
    print("👋 应用关闭")


app = FastAPI(
    title="智能运维助手",
    description="基于 LangChain + LangGraph 的智能对话助手，支持意图识别、FAQ检索、Skill执行",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(chat_router)

# 静态文件（前端）
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
