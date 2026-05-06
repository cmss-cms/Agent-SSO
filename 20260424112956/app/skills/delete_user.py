"""删除用户 Skill"""

from app.skills.base import BaseSkill, SkillParameter, SkillResult


class DeleteUserSkill(BaseSkill):
    """删除用户 Skill"""

    name = "delete_user"
    description = "从系统中删除用户"
    intent = "delete_user"
    parameters = [
        SkillParameter(name="username", description="用户名", required=True),
        SkillParameter(name="reason", description="删除原因", required=False),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        username = entities.get("username", "")
        reason = entities.get("reason", "")

        if not username:
            return SkillResult(
                success=False,
                message="缺少用户名，请提供要删除的用户名。",
            )

        # 模拟删除用户操作
        msg = f"已成功删除用户「{username}」"
        if reason:
            msg += f"，原因：{reason}"
        msg += "。注意：此操作不可恢复。"

        return SkillResult(
            success=True,
            message=msg,
            data={
                "username": username,
                "reason": reason,
                "action": "delete_user",
            },
        )
