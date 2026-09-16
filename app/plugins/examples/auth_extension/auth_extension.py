from app.plugins.plugin import AuthenticationPlugin


class AuthExtensionPlugin(AuthenticationPlugin):
    async def on_authentication_success(self, user_id, *args, **kwargs):
        self.context.logger.info(f"Auth success for user {user_id}")

    async def on_authentication_failure(self, user_id, *args, **kwargs):
        self.context.logger.info(f"Auth failure for user {user_id}")
