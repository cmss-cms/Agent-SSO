"""添加资源 Skill"""

from app.skills.base import BaseSkill, SkillParameter, SkillResult


class AddResourceSkill(BaseSkill):
    """添加资源 Skill"""

    name = "add_resource"
    description = "向系统添加新资源"
    intent = "add_resource"
    parameters = [
        SkillParameter(name="resource_type", description="资源类型（服务器/存储/数据库等）", required=True),
        SkillParameter(name="resource_name", description="资源名称", required=True),
        SkillParameter(name="spec", description="资源规格", required=False),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        resource_type = entities.get("资源类型") or entities.get("resource_type", "")
        resource_name = entities.get("资源名") or entities.get("resource_name", "")
        spec = entities.get("spec", "默认规格")

        if not resource_type:
            return SkillResult(
                success=False,
                message="缺少资源类型，请提供要添加的资源类型（如服务器、存储、数据库等）。",
            )

        if not resource_name:
            return SkillResult(
                success=False,
                message=f"缺少资源名称，请提供「{resource_type}」类型的资源名称。",
            )

        return SkillResult(
            success=True,
            message=f"已成功添加{resource_type}资源「{resource_name}」，规格：{spec}。",
            data={
                "resource_type": resource_type,
                "resource_name": resource_name,
                "spec": spec,
                "action": "add_resource",
            },
        )
