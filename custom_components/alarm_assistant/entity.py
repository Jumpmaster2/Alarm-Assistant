"""Base entity."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .engine import AlarmEngine


def global_device_info(entry_id: str) -> DeviceInfo:
    """Device of the integration as a whole."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=NAME,
        manufacturer=NAME,
        model="Alarm panel",
        entry_type=DeviceEntryType.SERVICE,
    )


class AlarmEntity(CoordinatorEntity[AlarmEngine]):
    """Entity of the integration."""

    _attr_has_entity_name = True

    def __init__(self, engine: AlarmEngine, key: str) -> None:
        super().__init__(engine)
        entry_id = engine.config_entry.entry_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = global_device_info(entry_id)
