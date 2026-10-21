"""Diagnostics."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CALL_ADDON,
    CONF_CALL_TARGETS,
    CONF_CODE,
    CONF_GARAGE_NETWORKS,
    CONF_HOME_NETWORKS,
    CONF_NIGHT_TAG,
)
from .engine import AlarmConfigEntry

# Code hash, phone numbers, network names and the tag id are often shared in
# public issues together with the diagnostics. Titles of sub items are names of
# persons and rooms.
TO_REDACT = {
    CONF_CODE,
    CONF_CALL_TARGETS,
    CONF_CALL_ADDON,
    CONF_HOME_NETWORKS,
    CONF_GARAGE_NETWORKS,
    CONF_NIGHT_TAG,
    "title",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AlarmConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry (private values redacted)."""
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "state": entry.runtime_data.diagnostics(),
    }
