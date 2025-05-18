"""Constants for wetter_alarm."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "wetter_alarm"
ATTRIBUTION = "Data provided by wetteralarm.ch"

"""Constant values for wetter_alarm integration."""
ALARM_ID = "alarm_id"
VALID_FROM = "valid_from"
VALID_TO = "valid_to"
PRIORITY = "priority"
REGION = "region"
TITLE = "title"
HINT = "hint"
SIGNATURE = "signature"

CONFIG_POI_NAME = "poi_name"
CONFIG_POI_ID = "poi_id"
CONFIG_POIS = "pois"
CONFIG_DATA_LANGUAGE = "language"
CONFIG_DATA_LANGUAGE_OPTIONS = ["de", "fr", "it", "en"]
