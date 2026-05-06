"""Skill 注册表"""

from app.skills.base import BaseSkill


class SkillRegistry:
    """Skill 注册表 - 管理所有可用的 Skill"""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill):
        """注册一个 Skill"""
        self._skills[skill.intent] = skill

    def get_by_intent(self, intent: str) -> BaseSkill | None:
        """根据意图获取 Skill"""
        return self._skills.get(intent)

    def list_skills(self) -> list[dict]:
        """列出所有已注册的 Skill"""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "intent": skill.intent,
                "parameters": [
                    {"name": p.name, "description": p.description, "required": p.required}
                    for p in skill.parameters
                ],
            }
            for skill in self._skills.values()
        ]

    @property
    def supported_intents(self) -> list[str]:
        """返回所有支持的意图"""
        return list(self._skills.keys())


# 全局注册表
registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    """获取全局 Skill 注册表"""
    return registry
