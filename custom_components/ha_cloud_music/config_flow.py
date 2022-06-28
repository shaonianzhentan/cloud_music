from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.storage import STORAGE_DIR

import os
from .manifest import manifest
from .http_api import http_cookie
from homeassistant.util.json import save_json

DOMAIN = manifest.domain

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str
})

class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors = {}
        if user_input is not None:
            url = user_input.get(CONF_URL)
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            login_url = '/login'
            if username.count('@') > 0:
                login_url = login_url + '?email='
            else:
                login_url = login_url + '/cellphone?phone='

            data = await http_cookie(url + login_url + f'{username}&password={password}')
            res_data = data.get('data', {})
            # 登录成功
            if res_data.get('code') == 200:
                print(res_data)
                # 写入cookie
                cookie = data.get('cookie')
                save_json(os.path.abspath(f'{STORAGE_DIR}/cloud_music.cookie'), cookie)
                return self.async_create_entry(title=DOMAIN, data=user_input)
            else:
                errors['base'] = 'login_failed'

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)