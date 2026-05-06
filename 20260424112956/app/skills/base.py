"""Skill 基类定义"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillParameter:
    """Skill 参数定义"""
    name: str
    description: str
    required: bool = True
    type: str = "string"
    default: Any = None


@dataclass
class SkillResult:
    """Skill 执行结果"""
    success: bool
    message: str
    data: dict = field(default_factory=dict)


class BaseSkill(ABC):
    """Skill 基类

    所有自定义 Skill 必须继承此类并实现 execute 方法
    """

    # Skill 元信息（子类必须定义）
    name: str = ""
    description: str = ""
    intent: str = ""  # 对应的意图类型
    parameters: list[SkillParameter] = []

    @abstractmethod
    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        """执行 Skill

        Args:
            entities: 从用户消息中提取的实体
            **kwargs: 其他参数

        Returns:
            SkillResult 执行结果
        """
        raise NotImplementedError

    def get_missing_params(self, entities: dict) -> list[SkillParameter]:
        """检查缺失的必要参数"""
        missing = []
        for param in self.parameters:
            if param.required and param.name not in entities:
                missing.append(param)
        return missing

    def format_clarification(self, missing_params: list[SkillParameter]) -> str:
        """生成参数澄清问题"""
        if not missing_params:
            return ""
        param_desc = "、".join(f"「{p.description}」({p.name})" for p in missing_params)
        return f"请提供以下信息：{param_desc}"
