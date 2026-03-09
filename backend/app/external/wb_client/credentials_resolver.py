from dataclasses import dataclass

from backend.app.core.config import Settings
from backend.app.external.wb_client.models import Credentials


@dataclass
class WbCredentialsResolver:
    settings: Settings

    def resolve(self, username: str, token: str) -> Credentials:
        authorization = self.settings.wb_authorization_template.replace("{token}", token)
        return Credentials(
            username=username,
            authorization=authorization,
            client_secret=self.settings.wb_client_secret,
            user_agent=self.settings.wb_user_agent,
        )
