from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_URL

from .manifest import manifest
from .cloud_music import CloudMusic

DOMAIN = manifest.domain

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): str
})

class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)


        self.hass.data[DOMAIN] = CloudMusic(self.hass, user_input.get(CONF_URL))
        return self.async_create_entry(title=DOMAIN, data=user_input)