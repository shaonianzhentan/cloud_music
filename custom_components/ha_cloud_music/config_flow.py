from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.storage import STORAGE_DIR
from urllib.parse import quote
from homeassistant.core import callback

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
            url = user_input.get(CONF_URL).strip('/')
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            login_url = '/login'
            if username.count('@') > 0:
                login_url = login_url + '?email='
            else:
                login_url = login_url + '/cellphone?phone='

            data = await http_cookie(url + login_url + f'{quote(username)}&password={quote(password)}')
            res_data = data.get('data', {})
            # 登录成功
            if res_data.get('code') == 200:
                # 写入cookie
                cookie = data.get('cookie')
                save_json(os.path.abspath(f'{STORAGE_DIR}/cloud_music.cookie'), cookie)
                user_input['uid'] = res_data['account']['id']
                user_input[CONF_URL] = url
                return self.async_create_entry(title=DOMAIN, data=user_input)
            else:
                errors['base'] = 'login_failed'

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
        
    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        return OptionsFlowHandler(entry)


class OptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is None:
            options = self.config_entry.options
            errors = {}
            DATA_SCHEMA = vol.Schema({
                vol.Required("mpd_host", default=options.get("mpd_host", "localhost")): str,
                vol.Required("mpd_port", default=options.get("mpd_port", 6600)): int,
                vol.Optional("mpd_password", default=options.get("mpd_password", "")): str
            })
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
        return self.async_create_entry(title='', data=user_input)