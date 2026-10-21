"""Checks for values that come from the panel (the flows use selectors with the same limits)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import valid_entity_id

from .const import (
    CONF_ALLOW_OPEN,
    CONF_ARM_COVER,
    CONF_ARM_COVER_POSITION,
    CONF_AUTO_BYPASS,
    CONF_CAMERA_PRESET,
    CONF_DETECT_SWITCHES,
    CONF_ENTITY,
    CONF_GARAGE_DELAY,
    CONF_GARAGE_MOTION,
    CONF_GARAGE_NETWORKS,
    CONF_GARAGE_PANEL,
    CONF_GARAGE_TTS,
    CONF_GARAGE_TTS_REPEAT,
    CONF_GARAGE_TTS_TEXT,
    CONF_KIDS_RESET_TIME,
    CONF_LANGUAGE,
    CONF_NIGHT_OFF_DAYS,
    CONF_NIGHT_OFF_TIME,
    CONF_ONLY_UNAVAILABLE,
    CONF_PERSON_COUNT,
    CONF_PERSON_IMAGE,
    CONF_PERSON_PUSH,
    CONF_PERSON_SENSOR,
    CONF_PERSON_WIFI,
    CONF_PRESENCE_MODE,
    CONF_PRIVACY,
    CONF_PRIVACY_DELAY,
    CONF_PTZ,
    CONF_PTZ_HOME,
    CONF_RECORD_SWITCHES,
    CONF_TYPE,
    CONF_UNKNOWN_PRESENCE,
    CONF_USE_ENTRY,
    CONF_USE_EXIT,
    DEFAULTS,
    LANGUAGE_OPTIONS,
    OPTIONAL_TEXT_KEYS,
    RANGES,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_PERSON,
    SUBENTRY_SENSOR,
)
from .logic.auto_arm import PRESENCE_MODES, UNKNOWN_PRESENCE
from .logic.misc import WEEKDAYS
from .logic.state_machine import SENSOR_TYPES

ENTITY = "entity"
ENTITIES = "entities"
TEXT = "text"
LIST = "list"
BOOL = "bool"
NUMBER = "number"

CHOICES: dict[str, list[str]] = {
    CONF_LANGUAGE: LANGUAGE_OPTIONS,
    CONF_PRESENCE_MODE: PRESENCE_MODES,
    CONF_TYPE: SENSOR_TYPES,
    CONF_UNKNOWN_PRESENCE: UNKNOWN_PRESENCE,
}
MULTI_CHOICES: dict[str, list[str]] = {CONF_NIGHT_OFF_DAYS: WEEKDAYS}
TIME_KEYS = (CONF_KIDS_RESET_TIME, CONF_NIGHT_OFF_TIME)
TIME_RE = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d(:[0-5]\d)?$")

# Fields of the sub items and their kind (required fields are checked separately).
SUBENTRY_FIELDS: dict[str, dict[str, str]] = {
    SUBENTRY_SENSOR: {
        CONF_ENTITY: ENTITY,
        CONF_TYPE: TEXT,
        CONF_USE_ENTRY: BOOL,
        CONF_USE_EXIT: BOOL,
        CONF_AUTO_BYPASS: BOOL,
        CONF_ALLOW_OPEN: BOOL,
        CONF_ONLY_UNAVAILABLE: ENTITY,
        CONF_ARM_COVER: ENTITY,
        CONF_ARM_COVER_POSITION: NUMBER,
        CONF_CAMERA_PRESET: TEXT,
    },
    SUBENTRY_PERSON: {CONF_PERSON_WIFI: ENTITY},
    SUBENTRY_CAMERA: {
        CONF_PRIVACY: ENTITY,
        CONF_PTZ: ENTITY,
        CONF_PTZ_HOME: TEXT,
        CONF_PRIVACY_DELAY: NUMBER,
        CONF_RECORD_SWITCHES: ENTITIES,
        CONF_DETECT_SWITCHES: ENTITIES,
        CONF_PERSON_SENSOR: ENTITY,
        CONF_PERSON_COUNT: ENTITY,
        CONF_PERSON_IMAGE: ENTITY,
        CONF_PERSON_PUSH: BOOL,
    },
    SUBENTRY_GARAGE: {
        CONF_GARAGE_PANEL: ENTITY,
        CONF_GARAGE_NETWORKS: LIST,
        CONF_GARAGE_DELAY: NUMBER,
        CONF_GARAGE_MOTION: ENTITIES,
        CONF_GARAGE_TTS: LIST,
        CONF_GARAGE_TTS_TEXT: TEXT,
        CONF_GARAGE_TTS_REPEAT: NUMBER,
    },
}


class FieldError(ValueError):
    """A value is not valid; the panel shows ``field`` with the text for ``code``."""

    def __init__(self, field: str, code: str) -> None:
        super().__init__(f"{field}:{code}")
        self.field = field
        self.code = code


def _number(key: str, value: Any, integer: bool) -> int | float:
    if isinstance(value, bool):
        raise FieldError(key, "not_a_number")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise FieldError(key, "not_a_number") from None
    if key in RANGES:
        minimum, maximum, _step, _unit = RANGES[key]
        if not minimum <= number <= maximum:
            raise FieldError(key, "out_of_range")
    return int(number) if integer and number.is_integer() else number


def _string_list(key: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise FieldError(key, "not_a_list")
    return [str(v).strip() for v in value if str(v).strip()]


def _entity(key: str, value: Any) -> str:
    entity_id = str(value).strip()
    if not valid_entity_id(entity_id):
        raise FieldError(key, "invalid_entity")
    return entity_id


def _bool(key: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise FieldError(key, "not_bool")
    return value


def _choice(key: str, value: str) -> str:
    if key in CHOICES and value not in CHOICES[key]:
        raise FieldError(key, "invalid_choice")
    if key in TIME_KEYS and not TIME_RE.match(value):
        raise FieldError(key, "invalid_time")
    return value


def coerce_option(key: str, value: Any) -> Any:
    """Bring an option from the panel into its type (None: cleared)."""
    if key not in DEFAULTS and key not in OPTIONAL_TEXT_KEYS:
        raise FieldError(key, "unknown_option")
    if value is None or value == "":
        return None
    default = DEFAULTS.get(key)
    if isinstance(default, bool):
        return _bool(key, value)
    if isinstance(default, int | float):
        return _number(key, value, isinstance(default, int))
    if isinstance(default, list):
        values = _string_list(key, value)
        if key in MULTI_CHOICES and any(v not in MULTI_CHOICES[key] for v in values):
            raise FieldError(key, "invalid_choice")
        return values
    return _choice(key, str(value).strip())


def validate_subentry(subentry_type: str, data: Mapping[str, Any]) -> dict[str, Any]:
    """Checked and typed data of a sub item from the panel."""
    fields = SUBENTRY_FIELDS.get(subentry_type)
    if fields is None:
        raise FieldError("type", "unknown_type")
    result: dict[str, Any] = {}
    for key, value in data.items():
        kind = fields.get(key)
        if kind is None:
            raise FieldError(key, "unknown_option")
        if value is None or value in ("", []):
            continue
        if kind == ENTITY:
            result[key] = _entity(key, value)
        elif kind == ENTITIES:
            result[key] = [_entity(key, v) for v in _string_list(key, value)]
        elif kind == LIST:
            result[key] = _string_list(key, value)
        elif kind == BOOL:
            result[key] = _bool(key, value)
        elif kind == NUMBER:
            result[key] = _number(key, value, True)
        else:
            result[key] = _choice(key, str(value).strip())
    return result


def duplicate_sensor(entry: ConfigEntry, entity_id: str, own_id: str | None = None) -> str | None:
    """Title of another sensor sub item with the same entity (None: no duplicate)."""
    for sub_id, sub in entry.subentries.items():
        if (
            sub.subentry_type == SUBENTRY_SENSOR
            and sub_id != own_id
            and sub.data.get(CONF_ENTITY) == entity_id
        ):
            return sub.title
    return None
