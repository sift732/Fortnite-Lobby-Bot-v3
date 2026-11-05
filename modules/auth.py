from typing import Any, Optional

import rebootpy
from rebootpy.errors import AuthException


class MyAdvancedAuth(rebootpy.AdvancedAuth):
    def __init__(
        self,
        device_id: Optional[str] = None,
        account_id: Optional[str] = None,
        secret: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            device_id=device_id,
            account_id=account_id,
            secret=secret,
            prompt_device_code=True,
            open_link_in_browser=False,
            **kwargs
        )

    @property
    def identifier(self) -> Optional[str]:
        return self.account_id

    async def ios_authenticate(self) -> dict:
        data = None
        used_existing_device_auth = False

        if self.device_auth_ready():
            try:
                data = await self.run_device_authenticate()
                used_existing_device_auth = True

            except AuthException as error:
                original = getattr(error, "original", None)

                if (
                    getattr(original, "message_code", None)
                    != "errors.com.epicgames.account.invalid_account_credentials"
                ):
                    raise

                data = None

        if data is None:
            data = await self.run_device_code_authenticate()

        if "access_token" not in data:
            exchange_code = (
                data.get("code")
                or data.get("exchange_code")
            )

            if exchange_code:
                data = await self.exchange_code_for_session(
                    self.ios_token,
                    exchange_code
                )

        if "access_token" not in data:
            raise AuthException(
                "Failed to retrieve an access_token from Epic Games."
            )

        self._update_ios_data(data)

        if not used_existing_device_auth:
            details = await self.generate_device_auth()

            self.client.dispatch_event(
                "device_auth_generate",
                details
            )

        return data
