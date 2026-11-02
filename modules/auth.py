import asyncio
import json
import os
import tempfile
import threading
from pathlib import Path

import rebootpy


AUTH_PATH = Path('data/device_auth.json')
_AUTH_LOCK = threading.RLock()
_INPUT_LOCK = asyncio.Lock()


def get_device_auth_details(path=AUTH_PATH):
    path = Path(path)
    if not path.is_file():
        return {}
    with path.open('r', encoding='utf-8') as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError('Invalid device auth data')
    return data


def get_device_auth(client_id, path=AUTH_PATH):
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError('client_id is required')
    return get_device_auth_details(path).get(client_id, {})


def store_device_auth_details(client_id, details, path=AUTH_PATH):
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError('client_id is required')
    if not isinstance(details, dict):
        raise TypeError('details must be a dictionary')
    account_id = details.get('account_id') or details.get('accountId')
    device_id = details.get('device_id') or details.get('deviceId')
    secret = details.get('secret')
    if not all(isinstance(value, str) and value for value in (account_id, device_id, secret)):
        raise ValueError('Incomplete device auth data')
    value = {'account_id': account_id, 'device_id': device_id, 'secret': secret}
    path = Path(path)
    with _AUTH_LOCK:
        existing = get_device_auth_details(path)
        existing[client_id] = value
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.device_auths_', suffix='.tmp', dir=path.parent)
        try:
            if os.name != 'nt':
                os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as file:
                json.dump(existing, file, indent=4, ensure_ascii=False)
                file.write('\n')
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return value


class MyAdvancedAuth(rebootpy.AdvancedAuth):
    def __init__(self, client_id, auth_method='device_code', auth_path=AUTH_PATH, **kwargs):
        if auth_method not in ('device_code', 'authorization_code'):
            raise ValueError('Unsupported auth_method')
        self.client_id = client_id
        self.auth_method = auth_method
        self.auth_path = Path(auth_path)
        saved = get_device_auth(client_id, self.auth_path)
        kwargs.pop('device_id', None)
        kwargs.pop('account_id', None)
        kwargs.pop('secret', None)
        kwargs.pop('prompt_device_code', None)
        kwargs.pop('prompt_authorization_code', None)
        kwargs.pop('prompt_exchange_code', None)
        kwargs.pop('open_link_in_browser', None)
        super().__init__(
            device_id=saved.get('device_id') or saved.get('deviceId'),
            account_id=saved.get('account_id') or saved.get('accountId'),
            secret=saved.get('secret'),
            prompt_device_code=auth_method == 'device_code',
            prompt_authorization_code=auth_method == 'authorization_code',
            prompt_exchange_code=False,
            open_link_in_browser=auth_method == 'device_code',
            **kwargs
        )

    async def ios_authenticate(self, priority=0):
        if self.device_auth_ready():
            try:
                return await self.run_device_authenticate(priority=priority)
            except rebootpy.AuthException as error:
                original = getattr(error, 'original', None)
                if not isinstance(original, rebootpy.HTTPException):
                    raise
                if original.message_code != 'errors.com.epicgames.account.invalid_account_credentials':
                    raise

        if self.auth_method == 'device_code':
            data = await self.run_device_code_authenticate()
        else:
            from aioconsole import ainput
            async with _INPUT_LOCK:
                code = (await ainput('Authorization Code: ')).strip()
            if not code:
                raise ValueError('Authorization Code is empty')
            self.authorization_code = code
            data = await self.run_authorization_code_authenticate()

        self._update_ios_data(data)
        generated = await self.generate_device_auth()
        details = store_device_auth_details(self.client_id, generated, self.auth_path)
        self.device_id = details['device_id']
        self.account_id = details['account_id']
        self.secret = details['secret']
        self.client.dispatch_event('device_auth_generate', details.copy())
        return data
