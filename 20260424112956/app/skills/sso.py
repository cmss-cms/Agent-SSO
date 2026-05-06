"""单点登录（SSO）Skill"""

from app.skills.base import BaseSkill, SkillParameter, SkillResult


class SSOSkill(BaseSkill):
    """SSO 单点登录 Skill

    处理 SSO 配置、查询和故障排查
    """

    name = "sso"
    description = "单点登录（SSO）配置与管理"
    intent = "sso"
    parameters = [
        SkillParameter(name="action", description="操作类型（配置/查询/排查）", required=False, default="查询"),
        SkillParameter(name="protocol", description="SSO协议（SAML/OAuth/OIDC）", required=False),
    ]

    async def execute(self, entities: dict, **kwargs) -> SkillResult:
        action = entities.get("action", "查询")
        protocol = entities.get("protocol", "")

        if action == "配置":
            proto = protocol or "未指定"
            return SkillResult(
                success=True,
                message=(
                    f"SSO 配置指引（协议：{proto}）：\n"
                    "1. 进入「系统设置」→「认证配置」\n"
                    "2. 选择 SSO 协议（SAML 2.0 / OAuth 2.0 / OIDC）\n"
                    "3. 填写 Identity Provider 元数据\n"
                    "4. 配置回调 URL\n"
                    "5. 映射用户属性\n"
                    "6. 测试连接\n"
                    "7. 启用 SSO\n"
                    "是否需要我帮你开始配置？"
                ),
                data={"action": "configure", "protocol": protocol},
            )
        elif action == "排查":
            return SkillResult(
                success=True,
                message=(
                    "SSO 常见问题排查：\n"
                    "1. 检查 IdP 元数据是否正确\n"
                    "2. 确认回调 URL 配置一致\n"
                    "3. 检查时钟同步（SAML 对时间敏感）\n"
                    "4. 验证证书有效期\n"
                    "5. 查看审计日志获取详细错误\n"
                    "请告诉我具体遇到的问题，我可以提供更针对性的帮助。"
                ),
                data={"action": "troubleshoot"},
            )
        else:
            return SkillResult(
                success=True,
                message=(
                    "关于单点登录（SSO）：\n\n"
                    "SSO 允许用户一次登录即可访问所有互信系统。\n\n"
                    "支持的协议：\n"
                    "• SAML 2.0 - 企业级身份联合\n"
                    "• OAuth 2.0 - 授权框架\n"
                    "• OIDC - 基于 OAuth 的身份层\n\n"
                    "我可以帮你：\n"
                    "1. 配置 SSO 接入\n"
                    "2. 排查 SSO 问题\n"
                    "3. 了解 SSO 最佳实践\n\n"
                    "你需要哪方面的帮助？"
                ),
                data={"action": "info"},
            )
