"""配置管理模块"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""

    # Anthropic LLM
    ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "http://192.168.186.114:8082")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "ultrasafe_test")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "GLM4.7-FP8")
    ANTHROPIC_SMALL_FAST_MODEL: str = os.getenv("ANTHROPIC_SMALL_FAST_MODEL", "GLM4.7-FP8")
    API_TIMEOUT_MS: int = int(os.getenv("API_TIMEOUT_MS", "600000"))

    # LangSmith
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "Intelligent-Chat-Assistant")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/chat.db")

    # App
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    def configure_langsmith(self):
        """配置 LangSmith 追踪环境变量"""
        os.environ["LANGCHAIN_TRACING_V2"] = self.LANGCHAIN_TRACING_V2
        if self.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = self.LANGCHAIN_API_KEY
        if self.LANGCHAIN_PROJECT:
            os.environ["LANGCHAIN_PROJECT"] = self.LANGCHAIN_PROJECT


settings = Settings()
settings.configure_langsmith()
