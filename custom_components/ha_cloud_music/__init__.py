from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import PLATFORMS
from .manifest import manifest
from .cloud_music import CloudMusic
from .http import HttpView

DOMAIN = manifest.domain

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN] = CloudMusic(hass)    
    hass.http.register_view(HttpView)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass, entry):
    config = entry.options

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)