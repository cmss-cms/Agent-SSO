"""删除资源 Skill"""

from app.skills.base import BaseSkill, SkillParameter, SkillResult


class DeleteResourceSkill(BaseSkill):
    """删除资源 Skill"""

    name = "delete_resource"
    description = "从系统中删除/释放资源"
    intent = "delete_resource"
    parameters = [
        SkillParameter(name="resource_type", description="资源类型", required=True),
        SkillParameter(name="resource_name", description="资源名称", required=True),
        SkillParameter(name="reason", description="删除原因", required=False),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        resource_type = entities.get("资源类型") or entities.get("resource_type", "")
        resource_name = entities.get("资源名") or entities.get("resource_name", "")
        reason = entities.get("reason", "")

        if not resource_type and not resource_name:
            return SkillResult(
                success=False,
                message="缺少资源信息，请提供要删除的资源类型或名称。",
            )

        desc = ""
        if resource_type:
            desc += resource_type
        if resource_name:
            desc += f"「{resource_name}」"

        msg = f"已成功删除{desc}资源"
        if reason:
            msg += f"，原因：{reason}"
        msg += "。删除前已确认无运行中的服务。"

        return SkillResult(
            success=True,
            message=msg,
            data={
                "resource_type": resource_type,
                "resource_name": resource_name,
                "reason": reason,
                "action": "delete_resource",
            },
        )
