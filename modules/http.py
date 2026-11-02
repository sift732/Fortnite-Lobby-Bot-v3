from typing import Any, Optional, Union

import aiohttp


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def close(self) -> None:
        await self.session.close()

    async def request(self, method: str, *args: Any, raw: Optional[bool] = False, **kwargs: Any) -> Union[str, dict]:
        if raw:
            return await self.session.request(method, *args, **kwargs)
        async with self.session.request(method, *args, **kwargs) as response:
            content = await response.text()
            if 'json' in response.headers.get('Content-Type', '').lower():
                try:
                    return await response.json(content_type=None)
                except (ValueError, aiohttp.ContentTypeError):
                    return content
            return content

    async def get(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('GET', *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('POST', *args, **kwargs)
