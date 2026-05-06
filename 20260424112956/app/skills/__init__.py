"""Skills 模块 - 自动注册所有 Skill"""

from app.skills.registry import registry
from app.skills.add_user import AddUserSkill
from app.skills.delete_user import DeleteUserSkill
from app.skills.add_resource import AddResourceSkill
from app.skills.delete_resource import DeleteResourceSkill
from app.skills.sso import SSOSkill


def register_all_skills():
    """注册所有内置 Skill"""
    registry.register(AddUserSkill())
    registry.register(DeleteUserSkill())
    registry.register(AddResourceSkill())
    registry.register(DeleteResourceSkill())
    registry.register(SSOSkill())


# 模块导入时自动注册
register_all_skills()
