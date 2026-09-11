from __future__ import annotations
import aiohttp
import logging
from homeassistant.components.tts import TextToSpeechEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_API_URL, CONF_PERSONA

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([KokoroTTSEntity(entry.data[CONF_API_URL], entry.data.get(CONF_PERSONA, "assistant"))])

class KokoroTTSEntity(TextToSpeechEntity):
    _attr_name = "Kokoro TTS"
    _attr_unique_id = "kokoro_tts"
    _attr_supported_options = {"persona", "voice", "speed"}
    _attr_supported_languages = ["ko", "en"]
    _attr_default_language = "ko"
    _attr_default_options = {"persona": "assistant"}

    def __init__(self, api_url: str, persona: str):
        self._api_url = api_url.rstrip("/")
        self._persona = persona

    async def async_get_tts_audio(self, message: str, language: str, options: dict):
        payload = {"text": message, "persona": options.get("persona", self._persona), "save": False}
        if options.get("voice"):
            payload["voice"] = options["voice"]
        if options.get("speed") is not None:
            payload["speed"] = options["speed"]
        try:
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{self._api_url}/tts", json=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Kokoro API returned HTTP %s", response.status)
                        return None, None
                    return "wav", await response.read()
        except (aiohttp.ClientError, TimeoutError) as exc:
            _LOGGER.error("Unable to connect to Kokoro API at %s: %s", self._api_url, exc)
            return None, None
