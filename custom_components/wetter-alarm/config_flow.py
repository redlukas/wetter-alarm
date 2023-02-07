from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries

from . import WetterAlarmApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WetterAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    _pois = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            poi_id = user_input.get("poi_id", "")
            client = WetterAlarmApiClient(poi_id)
            valid_poi = await client.validate_poi_id_async(hass=self.hass)
            if valid_poi:
                poi_name = user_input.get("poi_name", "")
                return self.async_create_entry(
                    title="Wetter-Alarm",
                    data={"pois": {(poi_name, poi_id)}},
                )
            else:
                _LOGGER.error("async step_user determined invalid POI")
                errors["base"] = "invalid_connection"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("poi_name"): str,
                    vol.Required("poi_id"): int,
                }
            ),
            errors=errors,
        )
