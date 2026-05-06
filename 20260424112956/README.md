# 智能运维助手 - LangChain + LangGraph + LangSmith

基于 **LangChain**、**LangGraph**、**LangSmith** 构建的智能运维对话助手，支持多轮对话、意图识别、FAQ 知识库检索、Skill 执行和对话历史持久化。

## 架构概览

```
┌──────────────────────────────────────────────────────┐
│                     FastAPI Backend                    │
│  ┌────────────────────────────────────────────────┐  │
│  │              LangGraph Agent Graph              │  │
│  │                                                  │  │
│  │  ┌──────────────┐    ┌───────────────────────┐  │  │
│  │  │ Intent       │───▶│ Route by Intent       │  │  │
│  │  │ Classifier   │    │ (add_user/delete_user │  │  │
│  │  └──────────────┘    │  /add_resource/...    │  │  │
│  │                       └──────┬───────┬───────┘  │  │
│  │                              │       │          │  │
│  │                    ┌─────────▼──┐ ┌──▼────────┐ │  │
│  │                    │ Skill      │ │ FAQ       │ │  │
│  │                    │ Execution  │ │ Retrieval │ │  │
│  │                    └──────┬─────┘ └─────┬─────┘ │  │
│  │                           │             │       │  │
│  │                    ┌──────▼─────────────▼──────┐│  │
│  │                    │     Response Generator     ││  │
│  │                    └───────────────────────────┘│  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Conversation  │  │ FAQ Vector   │  │ LangSmith   │ │
│  │ Store (SQLite)│  │ Store (FAISS)│  │ Tracing     │ │
│  └──────────────┘  └──────────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  Web UI  │
                    │ (HTML/JS)│
                    └─────────┘
```

## 核心功能

### 1. 多轮对话
- 基于 LangGraph 的状态图管理对话流程
- 支持上下文记忆，多轮追问
- 自动维护会话状态

### 2. 自动意图识别
支持识别以下意图：
| 意图 | 说明 |
|------|------|
| `add_user` | 添加用户 |
| `delete_user` | 删除用户 |
| `add_resource` | 添加资源 |
| `delete_resource` | 删除资源 |
| `sso` | 单点登录 |
| `faq` | FAQ 问答 |
| `general_chat` | 一般对话 |

### 3. FAQ 知识库检索
- 使用 FAISS 向量存储实现语义检索
- 内置 10 条运维 FAQ 数据
- 支持自定义扩展知识库

### 4. Skills 系统
- 可扩展的 Skill 插件架构
- 每个 Skill 对应一种意图
- 自动参数提取和缺失参数澄清
- 已注册 Skills：添加用户、删除用户、添加资源、删除资源、SSO

### 5. 对话历史持久化
- 基于 SQLAlchemy + SQLite 存储
- 支持多会话管理
- 可轻松切换到 PostgreSQL

### 6. LangSmith 追踪
- 全链路追踪：意图识别 → 检索 → Skill 执行 → 响应生成
- 可在 LangSmith 面板查看每次对话的详细执行过程
- 支持 Token 消耗统计和延迟分析

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

必须配置：
- `OPENAI_API_KEY` - OpenAI API 密钥
- `LANGCHAIN_API_KEY` - LangSmith API 密钥（可选，用于追踪）

### 3. 启动服务

```bash
python -m app.main
```

服务默认运行在 `http://localhost:8000`

### 4. 访问界面

打开浏览器访问 `http://localhost:8000`

## API 文档

启动后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送消息 |
| GET | `/api/history/{session_id}` | 获取对话历史 |
| DELETE | `/api/history/{session_id}` | 清除对话历史 |
| GET | `/api/sessions` | 列出所有会话 |
| POST | `/api/sessions/new` | 创建新会话 |
| GET | `/api/skills` | 列出所有 Skills |

### 请求示例

```bash
# 发送消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我添加一个用户zhangsan，邮箱是zhangsan@example.com", "session_id": "test01"}'

# 获取历史
curl http://localhost:8000/api/history/test01

# 查看 Skills
curl http://localhost:8000/api/skills
```

## 扩展 Skills

创建新的 Skill 只需 3 步：

### 1. 创建 Skill 文件

```python
# app/skills/my_skill.py
from app.skills.base import BaseSkill, SkillParameter, SkillResult

class MySkill(BaseSkill):
    name = "my_skill"
    description = "我的自定义 Skill"
    intent = "my_intent"  # 对应的意图
    parameters = [
        SkillParameter(name="param1", description="参数1", required=True),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        param1 = entities.get("param1", "")
        if not param1:
            return SkillResult(success=False, message="缺少参数")
        return SkillResult(success=True, message=f"执行成功：{param1}")
```

### 2. 注册 Skill

```python
# app/skills/__init__.py
from app.skills.my_skill import MySkill

def register_all_skills():
    registry.register(MySkill())
    # ...
```

### 3. 在意图识别中添加新意图

在 `app/graph/state.py` 的 `IntentType` 和 `INTENT_DESCRIPTIONS` 中添加对应条目。

## 项目结构

```
├── app/
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── graph/
│   │   ├── agent.py            # LangGraph 主图
│   │   ├── state.py            # 对话状态定义
│   │   ├── intent_classifier.py # 意图识别
│   │   └── nodes.py            # 处理节点
│   ├── skills/
│   │   ├── base.py             # Skill 基类
│   │   ├── registry.py         # Skill 注册表
│   │   ├── add_user.py         # 添加用户
│   │   ├── delete_user.py      # 删除用户
│   │   ├── add_resource.py     # 添加资源
│   │   ├── delete_resource.py  # 删除资源
│   │   └── sso.py              # 单点登录
│   ├── knowledge/
│   │   ├── faq_retriever.py    # FAQ 检索器
│   │   └── faq_data.json       # FAQ 数据
│   ├── memory/
│   │   └── conversation_store.py # 对话持久化
│   └── api/
│       ├── chat.py             # API 路由
│       └── schemas.py          # 数据模型
├── frontend/
│   ├── index.html              # 主页面
│   ├── style.css               # 样式
│   └── app.js                  # 前端逻辑
└── requirements.txt
```

## 技术栈

- **LangChain** - LLM 应用框架
- **LangGraph** - 状态图编排
- **LangSmith** - 可观测性与追踪
- **FastAPI** - Web 后端
- **FAISS** - 向量检索
- **SQLAlchemy** - 数据库 ORM
- **OpenAI GPT** - 大语言模型
