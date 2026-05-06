"""添加用户 Skill"""

from app.skills.base import BaseSkill, SkillParameter, SkillResult


class AddUserSkill(BaseSkill):
    """添加用户 Skill

    处理用户添加请求，验证参数并执行添加操作
    """

    name = "add_user"
    description = "添加新用户到系统"
    intent = "add_user"
    parameters = [
        SkillParameter(name="username", description="用户名", required=True),
        SkillParameter(name="email", description="邮箱地址", required=True),
        SkillParameter(name="role", description="用户角色", required=False, default="user"),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        username = entities.get("username", "")
        email = entities.get("email", "")
        role = entities.get("role", "user")

        if not username:
            return SkillResult(
                success=False,
                message="缺少用户名，请提供要添加的用户名。",
            )

        if not email:
            return SkillResult(
                success=False,
                message=f"缺少邮箱地址，请提供用户「{username}」的邮箱。",
            )

        # 模拟添加用户操作
        return SkillResult(
            success=True,
            message=f"已成功添加用户「{username}」，邮箱：{email}，角色：{role}。",
            data={
                "username": username,
                "email": email,
                "role": role,
                "action": "add_user",
            },
        )
