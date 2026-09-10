from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from .const import DOMAIN, CONF_API_URL, CONF_PERSONA, DEFAULT_API_URL, DEFAULT_PERSONA

class KokoroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Kokoro TTS", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
            vol.Optional(CONF_PERSONA, default=DEFAULT_PERSONA): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
