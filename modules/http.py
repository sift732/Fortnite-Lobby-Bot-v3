import json
from typing import Any, Optional, Union

import aiohttp


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def close(self) -> None:
        await self.session.close()

    async def request(self, method: str, *args: Any, raw: Optional[bool] = False, **kwargs: Any) -> Union[str, dict, aiohttp.ClientResponse]:
        response = await self.session.request(method, *args, **kwargs)
        if raw:
            return response
        try:
            text = await response.text()
            try:
                return json.loads(text)
            except (ValueError, TypeError):
                return text
        finally:
            response.release()

    async def get(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('GET', *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('POST', *args, **kwargs)
